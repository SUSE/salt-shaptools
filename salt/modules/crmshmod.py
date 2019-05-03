# -*- coding: utf-8 -*-
'''
Module to provide CRM shell (HA cluster) functionality to Salt

.. versionadded:: pending

:maintainer:    Xabier Arbulu Insausti <xarbulu@suse.com>
:maturity:      alpha
:depends:       ``crmsh`` Python module
:platform:      all

:configuration: This module requires the crmsh python module and uses the
    following defaults which may be overridden in the minion configuration:

.. code-block:: yaml

    #TODO: create some default configuration parameters if needed

    Disclaimer: Only the methods status, init and join are tested using the
    ha-cluster-init and ha-cluster-join methods
'''

# Import Python libs
from __future__ import absolute_import, unicode_literals, print_function
import logging

from salt import exceptions
import salt.utils.path


__virtualname__ = 'crm'

CRMSH = 'crmsh'
CRM_COMMAND = '/usr/sbin/crm'
HA_INIT_COMMAND = '/usr/sbin/ha-cluster-init'
HA_JOIN_COMMAND = '/usr/sbin/ha-cluster-join'
# Below this version ha-cluster-init will be used to create the cluster
CRM_NEW_VERSION = '3.0.0'
COROSYNC_CONF = '/etc/corosync/corosync.conf'

LOGGER = logging.getLogger(__name__)
# True if current execution has a newer version than CRM_NEW_VERSION


def __virtual__():
    '''
    Only load this module if crm package is installed
    '''
    if bool(salt.utils.path.which(CRM_COMMAND)):
        version = __salt__['pkg.version'](CRMSH)
        use_crm = __salt__['pkg.version_cmp'](
            version, CRM_NEW_VERSION) >= 0
        LOGGER.info('crmsh version: %s', version)
        LOGGER.info(
            '%s will be used', 'crm' if use_crm else 'ha-cluster')

    else:
        return (
            False,
            'The crmsh execution module failed to load: the crm package'
            ' is not available.')

    if not use_crm and not bool(salt.utils.path.which(HA_INIT_COMMAND)):
        return (
            False,
            'The crmsh execution module failed to load: the ha-cluster-init'
            ' package is not available.')

    __salt__['crmsh.version'] = use_crm
    return __virtualname__


def status():
    '''
    Show cluster status. The status is displayed by crm_mon. Supply additional
    arguments for more information or different format.

    CLI Example:

    .. code-block:: bash

        salt '*' crm.status
    '''
    cmd = '{crm_command} status'.format(crm_command=CRM_COMMAND)
    return __salt__['cmd.retcode'](cmd)


def cluster_status():
    '''
    Reports the status for the cluster messaging layer on the local node

    CLI Example:

    .. code-block:: bash

        salt '*' crm.cluster_status
    '''
    cmd = '{crm_command} cluster status'.format(crm_command=CRM_COMMAND)
    return __salt__['cmd.retcode'](cmd)


def cluster_start():
    '''
    Starts the cluster-related system services on this node

    CLI Example:

    .. code-block:: bash

        salt '*' crm.cluster_start
    '''
    cmd = '{crm_command} cluster start'.format(crm_command=CRM_COMMAND)
    return __salt__['cmd.retcode'](cmd)


def cluster_stop():
    '''
    Stops the cluster-related system services on this node

    CLI Example:

    .. code-block:: bash

        salt '*' crm.cluster_stop
    '''
    cmd = '{crm_command} cluster stop'.format(crm_command=CRM_COMMAND)
    return __salt__['cmd.retcode'](cmd)


def cluster_run(
        cmd):
    '''
    This command takes a shell statement as argument, executes that statement on
    all nodes in the cluster, and reports the result.

    CLI Example:

    .. code-block:: bash

        salt '*' crm.cluster_run "pwd"
    '''
    cmd = '{crm_command} cluster run "{cmd}"'.format(
        crm_command=CRM_COMMAND, cmd=cmd)
    return __salt__['cmd.retcode'](cmd)


def cluster_health():
    '''
    Execute health check

    CLI Example:

    .. code-block:: bash

        salt '*' crm.cluster_health
    '''
    cmd = '{crm_command} cluster health'.format(crm_command=CRM_COMMAND)
    return __salt__['cmd.retcode'](cmd)


def wait_for_startup(
        timeout=None):
    '''
    Mostly useful in scripts or automated workflows, this command will attempt
    to connect to the local cluster node repeatedly. The command will keep
    trying until the cluster node responds, or the timeout elapses.
    The timeout can be changed by supplying a value in seconds as an argument.

    timeout:
        Timeout to wait in seconds

    CLI Example:

    .. code-block:: bash

        salt '*' crm.wait_for_startup
    '''
    cmd = '{crm_command} cluster wait_for_startup'.format(crm_command=CRM_COMMAND)
    if timeout:
        if not isinstance(timeout, int):
            raise exceptions.SaltInvocationError('timeout must be integer type')
        cmd = '{cmd} {timeout}'.format(cmd=cmd, timeout=timeout)
    return __salt__['cmd.retcode'](cmd)


def _add_watchdog_sbd(watchdog):
    '''
    Update /etc/sysconfig/sbd file to add the watchdog device.
    Specifically the line 'SBD_WATCHDOG_DEV=/dev/watchdog' is updated/added

    **INFO: This method is used when the ha-cluster-init/join options
    are used**

    watchdog:
        Watchdog device to add to sbd configuration file
    '''
    __salt__['file.replace'](
        path='/etc/sysconfig/sbd',
        pattern='^SBD_WATCHDOG_DEV=.*',
        repl='SBD_WATCHDOG_DEV={}'.format(watchdog),
        append_if_not_found=True
    )


def _set_corosync_value(path, value):
    '''
    Set value to a parameter in the corosync configuration file

    Example:
        update transport mode to unicast
        _update_corosync_conf('totem.transport', 'udpu')
    '''
    cmd = '{crm_command} corosync set {path} {value}'.format(
        crm_command=CRM_COMMAND, path=path, value=value)
    __salt__['cmd.run'](cmd, raise_err=True)


def _add_node_corosync(addr, name):
    '''
    Set value to a parameter in the corosync configuration file
    '''
    if not __salt__['file.contains_regex'](
            path=COROSYNC_CONF, regex='^nodelist.*'):
        __salt__['file.append'](path=COROSYNC_CONF, args='nodelist {}')

    cmd = '{crm_command} corosync add-node {addr} {name}'.format(
        crm_command=CRM_COMMAND, addr=addr, name=name or '')
    __salt__['cmd.run'](cmd, raise_err=True)


def _create_corosync_authkey():
    '''
    Create corosync authkey
    '''
    cmd = 'corosync-keygen'
    __salt__['cmd.run'](cmd, raise_err=True)


def _set_corosync_unicast(addr, name=None):
    '''
    Update corosync configuration file value with a new entry.

    By default /etc/corosync/corosync.conf is used.

    Raises:
        salt.exceptions.CommandExecutionError: If any salt cmd.run fails
    '''
    cmd = '{crm_command} cluster stop'.format(crm_command=CRM_COMMAND)
    __salt__['cmd.run'](cmd, raise_err=True)

    __salt__['file.line'](
        path=COROSYNC_CONF, match='.*mcastaddr:.*', mode='delete')
    _set_corosync_value('totem.transport', 'udpu')
    _add_node_corosync(addr, name)
    _create_corosync_authkey()

    cmd = '{crm_command} cluster start'.format(crm_command=CRM_COMMAND)
    __salt__['cmd.run'](cmd, raise_err=True)


def _join_corosync_unicast(host, interface=None):
    '''
    Check if first node is configured as unicast and in that case add the
    new node information to the configuration file

    Warning: SSH connection must be available
    '''
    unicast = __salt__['cmd.retcode'](
        'ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -t '
        'root@{host} "grep \'transport: udpu\' {conf}"'.format(
            host=host, conf=COROSYNC_CONF))
    if unicast:
        LOGGER.info('cluster not set as unicast')
        return

    name = __salt__['network.get_hostname']()
    addr = __salt__['network.interface_ip'](interface or 'eth0')

    cmd = 'ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -t '\
        'root@{host} "sudo {crm_command} corosync add-node {addr} {name}"'.format(
            host=host, crm_command=CRM_COMMAND, addr=addr, name=name)
    __salt__['cmd.run'](cmd, raise_err=True)


def _crm_init(
        name,
        watchdog=None,
        interface=None,
        unicast=None,
        admin_ip=None,
        sbd=None,
        sbd_dev=None,
        quiet=None):
    '''
    crm cluster init command execution
    '''
    cmd = '{crm_command} cluster init -y -n {name}'.format(
        crm_command=CRM_COMMAND, name=name)
    if watchdog:
        cmd = '{cmd} -w {watchdog}'.format(cmd=cmd, watchdog=watchdog)
    if interface:
        cmd = '{cmd} -i {interface}'.format(cmd=cmd, interface=interface)
    if unicast:
        cmd = '{cmd} -u'.format(cmd=cmd)
    if admin_ip:
        cmd = '{cmd} -A {admin_ip}'.format(cmd=cmd, admin_ip=admin_ip)
    if sbd:
        cmd = '{cmd} --enable-sbd'.format(cmd=cmd)
        if sbd_dev:
            cmd = '{cmd} -s {sbd_dev}'.format(cmd=cmd, sbd_dev=sbd_dev)
    if quiet:
        cmd = '{cmd} -q'.format(cmd=cmd)

    return __salt__['cmd.retcode'](cmd)


def _ha_cluster_init(
        watchdog=None,
        interface=None,
        unicast=None,
        admin_ip=None,
        sbd=None,
        sbd_dev=None,
        quiet=None):
    '''
    ha-cluster-init command execution
    '''
    if watchdog:
        _add_watchdog_sbd(watchdog)

    cmd = '{ha_init_command} -y'.format(
        ha_init_command=HA_INIT_COMMAND)
    if interface:
        cmd = '{cmd} -i {interface}'.format(cmd=cmd, interface=interface)
    if admin_ip:
        cmd = '{cmd} -A {admin_ip}'.format(cmd=cmd, admin_ip=admin_ip)
    if sbd:
        cmd = '{cmd} -S'.format(cmd=cmd)
        if sbd_dev:
            cmd = '{cmd} -s {sbd_dev}'.format(cmd=cmd, sbd_dev=sbd_dev)
    if quiet:
        cmd = '{cmd} -q'.format(cmd=cmd)

    return_code = __salt__['cmd.retcode'](cmd)
    if not return_code and unicast:
        name = __salt__['network.get_hostname']()
        addr = __salt__['network.interface_ip'](interface or 'eth0')
        _set_corosync_unicast(addr, name)
    return return_code


def cluster_init(
        name,
        watchdog=None,
        interface=None,
        unicast=None,
        admin_ip=None,
        sbd=None,
        sbd_dev=None,
        quiet=None):
    '''
    Initialize a cluster from scratch.

    INFO: This action will remove any old configuration (corosync, pacemaker, etc)

    name
        Cluster name (only used in crmsh version higher than CRM_NEW_VERSION)
    watchdog
        Watchdog to set. If None default watchdog (/dev/watchdog) is used
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
    quiet:
        execute the command in quiet mode (no output)

    CLI Example:

    .. code-block:: bash

        salt '*' crm.cluster_init hacluster
    '''
    # INFO: 2 different methods are created to make easy to read/understand
    # and create the corresponing UT
    if __salt__['crmsh.version']:
        return _crm_init(
            name, watchdog, interface, unicast, admin_ip, sbd, sbd_dev, quiet)

    LOGGER.warn('The parameter name is not considered!')
    return _ha_cluster_init(
        watchdog, interface, unicast, admin_ip, sbd, sbd_dev, quiet)


def _crm_join(
        host,
        watchdog=None,
        interface=None,
        quiet=None):
    '''
    crm cluster join command execution
    '''
    cmd = '{crm_command} cluster join -y -c {host}'.format(
        crm_command=CRM_COMMAND, host=host)
    if watchdog:
        cmd = '{cmd} -w {watchdog}'.format(cmd=cmd, watchdog=watchdog)
    if interface:
        cmd = '{cmd} -i {interface}'.format(cmd=cmd, interface=interface)
    if quiet:
        cmd = '{cmd} -q'.format(cmd=cmd)

    return __salt__['cmd.retcode'](cmd)


def _ha_cluster_join(
        host,
        watchdog=None,
        interface=None,
        quiet=None):
    '''
    ha-cluster-join command execution
    '''
    if watchdog:
        _add_watchdog_sbd(watchdog)

    # To logic to apply unicast is done in _join_corosync_unicast
    _join_corosync_unicast(host, interface)
    cmd = '{ha_join_command} -y -c {host}'.format(
        ha_join_command=HA_JOIN_COMMAND, host=host)
    if interface:
        cmd = '{cmd} -i {interface}'.format(cmd=cmd, interface=interface)
    if quiet:
        cmd = '{cmd} -q'.format(cmd=cmd)

    return_code = __salt__['cmd.retcode'](cmd)
    if return_code:
        return return_code

    cmd = '{crm_command} resource refresh'.format(crm_command=CRM_COMMAND)
    return __salt__['cmd.retcode'](cmd)


def cluster_join(
        host,
        watchdog=None,
        interface=None,
        quiet=None):
    '''
    Join the current node to an existing cluster.
    The current node cannot be a member of a cluster already.

    INFO: This action will remove any old configuration (corosync, pacemaker, etc)

    host
        Hostname or ip address of a node of an existing cluster
    watchdog
        Watchdog to set. If None the watchdog is not set (
        only used in crmsh version higher than CRM_NEW_VERSION)
    interface
        Network interface to bind the cluster. If None wlan0 is used
    quiet:
        execute the command in quiet mode (no output)

    CLI Example:

    .. code-block:: bash

        salt '*' crm.cluster_join 192.168.1.41
    '''
    # INFO: 2 different methods are created to make easy to read/understand
    # and create the corresponing UT
    if __salt__['crmsh.version']:
        return _crm_join(host, watchdog, interface, quiet)

    return _ha_cluster_join(host, watchdog, interface, quiet)


def cluster_remove(
        host,
        force=None,
        quiet=None):
    '''
    Remove a node from the cluster

    host
        Hostname or ip address of a node of an existing cluster
    force
        Force removal. If the host is itself it's mandatory
    quiet:
        execute the command in quiet mode (no output)

    CLI Example:

    .. code-block:: bash

        salt '*' crm.cluster_remove 192.168.1.41 True
    '''
    cmd = '{crm_command} cluster remove -y -c {host}'.format(
        crm_command=CRM_COMMAND, host=host)
    if force:
        cmd = '{cmd} --force'.format(cmd=cmd)
    if quiet:
        cmd = '{cmd} -q'.format(cmd=cmd)

    return __salt__['cmd.retcode'](cmd)


def configure_load(
        method,
        url,
        is_xml=None):
    '''
    Load a part of configuration (or all of it) from a local file or a
    network URL. The replace method replaces the current configuration with
    the one from the source. The update method tries to import the contents
    into the current configuration. The push method imports the contents into
    the current configuration and removes any lines that are not present in
    the given configuration. The file may be a CLI file or an XML file.

    method
        Used method (check in the description)
    url
        Used configuration file url (or path if it's a local file)
    is_xml:
        Set to true if the file is an xml file

    CLI Example:

    .. code-block:: bash

        salt '*' crm.configure_load update file.conf
    '''
    cmd = '{crm_command} configure load {xml}{method} {url}'.format(
        crm_command=CRM_COMMAND,
        xml='xml ' if is_xml else '',
        method=method, url=url)

    return __salt__['cmd.retcode'](cmd)
