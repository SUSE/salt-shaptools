'''
State module to provide CRMSH (HA cluster) functionality to Salt

.. versionadded:: pending

:maintainer:    Xabier Arbulu Insausti <xarbulu@suse.com>
:maturity:      alpha
:depends:       crmsh
:platform:      all

:configuration: This module requires the crm python module and uses the
    following defaults which may be overridden in the minion configuration:

.. code-block:: yaml

    #TODO: create some default configuration parameters if needed

:usage:

.. code-block:: yaml
    cluster-init:
      crm.initialized:
        - name: 'hacluster'
        - watchdog: '/dev/watchdog'
        - interface: 'wlan0'
        - unicast: False
        - admin_ip: '192.168.1.50'
        - sbd: False
'''


# Import python libs
from __future__ import absolute_import, unicode_literals, print_function


# Import salt libs
from salt import exceptions
from salt import utils as salt_utils
from salt.ext import six


__virtualname__ = 'crm'


def __virtual__():  # pragma: no cover
    '''
    Only load if the hana module is in __salt__
    '''
    return 'crm.cluster_init' in __salt__


def cluster_absent(
        name='localhost',
        quiet=None):
    """
    Machine is not running as a cluster node

    quiet:
        execute the command in quiet mode (no output)
    """
    ret = {'name': name,
           'changes': {},
           'result': False,
           'comment': ''}

    if __salt__['crm.status']():
        ret['result'] = True
        ret['comment'] = 'Cluster is already not running'
        return ret

    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = 'Cluster node {} would be removed'.format(name)
        ret['changes']['name'] = name
        return ret

    try:
        #  Here starts the actual process
        result = __salt__['crm.cluster_remove'](
            host=name,
            force=True,
            quiet=quiet)

        if result:
            ret['changes']['name'] = name
            ret['comment'] = 'Error removing cluster node'
            ret['result'] = False
            return ret

        ret['changes']['name'] = name
        ret['comment'] = 'Cluster node removed'
        ret['result'] = True
        return ret

    except exceptions.CommandExecutionError as err:
        ret['comment'] = six.text_type(err)
        return ret


def cluster_initialized(
        name,
        watchdog=None,
        interface=None,
        unicast=None,
        admin_ip=None,
        sbd=None,
        sbd_dev=None,
        sbd_timeout_watchdog=5,
        sbd_timeout_msgwait=10,
        no_overwrite_sshkey=False,
        quiet=None):
    """
    Machine is running a cluster node

    name
        Cluster name
    watchdog
        Watchdog to set. If None the watchdog is not set
    interface
        Network interface to bind the cluster. If None wlan0 is used
    unicast
        Set the cluster in unicast mode. If None multicast is used
    admin_ip
        Virtual IP address. If None the virtual address is not set
    sbd
        Enable sbd usage. If None sbd is not set
    sbd_dev
        sbd device path. To be used "sbd" parameter must be used too. If None,
            the sbd is set as diskless.
        This parameter can be a string (meaning one disk) or a list with multiple disks
    sbd_timeout_watchdog
        watchdog timeout for sbd device creation. To be used "sbd" parameter must be used too.
            defaults to 5
    sbd_timeout_msgwait
        msgwait timeout for sbd device creation. To be used "sbd" parameter must be used too.
            defaults to 10
    no_overwrite_sshkey
        No overwrite the currently existing sshkey (/root/.ssh/id_rsa)
        Only available after crmsh 3.0.0
    quiet:
        execute the command in quiet mode (no output)
    """
    ret = {'name': name,
           'changes': {},
           'result': False,
           'comment': ''}

    if not __salt__['crm.status']():
        ret['result'] = True
        ret['comment'] = 'Cluster is already initialized'
        return ret

    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = '{} would be initialized'.format(name)
        ret['changes']['name'] = name
        return ret

    try:
        #  Here starts the actual process
        result = __salt__['crm.cluster_init'](
            name=name,
            watchdog=watchdog,
            interface=interface,
            unicast=unicast,
            admin_ip=admin_ip,
            sbd=sbd,
            sbd_dev=sbd_dev,
            sbd_timeout_watchdog=sbd_timeout_watchdog,
            sbd_timeout_msgwait=sbd_timeout_msgwait,
            no_overwrite_sshkey=no_overwrite_sshkey,
            quiet=quiet)

        if result:
            ret['changes']['name'] = name
            ret['comment'] = 'Error initialazing cluster'
            ret['result'] = False
            return ret

        ret['changes']['name'] = name
        ret['comment'] = 'Cluster initialized'
        ret['result'] = True
        return ret

    except exceptions.CommandExecutionError as err:
        ret['comment'] = six.text_type(err)
        return ret


def cluster_joined(
        name,
        watchdog=None,
        interface=None,
        quiet=None):
    """
    Machine is joined to a cluster as a node

    name
        hostname or ip address of a cluster node to join
    watchdog
        Watchdog to set. If None the watchdog is not set
    quiet:
        execute the command in quiet mode (no output)
    """
    ret = {'name': name,
           'changes': {},
           'result': False,
           'comment': ''}

    if not __salt__['crm.status']():
        ret['result'] = True
        ret['comment'] = 'Node is already joined to a cluster'
        return ret

    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = 'Node would be joined to {}'.format(name)
        ret['changes']['name'] = name
        return ret

    try:
        #  Here starts the actual process
        result = __salt__['crm.cluster_join'](
            host=name,
            watchdog=watchdog,
            interface=interface,
            quiet=quiet)

        if result:
            ret['changes']['name'] = name
            ret['comment'] = 'Error joining to the cluster'
            ret['result'] = False
            return ret

        ret['changes']['name'] = name
        ret['comment'] = 'Node joined to the cluster'
        ret['result'] = True
        return ret

    except exceptions.CommandExecutionError as err:
        ret['comment'] = six.text_type(err)
        return ret


def cluster_configured(
        name,
        url,
        is_xml=None):
    """
    Machine is congifured with the provided configuration file

    name
        Used method. replace, update or push
    url
        Configuration file path or url
    is_xml:
        True if the configuration file is xml type, False otherwise
    """
    method = name

    ret = {'name': method,
           'changes': {},
           'result': False,
           'comment': ''}

    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = 'Cluster would be configured with method {} and file {}'.format(
            method, url)
        ret['changes']['method'] = method
        ret['changes']['url'] = url
        return ret

    try:
        #  Here starts the actual process
        if __salt__['crm.status']():
            ret['result'] = False
            ret['comment'] = 'Cluster is not created yet. Run cluster_initialized before'
            return ret

        result = __salt__['crm.configure_load'](
            method=method,
            url=url,
            is_xml=is_xml)

        if result:
            ret['comment'] = 'Error configuring the cluster with method {} and file {}'.format(
                method, url)
            ret['result'] = False
            return ret

        ret['changes']['method'] = method
        ret['changes']['url'] = url
        ret['comment'] = 'Cluster properly configured'
        ret['result'] = True
        return ret

    except exceptions.CommandExecutionError as err:
        ret['comment'] = six.text_type(err)
        return ret


def _convert2dict(file_content_lines):
    """
    Convert the corosync configuration file to a dictionary
    """
    corodict = {}
    index = 0

    for i, line in enumerate(file_content_lines):
        stripped_line = line.strip()
        if not stripped_line or stripped_line[0] == '#':
            continue

        if index > i:
            continue

        line_items = stripped_line.split()
        if '{' in stripped_line:
            corodict[line_items[0]], new_index = _convert2dict(file_content_lines[i+1:])
            index = i + new_index
        elif line_items[0][-1] == ':':
            corodict[line_items[0][:-1]] = line_items[-1]
        elif '}' in stripped_line:
            return corodict, i+2

    return corodict, index


def _mergedicts(main_dict, changes_dict, applied_changes, initial_path=''):
    """
    Merge the 2 dictionaries. We cannot use update as it changes all the children of an entry
    """
    for key, value in changes_dict.items():
        current_path = '{}.{}'.format(initial_path, key)
        if key in main_dict.keys() and not isinstance(value, dict):
            if str(main_dict[key]) != str(value):
                applied_changes[current_path] = value
            main_dict[key] = value
        elif key in main_dict.keys():
            modified_dict, new_changes = _mergedicts(main_dict[key], value, applied_changes, current_path)
            main_dict[key] = modified_dict
            applied_changes.update(new_changes)

        else:  # Entry not found in current main dictionary, so we can update all
            main_dict[key] = changes_dict[key]
            applied_changes[current_path] = value

    return main_dict, applied_changes


def _convert2corosync(corodict, indentation=''):
    """
    Convert a corosync data dictionary to the corosync configuration file format
    """
    output = ''
    for key, value in corodict.items():
        if isinstance(value, dict):
            output += '{}{} {{\n'.format(indentation, key)
            indentation += '\t'
            output += _convert2corosync(value, indentation)
            indentation = indentation[:-1]
            output += '{}}}\n'.format(indentation)
        else:
            output += '{}{}: {}\n'.format(indentation, key, value)
    return output


def corosync_updated(
        name,
        data,
        backup=True):
    """
    Configure corosync configuration file

    name
        Corosync configuration file path
    data
        Dictionary with the values that have to be changed. The method won't do any sanity check
        so, it will put in the configuration file value added in this parameter
    """

    changes = {}
    ret = {'name': name,
           'changes': changes,
           'result': False,
           'comment': ''}

    with salt_utils.files.fopen(name, 'r') as file_content:
        corodict, _ = _convert2dict(file_content.read().splitlines())
    new_conf_dict, changes = _mergedicts(corodict, data, {})

    if not changes:
        ret['changes'] = changes
        ret['comment'] = 'Corosync already has the required configuration'
        ret['result'] = True
        return ret

    new_conf_file_content = _convert2corosync(new_conf_dict)
    if backup:
        __salt__['file.copy'](name, '{}.backup'.format(name))
    __salt__['file.write'](name, new_conf_file_content)

    ret['changes'] = changes
    ret['comment'] = 'Corosync configuration file updated'
    ret['result'] = True
    return ret
