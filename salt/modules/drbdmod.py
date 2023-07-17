# -*- coding: utf-8 -*-
'''
Module to provide DRBD functionality to Salt

.. versionadded:: pending

:maintainer:    Nick Wang <nwang@suse.com>
:maturity:      alpha
:depends:       ``drbdadm`` drbd utils
:platform:      all

:configuration: This module requires drbd kernel module and drbd utils tool

.. code-block:: yaml

'''
from __future__ import absolute_import, print_function, unicode_literals

import logging

from salt.exceptions import CommandExecutionError
from salt.ext import six

import salt.utils.json
import salt.utils.path

LOGGER = logging.getLogger(__name__)

# Define the module's virtual name
__virtualname__ = 'drbd'

DRBD_COMMAND = 'drbdadm'
ERR_STR = 'UNKNOWN'
DUMMY_STR = 'IGNORED'
WITH_JSON = True
DRBDADM = 'drbd-utils'
# drbd-utils >= 9.0.0 for json status
DRBDADM_JSON_VERSION = '9.0.0'


def __virtual__():  # pragma: no cover
    '''
    Only load this module if drbdadm(drbd-utils) is installed
    '''
    if bool(salt.utils.path.which(DRBD_COMMAND)):
        __salt__['drbd.json'] = WITH_JSON

        version = __salt__['pkg.version'](DRBDADM)
        json_support = __salt__['pkg.version_cmp'](version,
            DRBDADM_JSON_VERSION) >= 0
        if not json_support:
            __salt__['drbd.json'] = False

        return __virtualname__
    return (
        False,
        'The drbd execution module failed to load: the drbdadm'
        ' binary is not available.')


def _analyse_overview_field(content):
    '''
    Split the field in drbd-overview
    '''
    if "(" in content:
        # Output like "Connected(2*)" or "UpToDate(2*)"
        return content.split("(")[0], content.split("(")[0]
    elif "/" in content:
        # Output like "Primar/Second" or "UpToDa/UpToDa"
        return content.split("/")[0], content.split("/")[1]

    return content, ""


def _count_spaces_startswith(line):
    '''
    Count the number of spaces before the first character
    '''
    if line.split('#')[0].strip() == "":
        return None

    spaces = 0
    for i in line:
        if i.isspace():
            spaces += 1
        else:
            return spaces


def _analyse_status_type(line):
    '''
    Figure out the sections in drbdadm status
    '''
    spaces = _count_spaces_startswith(line)

    if spaces is None:
        return ''

    switch = {
        0: 'RESOURCE',
        2: {' disk:': 'LOCALDISK', ' role:': 'PEERNODE', ' connection:': 'PEERNODE'},
        4: {' peer-disk:': 'PEERDISK'},
        6: DUMMY_STR,
        8: DUMMY_STR,
    }

    ret = switch.get(spaces, ERR_STR)

    # isinstance(ret, str) only works when run directly, calling need unicode(six)
    if isinstance(ret, six.text_type):
        return ret

    for x in ret:
        if x in line:
            return ret[x]

    # Doesn't find expected KEY in support indent
    return ERR_STR


def _add_res(line):
    '''
    Analyse the line of local resource of ``drbdadm status``
    '''
    fields = line.strip().split()

    if __context__['drbd.resource']:
        __context__['drbd.statusret'].append(__context__['drbd.resource'])
        __context__['drbd.resource'] = {}

    resource = {}
    resource["resource name"] = fields[0]
    resource["local role"] = fields[1].split(":")[1]
    resource["local volumes"] = []
    resource["peer nodes"] = []

    __context__['drbd.resource'] = resource


def _add_volume(line):
    '''
    Analyse the line of volumes of ``drbdadm status``
    '''
    section = _analyse_status_type(line)
    fields = line.strip().split()

    volume = {}
    for field in fields:
        volume[field.split(':')[0]] = field.split(':')[1]

    if section == 'LOCALDISK':
        if 'drbd.resource' not in __context__:  # pragma: no cover
            # Should always be called after _add_res
            __context__['drbd.resource'] = {}
            __context__['drbd.resource']['local volumes'] = []

        __context__['drbd.resource']['local volumes'].append(volume)
    else:
        # 'PEERDISK'
        if 'drbd.lastpnodevolumes' not in __context__:  # pragma: no cover
            # Insurance refer to:
            # https://docs.saltstack.com/en/latest/topics/development/modules/developing.html#context
            # Should always be called after _add_peernode
            __context__['drbd.lastpnodevolumes'] = []

        __context__['drbd.lastpnodevolumes'].append(volume)


def _add_peernode(line):
    '''
    Analyse the line of peer nodes of ``drbdadm status``
    '''
    fields = line.strip().split()

    peernode = {}
    peernode["peernode name"] = fields[0]
    # Could be role or connection:
    peernode[fields[1].split(":")[0]] = fields[1].split(":")[1]
    peernode["peer volumes"] = []

    if 'drbd.resource' not in __context__:  # pragma: no cover
        # Should always be called after _add_res
        __context__['drbd.resource'] = {}
        __context__['drbd.resource']['peer nodes'] = []

    __context__['drbd.resource']["peer nodes"].append(peernode)

    __context__['drbd.lastpnodevolumes'] = peernode["peer volumes"]


def _empty(dummy):
    '''
    Action of empty line or extra verbose info of ``drbdadm status``
    '''


def _unknown_parser(line):
    '''
    Action of unsupported line of ``drbdadm status``
    '''
    raise CommandExecutionError('The unknown line:\n' + line)


def _line_parser(line):
    '''
    Call action for different lines
    '''
    # Should always be called via status()
    section = _analyse_status_type(line)

    switch = {
        '': _empty,
        'RESOURCE': _add_res,
        'PEERNODE': _add_peernode,
        'LOCALDISK': _add_volume,
        'PEERDISK': _add_volume,
        DUMMY_STR: _empty,
        ERR_STR: _unknown_parser,
    }

    func = switch.get(section, _unknown_parser)

    func(line)


def _is_local_all_uptodated(res, output):
    '''
    Check whether all local volumes of given resource are UpToDate.
    '''

    for vol in res[output["volume"]]:
        if vol[output["state"]] != 'UpToDate':
            return False

    return True


def _is_peers_uptodated(res, output, peernode='all'):
    '''
    Check whether all volumes of peer node of given resource are UpToDate.

    .. note::

        If peernode is not match, will return None, same as False.
    '''
    ret = False

    for node in res[output["connection"]]:
        if peernode != 'all' and node[output["peer_node"]] != peernode:
            continue

        for vol in node[output["peer_node_vol"]]:
            if vol[output["peer_node_state"]] != 'UpToDate':
                return False
            else:
                # At lease one volume is 'UpToDate'
                ret = True

    return ret


def _is_no_backing_dev_request(res, output):
    '''
    Check whether all volumes have no unfinished backing device request.
    Only working when json status supported.

    Metadata still need to sync to disk after state changed.
    Only reply to sync target to change when I/O request finished,
    which is unpredictable. Local reference count is not 0 before endio.

    '''
    if not __salt__['drbd.json']:
        return True

    # Since name is not all, res only have one element
    for vol in res[output["volume"]]:
        if int(vol[output["local_cnt"]]) != 0:
            return False

    return True


def _get_json_output_save(command):
    '''
    A wrapper of get json command to acommandate json output issues
    '''

    error_str = '"estimated-seconds-to-finish": nan,'
    replace_str = '"estimated-seconds-to-finish": 987654321,'
    results = __salt__['cmd.run_all'](command)

    if 'retcode' not in results or results['retcode'] != 0:
        LOGGER.info("Error running command \"%s\".  Error message: %s (%s)",
                     command, results['stderr'], results['retcode'])
        return None

    # https://github.com/LINBIT/drbd-utils/commit/104293030b2c0106b4791edb3eec38b476652a2e
    # results['stdout'] is unicode
    s_result = str(results['stdout'])
    if error_str in s_result:
        s_result = s_result.replace(error_str, replace_str)
        results['stdout'] = six.text_type(s_result)

    try:
        ret = salt.utils.json.loads(results['stdout'], strict=False)

    except ValueError:
        raise CommandExecutionError('Error trying to load the json output',
                                    info=results)

    return ret


def overview():
    '''
    Show status of the DRBD devices, support two nodes only.
    drbd-overview is removed since drbd-utils-9.6.0,
    use status instead.

    CLI Example:

    .. code-block:: bash

        salt '*' drbd.overview
    '''
    cmd = 'drbd-overview'
    for line in __salt__['cmd.run'](cmd).splitlines():
        ret = {}
        fields = line.strip().split()
        minnum = fields[0].split(':')[0]
        device = fields[0].split(':')[1]
        connstate, _ = _analyse_overview_field(fields[1])
        localrole, partnerrole = _analyse_overview_field(fields[2])
        localdiskstate, partnerdiskstate = _analyse_overview_field(fields[3])
        if localdiskstate.startswith("UpTo"):
            if partnerdiskstate.startswith("UpTo"):
                if len(fields) >= 5:
                    mountpoint = fields[4]
                    fs_mounted = fields[5]
                    totalsize = fields[6]
                    usedsize = fields[7]
                    remainsize = fields[8]
                    perc = fields[9]
                    ret = {
                        'minor number': minnum,
                        'device': device,
                        'connection state': connstate,
                        'local role': localrole,
                        'partner role': partnerrole,
                        'local disk state': localdiskstate,
                        'partner disk state': partnerdiskstate,
                        'mountpoint': mountpoint,
                        'fs': fs_mounted,
                        'total size': totalsize,
                        'used': usedsize,
                        'remains': remainsize,
                        'percent': perc,
                    }
                else:
                    ret = {
                        'minor number': minnum,
                        'device': device,
                        'connection state': connstate,
                        'local role': localrole,
                        'partner role': partnerrole,
                        'local disk state': localdiskstate,
                        'partner disk state': partnerdiskstate,
                    }
            else:
                syncbar = fields[4]
                synced = fields[6]
                syncedbytes = fields[7]
                sync = synced+syncedbytes
                ret = {
                    'minor number': minnum,
                    'device': device,
                    'connection state': connstate,
                    'local role': localrole,
                    'partner role': partnerrole,
                    'local disk state': localdiskstate,
                    'partner disk state': partnerdiskstate,
                    'synchronisation: ': syncbar,
                    'synched': sync,
                }
    return ret


def status(name='all'):
    '''
    Using drbdadm to show status of the DRBD devices,
    available in the latest DRBD9.
    Support multiple nodes, multiple volumes.

    :type name: str
    :param name:
        Resource name.

    :return: DRBD status of resource.
    :rtype: list(dict(res))

    CLI Example:

    .. code-block:: bash

        salt '*' drbd.status
        salt '*' drbd.status name=<resource name>
    '''

    # Initialize for multiple times test cases
    __context__['drbd.statusret'] = []
    __context__['drbd.resource'] = {}

    cmd = 'drbdadm status {}'.format(name)

    # One possible output: (number of resource/node/vol are flexible)
    # resource role:Secondary
    #   volume:0 disk:Inconsistent
    #   volume:1 disk:Inconsistent
    #   drbd-node1 role:Primary
    #     volume:0 replication:SyncTarget peer-disk:UpToDate done:10.17
    #     volume:1 replication:SyncTarget peer-disk:UpToDate done:74.08
    #   drbd-node2 role:Secondary
    #     volume:0 peer-disk:Inconsistent resync-suspended:peer
    #     volume:1 peer-disk:Inconsistent resync-suspended:peer

    result = __salt__['cmd.run_all'](cmd)
    if result['retcode'] != 0:
        LOGGER.info('No status due to %s (%s).', result['stderr'], result['retcode'])
        return None

    try:
        for line in result['stdout'].splitlines():
            _line_parser(line)
    except CommandExecutionError as err:
        raise CommandExecutionError('UNKNOWN status output format found',
                                    info=(result['stdout'] + "\n\n" +
                                    six.text_type(err)))

    if __context__['drbd.resource']:
        __context__['drbd.statusret'].append(__context__['drbd.resource'])

    return __context__['drbd.statusret']


def createmd(name='all', force=True):
    '''
    Create the metadata of DRBD resource.

    :type name: str
    :param name:
        Resource name.

    :type force: bool
    :param force:
        Force create metadata.

    :return: result of creating metadata.
    :rtype: bool

    CLI Example:

    .. code-block:: bash

        salt '*' drbd.create
        salt '*' drbd.create name=<resource name>
    '''

    cmd = 'drbdadm create-md {}'.format(name)

    if force:
        cmd += ' --force'

    return __salt__['cmd.retcode'](cmd)


def up(name='all'):
    '''
    Start of drbd resource.

    :type name: str
    :param name:
        Resource name.

    :return: result of start resource.
    :rtype: bool

    CLI Example:

    .. code-block:: bash

        salt '*' drbd.up
        salt '*' drbd.up name=<resource name>
    '''

    cmd = 'drbdadm up {}'.format(name)

    return __salt__['cmd.retcode'](cmd)


def down(name='all'):
    '''
    Stop of DRBD resource.

    :type name: str
    :param name:
        Resource name.

    :return: result of stop resource.
    :rtype: bool

    CLI Example:

    .. code-block:: bash

        salt '*' drbd.down
        salt '*' drbd.down name=<resource name>
    '''

    cmd = 'drbdadm down {}'.format(name)

    return __salt__['cmd.retcode'](cmd)


def primary(name='all', force=False):
    '''
    Promote the DRBD resource.

    :type name: str
    :param name:
        Resource name.

    :type force: bool
    :param force:
        Force to promote the resource.
        Needed in the initial sync.

    :return: result of promote resource.
    :rtype: bool

    CLI Example:

    .. code-block:: bash

        salt '*' drbd.primary
        salt '*' drbd.primary name=<resource name>
    '''

    cmd = 'drbdadm primary {}'.format(name)

    if force:
        cmd += ' --force'

    return __salt__['cmd.retcode'](cmd)


def secondary(name='all'):
    '''
    Demote the DRBD resource.

    :type name: str
    :param name:
        Resource name.

    :return: result of demote resource.
    :rtype: bool

    CLI Example:

    .. code-block:: bash

        salt '*' drbd.secondary
        salt '*' drbd.secondary name=<resource name>
    '''

    cmd = 'drbdadm secondary {}'.format(name)

    return __salt__['cmd.retcode'](cmd)


def adjust(name='all'):
    '''
    Adjust the DRBD resource while running.

    :type name: str
    :param name:
        Resource name.

    :return: result of adjust resource.
    :rtype: bool

    CLI Example:

    .. code-block:: bash

        salt '*' drbd.adjust
        salt '*' drbd.adjust name=<resource name>
    '''

    cmd = 'drbdadm adjust {}'.format(name)

    return __salt__['cmd.retcode'](cmd)


def setup_show(name='all'):
    '''
    Show the DRBD resource via drbdsetup directly.
    Only support the json format so far.

    :type name: str
    :param name:
        Resource name.

    :return: The resource configuration.
    :rtype: dict

    CLI Example:

    .. code-block:: bash

        salt '*' drbd.setup_show
        salt '*' drbd.setup_show name=<resource name>
    '''

    ret = {'name': name,
           'result': False,
           'comment': ''}

    # Only support json format
    cmd = 'drbdsetup show --json {}'.format(name)

    ret = _get_json_output_save(cmd)

    return ret


def setup_status(name='all'):
    '''
    Show the DRBD running status.
    Only support enable the json format so far.

    :type name: str
    :param name:
        Resource name.

    :return: The resource configuration.
    :rtype: dict

    CLI Example:

    .. code-block:: bash

        salt '*' drbd.setup_status
        salt '*' drbd.setup_status name=<resource name>
    '''

    cmd = 'drbdsetup status --json {}'.format(name)

    ret = _get_json_output_save(cmd)

    return ret


# Define OUTPUT_OPTIONS after setup_status() and status() defined
OUTPUT_OPTIONS = {
  "json": {
    "volume": "devices",
    "state": "disk-state",
    "connection": "connections",
    "peer_node": "name",
    "peer_node_vol": "peer_devices",
    "peer_node_state": "peer-disk-state",
    "local_cnt": "lower-pending",
    "get_res_func": setup_status
  },
  "text": {
    "volume": "local volumes",
    "state": "disk",
    "connection": "peer nodes",
    "peer_node": "peernode name",
    "peer_node_vol": "peer volumes",
    "peer_node_state": "peer-disk",
    "get_res_func": status
  }
}


def check_sync_status(name, peernode='all'):
    '''
    Query a drbd resource until fully synced for all volumes.

    :type name: str
    :param name:
        Resource name. Not support all.

    :type peernode: str
    :param peernode:
        Peer node name. Default: all

    CLI Example:

    .. code-block:: bash

        salt '*' drbd.check_sync_status <resource name> <peernode name>
    '''
    if __salt__['drbd.json']:
        output = OUTPUT_OPTIONS['json']
    else:
        output = OUTPUT_OPTIONS['text']

    # Need a specific node name instead of `all`. res should only have one element
    resources = output["get_res_func"](name)

    if not resources:
        return False

    res = resources[0]

    if _is_local_all_uptodated(res, output) and _is_peers_uptodated(
            res, output, peernode=peernode) and _is_no_backing_dev_request(
            res, output):
        return True

    return False
