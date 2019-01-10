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
'''

# Import Python libs
from __future__ import absolute_import, unicode_literals, print_function

from salt import exceptions

# Import third party libs
try: # pragma: no cover
    import crmsh
    HAS_CRMSH = True
except ImportError:
    HAS_CRMSH = False

__virtualname__ = 'crm'

CRM_COMMAND = '/usr/sbin/crm'


def __virtual__():  # pragma: no cover
    '''
    Only load this module if shaptools python module is installed
    '''
    if HAS_CRMSH:
        return __virtualname__
    return (
        False,
        'The crmsh execution module failed to load: the crmsh python'
        ' library is not available.')


def cluster_status():
    '''
    Reports the status for the cluster messaging layer on the local node

    CLI Example:

    .. code-block:: bash

        salt '*' crm.status
    '''
    cmd = '{crm_command} cluster status'.format(crm_command=CRM_COMMAND)
    return __salt__['cmd.retcode'](cmd)


def cluster_start():
    '''
    Starts the cluster-related system services on this node

    CLI Example:

    .. code-block:: bash

        salt '*' crm.start
    '''
    cmd = '{crm_command} cluster start'.format(crm_command=CRM_COMMAND)
    return __salt__['cmd.retcode'](cmd)


def cluster_stop():
    '''
    Stops the cluster-related system services on this node

    CLI Example:

    .. code-block:: bash

        salt '*' crm.stop
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

        salt '*' crm.run "pwd"
    '''
    cmd = '{crm_command} cluster run "{cmd}"'.format(
        crm_command=CRM_COMMAND, cmd=cmd)
    return __salt__['cmd.retcode'](cmd)


def cluster_health():
    '''
    Execute health check

    CLI Example:

    .. code-block:: bash

        salt '*' crm.health
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

        salt '*' crm.health
    '''
    cmd = '{crm_command} cluster wait_for_startup'.format(crm_command=CRM_COMMAND)
    if timeout:
        if not isinstance(timeout, int):
            raise exceptions.SaltInvocationError('timeout must be integer type')
        cmd = '{cmd} {timeout}'.format(cmd=cmd, timeout=timeout)
    return __salt__['cmd.retcode'](cmd)


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
    quiet:
        execute the command in quiet mode (no output)

    CLI Example:

    .. code-block:: bash

        salt '*' crm.init hacluster
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
        Watchdog to set. If None the watchdog is not set
    interface
        Network interface to bind the cluster. If None wlan0 is used
    quiet:
        execute the command in quiet mode (no output)

    CLI Example:

    .. code-block:: bash

        salt '*' crm.join 192.168.1.41
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

        salt '*' crm.remove 192.168.1.41 True
    '''
    cmd = '{crm_command} cluster remove -y -c {host}'.format(
        crm_command=CRM_COMMAND, host=host)
    if force:
        cmd = '{cmd} --force'.format(cmd=cmd)
    if quiet:
        cmd = '{cmd} -q'.format(cmd=cmd)

    return __salt__['cmd.retcode'](cmd)
