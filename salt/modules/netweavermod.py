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


def execute_sapcontrol(
        function,
        sid=None,
        inst=None,
        password=None):
    '''
    Run a sapcontrol command

    function:
        sapcontrol function
    sid
        Netweaver system id (PRD for example)
    inst
        Netweaver instance number (00 for example)
    password
        Netweaver instance password
    '''
    try:
        netweaver_inst = _init(sid, inst, password)
        return netweaver_inst._execute_sapcontrol(function).output
    except netweaver.NetweaverError as err:
        raise exceptions.CommandExecutionError(err)


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


def is_instance_installed(
        sap_instance,
        dispstatus=None,
        virtual_host=None,
        sid=None,
        inst=None,
        password=None):
    '''
    Check if a SAP Netweaver instance is installed among all the nodes

    This is a possible output of the command:

    hostname, instanceNr, httpPort, httpsPort, startPriority, features, dispstatus
    sapha1as, 0, 50013, 50014, 1, MESSAGESERVER|ENQUE, GREEN
    sapha1er, 10, 51013, 51014, 3, ENQREP, GREEN
    sapha1aas, 2, 50213, 50214, 3, ABAP|GATEWAY|ICMAN|IGS, GREEN
    sapha1pas, 1, 50113, 50114, 3, ABAP|GATEWAY|ICMAN|IGS, GREEN

    sap_instance:
        Check for specific SAP instances. Available options:
        MESSAGESERVER,ENQREP,ENQUE,ABAP,GATEWAY,ICMAN,IGS
    dispstatus:
        Check for a particular dispstatus. Available options: GREEN, GRAY
    virtual_host:
        Check for a particular virtual host. If set to None the first match will be returned
    sid
        Netweaver system id (PRD for example)
    inst
        Netweaver instance number (00 for example)
    password
        Netweaver instance password
    '''
    try:
        netweaver_inst = _init(sid, inst, password)
        instances = netweaver_inst.get_system_instances().output
        instance_pattern = '{virtual_host}.*{sap_instance}.*{dispstatus}.*'.format(
            virtual_host=virtual_host if virtual_host else '',
            sap_instance=sap_instance,
            dispstatus=dispstatus if dispstatus else '')
        found = netweaver.shell.find_pattern(instance_pattern, instances)
        if found:
            found = found.group(0).replace(' ', '').split(',')
            return {
                'hostname': found[0],
                'instance': found[1],
                'http_port': found[2],
                'https_port': found[3],
                'start_priority': found[4],
                'features': found[5],
                'dispstatus': found[6],
            }
        return False
    except netweaver.NetweaverError:
        return False


def attach_virtual_host(
        virtual_host,
        virtual_host_interface='eth0',
        virtual_host_mask=24):
    '''
    Attach virtual host ip address to network interface

    virtual_host
        Virtual host name
    virtual_host_interface
        Network interface to attach the virtual host ip address
    virtual_host_mask
        Ip address mask for the virtual address (24 be default)

    Returns:
        str: Attached ip address

    CLI Example:

    .. code-block:: bash

        salt '*' netweaver.attach_virtual_host my_host eth1
    '''
    ip_address = __salt__['hosts.get_ip'](virtual_host)
    if not ip_address:
        raise exceptions.CommandExecutionError('virtual host {} not available'.format(virtual_host))
    result = __salt__['cmd.retcode'](
        'ip a | grep {}/{}'.format(ip_address, virtual_host_mask), python_shell=True)
    if result == 1:
        result = __salt__['cmd.run']('ip address add {}/{} dev {}'.format(
            ip_address, virtual_host_mask, virtual_host_interface))
    # Non zero return code in any of the cmd commands
    if result:
        raise exceptions.CommandExecutionError('error running "ip address" command')

    return ip_address

def update_conf_file(
        conf_file,
        **extra_parameters):
    '''
    Update SAP Netweaver installation configuration file

    conf_file
        Path to the existing configuration file
    extra_parameters (dict): Dictionary with the values to be updated. Use the exact
        name of the SAP configuration file for the key

    Returns:
        str: Configuration file path

    CLI Example:

    .. code-block:: bash

        salt '*' netweaver.update_conf_file /tmp/nw.inifile.params sid=HA1
    '''
    try:
        return netweaver.NetweaverInstance.update_conf_file(conf_file, **extra_parameters)
    except IOError as err:
        raise exceptions.CommandExecutionError(err)

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


def get_ensa_version(
        sap_instance,
        sid=None,
        inst=None,
        password=None):
    '''
    Get currently installed sap instance ENSA version

    sap_instance
        Check for specific SAP instances. Available options: ascs, ers.
    sid
        Netweaver system id (PRD for example)
    inst
        Netweaver instance number (00 for example)
    password
        Netweaver instance password
    '''
    try:
        netweaver_inst = _init(sid, inst, password)
        return netweaver_inst.get_ensa_version(sap_instance)
    except (ValueError, netweaver.NetweaverError) as err:
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
        List with path to additional folders used during the installation
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
    # Add additional dvds
    if additional_dvds:
        __salt__['file.append'](start_dir, args=additional_dvds)

    return cwd
