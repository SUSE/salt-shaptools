# -*- coding: utf-8 -*-
'''
Module to provide SAP Netweaver functionality to Salt

.. versionadded:: pending

:maintainer:    Xabier Arbulu Insausti <xarbulu@suse.com>
:maturity:      alpha
:depends:       ``shaptools`` Python module
:platform:      all

:configuration: This module requires the shaptools python module and uses the
    following defaults which may be overridden in the minion configuration:

.. code-block:: yaml

    netweaver.sid: 'prd'
    netweaver.inst: '00'
    netweaver.password: 'Qwerty1234'
'''

# Import Python libs
from __future__ import absolute_import, unicode_literals, print_function

from salt import exceptions

# Import third party libs
try:
    from shaptools import netweaver
    HAS_NETWEAVER = True
except ImportError:  # pragma: no cover
    HAS_NETWEAVER = False

__virtualname__ = 'netweaver'


def __virtual__():  # pragma: no cover
    '''
    Only load this module if shaptools python module is installed
    '''
    if HAS_NETWEAVER:
        return __virtualname__
    return (
        False,
        'The netweaver execution module failed to load: the shaptools python'
        ' library is not available.')


def _init(
        sid=None,
        inst=None,
        password=None):
    '''
    Returns an instance of the netweaver instance

    sid
        Netweaver system id (PRD for example)
    inst
        Netweaver instance number (00 for example)
    password
        Netweaver instance password
    '''
    if sid is None:
        sid = __salt__['config.option']('netweaver.sid', None)
    if inst is None:
        inst = __salt__['config.option']('netweaver.inst', None)
    if password is None:
        password = __salt__['config.option']('netweaver.password', None)

    try:
        return netweaver.NetweaverInstance(sid, inst, password)
    except TypeError as err:
        raise exceptions.SaltInvocationError(err)


def is_installed(
        sid=None,
        inst=None,
        password=None,
        sap_instance=None):
    '''
    Check if SAP Netweaver platform is installed

    sid
        Netweaver system id (PRD for example)
    inst
        Netweaver instance number (00 for example)
    password
        Netweaver instance password
    sap_instance
        Check for specific SAP instances. Available options: ascs, ers. If None it will checked
        if any instance is installed

    Returns:
        bool: True if installed, False otherwise

    CLI Example:

    .. code-block:: bash

        salt '*' netweaver.is_installed prd '"00"' pass
    '''
    netweaver_inst = _init(sid, inst, password)
    return netweaver_inst.is_installed(sap_instance)


def attach_virtual_host(
        virtual_host,
        virtual_host_interface='eth0'):
    '''
    Attach virtual host ip address to network interface

    virtual_host
        Virtual host name
    virtual_host_interface:
        Network interface to attach the virtual host ip address

    Returns:
        str: Attached ip address

    CLI Example:

    .. code-block:: bash

        salt '*' netweaver.attach_virtual_host my_host eth1
    '''
    ip_address = __salt__['hosts.get_ip'](virtual_host)
    if not ip_address:
        raise exceptions.CommandExecutionError('virtual host {} not available'.format(virtual_host))
    result = __salt__['cmd.retcode']('ip a | grep {}/24'.format(ip_address), python_shell=True)
    if result == 1:
        result = __salt__['cmd.run']('ip address add {}/24 dev {}'.format(
            ip_address, virtual_host_interface))
    # Non zero return code in any of the cmd commands
    if result:
        raise exceptions.CommandExecutionError('error running "ip address" command')

    return ip_address


def install(
        software_path,
        virtual_host,
        product_id,
        conf_file,
        root_user,
        root_password):
    '''
    Install SAP Netweaver with configuration file

    software_path
        Path where SAP Netweaver software is downloaded
    virtual_host
        Virtual host associated to the SAP instance
    product_id
        Id of the product to be installed. Example: NW_ABAP_ASCS:NW750.HDB.ABAPHA
    conf_file
        Path to the configuration file used to install Netweaver
    root_user
        Root user name
    root_password
        Root user password

    CLI Example:

    .. code-block:: bash

        salt '*' netweaver.install installation_path my_host product_id netweaver.conf root root
    '''
    try:
        netweaver.NetweaverInstance.install(
            software_path, virtual_host, product_id, conf_file, root_user, root_password)
    except netweaver.NetweaverError as err:
        raise exceptions.CommandExecutionError(err)


def install_ers(
        software_path,
        virtual_host,
        product_id,
        conf_file,
        root_user,
        root_password,
        ascs_password=None,
        timeout=0,
        interval=5):
    '''
    Install SAP Netweaver ERS instance with configuration file

    software_path
        Path where SAP Netweaver software is downloaded
    virtual_host
        Virtual host associated to the SAP instance
    product_id
        Id of the product to be installed. Example: NW_ABAP_ASCS:NW750.HDB.ABAPHA
    conf_file
        Path to the configuration file used to install Netweaver
    root_user
        Root user name
    root_password
        Root user password
    ascs_password
        Password of the SAP user in the machine hosting the ASCS instance.
        If it's not set the same password used to install ERS will be used
    timeout
        Timeout of the installation process. If 0 it will try to install the instance only once
    interval
        Retry interval in seconds

    CLI Example:

    .. code-block:: bash

        salt '*' netweaver.install installation_path my_host product_id netweaver.conf root root
    '''
    try:
        netweaver.NetweaverInstance.install_ers(
            software_path, virtual_host, product_id, conf_file, root_user, root_password,
            ascs_password=ascs_password, timeout=timeout, interval=interval)
    except netweaver.NetweaverError as err:
        raise exceptions.CommandExecutionError(err)
