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
        Check for specific SAP instances. Available options: ascs, ers, pas, aas.
        If None it will check if any instance is installed

    Returns:
        bool: True if installed, False otherwise

    CLI Example:

    .. code-block:: bash

        salt '*' netweaver.is_installed prd '"00"' pass
    '''
    netweaver_inst = _init(sid, inst, password)
    return netweaver_inst.is_installed(sap_instance)


def is_db_installed(
        host,
        port,
        schema_name,
        schema_password):
    '''
    Check if SAP Netweaver DB instance is installed

    host:
        Host where HANA is running
    port:
        HANA database port
    schema_name:
        Schema installed in the dabase
    schema_password:
        Password of the user for the schema

    Returns:
        bool: True if installed, False otherwise

    CLI Example:

    .. code-block:: bash

        salt '*' netweaver.is_db_installed 192.168.10.15 30013 SAPABAP1 password
    '''
    if 'hana.wait_for_connection' not in __salt__:
        raise exceptions.CommandExecutionError(
            'hana.wait_for_connection not available. hanamod must be installed and loaded')

    try:
        __salt__['hana.wait_for_connection'](
            host=host,
            port=port,
            user=schema_name,
            password=schema_password,
            timeout=0,
            interval=0)
        return True
    except exceptions.CommandExecutionError:
        return False


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
        root_password,
        cwd=None):
    '''
    Install SAP Netweaver instance with configuration file

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
    cwd
        New value for SAPINST_CWD parameter
        CAUTION: All of the files stored in this path will be removed except the
        start_dir.cd. This folder only will contain temporary files about the installation

    CLI Example:

    .. code-block:: bash

        salt '*' netweaver.install installation_path my_host product_id netweaver.conf root root
    '''
    try:
        netweaver.NetweaverInstance.install(
            software_path, virtual_host, product_id, conf_file, root_user, root_password, cwd=cwd)
    except netweaver.NetweaverError as err:
        raise exceptions.CommandExecutionError(err)


def install_ers(
        software_path,
        virtual_host,
        product_id,
        conf_file,
        root_user,
        root_password,
        cwd=None,
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
    cwd
        New value for SAPINST_CWD parameter
        CAUTION: All of the files stored in this path will be removed except the
        start_dir.cd. This folder only will contain temporary files about the installation
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
            cwd=cwd, ascs_password=ascs_password, timeout=timeout, interval=interval)
    except netweaver.NetweaverError as err:
        raise exceptions.CommandExecutionError(err)


def setup_cwd(
        software_path,
        cwd='/tmp/swpm_unattended',
        additional_dvds=None):
    '''
    Setup folder to run the sapinst tool in other directory (modified SAPINST_CWD)

    software_path
        Path where SAP Netweaver software is downloaded
    cwd
        Path used to run the installation. All the files created during the installation will
        be stored there.
        CAUTION: All of the files stored in this path will be removed except the
        start_dir.cd. This folder only will contain temporary files about the installation
    additional_dvds
        Path to additional folders used during the installation
    '''

    # Create folder. Remove if already exists first
    __salt__['file.remove'](cwd)
    __salt__['file.mkdir'](cwd, user='root', group='sapinst', mode=775)
    # Create start_dir.cd file
    start_dir = '{}/start_dir.cd'.format(cwd)
    __salt__['file.touch'](start_dir)
    __salt__['file.chown'](start_dir, 'root', 'sapinst')
    __salt__['file.set_mode'](start_dir, 775)
    # Add sapints_folder
    __salt__['file.append'](start_dir, args=software_path)
    # Add additional dvds. Add just /swpm at the beginning
    __salt__['file.append'](start_dir, args=['/swpm/{}'.format(dvd) for dvd in additional_dvds])

    return cwd
