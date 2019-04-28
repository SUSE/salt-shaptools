# -*- coding: utf-8 -*-
'''
DRBD administration module
'''
from __future__ import absolute_import, print_function, unicode_literals

import logging

from salt.exceptions import CommandExecutionError
from salt.ext import six

import salt.utils.json

LOG = logging.getLogger(__name__)

# Define the module's virtual name
__virtualname__ = 'drbd'


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
        4: {' peer-disk:': 'PEERDISK'}
    }

    ret = switch.get(spaces, 'UNKNOWN')

    # isinstance(ret, str) only works when run directly, calling need unicode(six)
    if isinstance(ret, six.text_type):
        return ret

    for x in ret:
        if x in line:
            return ret[x]


def _add_res(line):
    '''
    Analyse the line of local resource of ``drbdadm status``
    '''
    global resource
    fields = line.strip().split()

    if resource:
        ret.append(resource)
        resource = {}

    resource["resource name"] = fields[0]
    resource["local role"] = fields[1].split(":")[1]
    resource["local volumes"] = []
    resource["peer nodes"] = []


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
        resource['local volumes'].append(volume)
    else:
        # 'PEERDISK'
        lastpnodevolumes.append(volume)


def _add_peernode(line):
    '''
    Analyse the line of peer nodes of ``drbdadm status``
    '''
    global lastpnodevolumes

    fields = line.strip().split()

    peernode = {}
    peernode["peernode name"] = fields[0]
    #Could be role or connection:
    peernode[fields[1].split(":")[0]] = fields[1].split(":")[1]
    peernode["peer volumes"] = []
    resource["peer nodes"].append(peernode)
    lastpnodevolumes = peernode["peer volumes"]


def _empty(dummy):
    '''
    Action of empty line of ``drbdadm status``
    '''


def _unknown_parser(line):
    '''
    Action of unsupported line of ``drbdadm status``
    '''
    global ret
    ret = {"Unknown parser": line}


def _line_parser(line):
    '''
    Call action for different lines
    '''
    section = _analyse_status_type(line)

    switch = {
        '': _empty,
        'RESOURCE': _add_res,
        'PEERNODE': _add_peernode,
        'LOCALDISK': _add_volume,
        'PEERDISK': _add_volume,
    }

    func = switch.get(section, _unknown_parser)

    func(line)


def _is_local_all_uptodated(name):
    '''
    Check whether all local volumes are UpToDate.
    '''

    ret = False

    res = status(name)
    if not res or len(res) == 0:
        return ret

    # Since name is not all, res only have one element
    for vol in res[0]['local volumes']:
        if vol['disk'] != 'UpToDate':
            return ret

    ret = True
    return ret


def _is_peers_uptodated(name, peernode='all'):
    '''
    Check whether all volumes of peer node are UpToDate.

    .. note::

        If peernode is not match, will return None, same as False.
    '''
    ret = None

    res = status(name)
    if not res or len(res) == 0:
        return ret

    # Since name is not all, res only have one element
    for node in res[0]['peer nodes']:
        if peernode != 'all' and node['peernode name'] != peernode:
            continue

        for vol in node['peer volumes']:
            if vol['peer-disk'] != 'UpToDate':
                ret = False
                return ret
            else:
                # At lease one volume is 'UpToDate'
                ret = True

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


# Global para for func status
ret = []
resource = {}
lastpnodevolumes = None


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
    global ret
    global resource
    ret = []
    resource = {}

    cmd = ['drbdadm', 'status']
    cmd.append(name)

    #One possible output: (number of resource/node/vol are flexible)
    #resource role:Secondary
    #  volume:0 disk:Inconsistent
    #  volume:1 disk:Inconsistent
    #  drbd-node1 role:Primary
    #    volume:0 replication:SyncTarget peer-disk:UpToDate done:10.17
    #    volume:1 replication:SyncTarget peer-disk:UpToDate done:74.08
    #  drbd-node2 role:Secondary
    #    volume:0 peer-disk:Inconsistent resync-suspended:peer
    #    volume:1 peer-disk:Inconsistent resync-suspended:peer

    result = __salt__['cmd.run_all'](cmd)
    if result['retcode'] != 0:
        LOG.info('No status due to {} ({}).'.format(result['stderr'], result['retcode']))
        return None

    for line in result['stdout'].splitlines():
        _line_parser(line)

    if resource:
        ret.append(resource)

    return ret


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

    cmd = ['drbdadm', 'create-md']
    cmd.append(name)

    if force:
        cmd.append('--force')

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

    cmd = ['drbdadm', 'up']
    cmd.append(name)

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

    cmd = ['drbdadm', 'down']
    cmd.append(name)

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

    cmd = ['drbdadm', 'primary']
    cmd.append(name)

    if force:
        cmd.append('--force')

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

    cmd = ['drbdadm', 'secondary']
    cmd.append(name)

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

    ret = []

    cmd = ['drbdadm', 'adjust']
    cmd.append(name)

    return __salt__['cmd.retcode'](cmd)


def setup_show(name='all', json=True):
    '''
    Show the DRBD resource via drbdsetup directly.
    Only support the json format so far.

    :type name: str
    :param name:
        Resource name.

    :type json: bool
    :param json:
        Use the json format.

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

    cmd = ['drbdsetup', 'show']
    cmd.append(name)

    if json:
        cmd.append('--json')

        results = __salt__['cmd.run_all'](cmd)

        if 'retcode' not in results or results['retcode'] != 0:
            ret['comment'] = 'Error({}) happend when show resource via drbdsetup.'.format(
                results['retcode'])
            return ret

        try:
            ret = salt.utils.json.loads(results['stdout'], strict=False)
        except ValueError:
            raise CommandExecutionError('Error happens when try to load the json output.',
                                        info=results)

    return ret


def setup_status(name='all', json=True):
    '''
    Show the DRBD running status.
    Only support enable the json format so far.

    :type name: str
    :param name:
        Resource name.

    :type json: bool
    :param json:
        Use the json format.

    :return: The resource configuration.
    :rtype: dict

    CLI Example:

    .. code-block:: bash

        salt '*' drbd.setup_status
        salt '*' drbd.setup_status name=<resource name>
    '''

    ret = {'name': name,
           'result': False,
           'comment': ''}

    cmd = ['drbdsetup', 'status']
    cmd.append(name)

    if json:
        cmd.append('--json')

        results = __salt__['cmd.run_all'](cmd)

        if 'retcode' not in results or results['retcode'] != 0:
            ret['comment'] = 'Error({}) happend when show resource via drbdsetup.'.format(
                results['retcode'])
            return ret

        try:
            ret = salt.utils.json.loads(results['stdout'], strict=False)
        except ValueError:
            raise CommandExecutionError('Error happens when try to load the json output.',
                                        info=results)

    return ret


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
    if _is_local_all_uptodated(name) and _is_peers_uptodated(
            name, peernode=peernode):
        return True

    return False
