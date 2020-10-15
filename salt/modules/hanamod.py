# -*- coding: utf-8 -*-
'''
Module to provide SAP HANA functionality to Salt

.. versionadded:: pending

:maintainer:    Xabier Arbulu Insausti <xarbulu@suse.com>
:maturity:      alpha
:depends:       ``shaptools`` Python module
:platform:      all

:configuration: This module requires the shaptools python module and uses the
    following defaults which may be overridden in the minion configuration:

.. code-block:: yaml

    hana.sid: 'prd'
    hana.inst: '00'
    hana.password: 'Qwerty1234'
'''


# Import Python libs
from __future__ import absolute_import, unicode_literals, print_function

import logging
import time
import re
import sys
import os

if sys.version_info.major == 2: # pragma: no cover
    import imp

from salt.ext.six.moves import reload_module
from salt import exceptions
from salt.utils import files as salt_files

# Import third party libs
try:
    from shaptools import hana
    from shaptools import hdb_connector
    from shaptools.hdb_connector.connectors import base_connector
    HAS_HANA = True
except ImportError:  # pragma: no cover
    HAS_HANA = False

LOGGER = logging.getLogger(__name__)

__virtualname__ = 'hana'

LABEL_FILE = 'LABEL.ASC'
LABELIDX_FILE = 'LABELIDX.ASC'


class SapFolderNotFoundError(Exception):
    '''
    SAP folder not found exception
    '''


def __virtual__():  # pragma: no cover
    '''
    Only load this module if shaptools python module is installed
    '''
    if HAS_HANA:
        return __virtualname__
    return (
        False,
        'The hana execution module failed to load: the shaptools python'
        ' library is not available.')


def _init(
        sid=None,
        inst=None,
        password=None):
    '''
    Returns an instance of the hana instance

    sid
        HANA system id (PRD for example)
    inst
        HANA instance number (00 for example)
    password
        HANA instance password
    '''
    if sid is None:
        sid = __salt__['config.option']('hana.sid', None)
    if inst is None:
        inst = __salt__['config.option']('hana.inst', None)
    if password is None:
        password = __salt__['config.option']('hana.password', None)

    try:
        return hana.HanaInstance(sid, inst, password)
    except TypeError as err:
        raise exceptions.SaltInvocationError(err)


def is_installed(
        sid=None,
        inst=None,
        password=None):
    '''
    Check if SAP HANA platform is installed

    sid
        HANA system id (PRD for example)
    inst
        HANA instance number (00 for example)
    password
        HANA instance password

    Returns:
        bool: True if installed, False otherwise

    CLI Example:

    .. code-block:: bash

        salt '*' hana.is_installed prd '"00"' pass
    '''
    hana_inst = _init(sid, inst, password)
    return hana_inst.is_installed()


def create_conf_file(
        software_path,
        conf_file,
        root_user,
        root_password):
    '''
    Create SAP HANA configuration template file

    software_path
        Path where SAP HANA software is downloaded
    conf_file
        Path where configuration file will be created
    root_user
        Root user name
    root_password
        Root user password

    Returns:
        str: Configuration file path

    CLI Example:

    .. code-block:: bash

        salt '*' hana.create_conf_file /installation_path /home/myuser/hana.conf root root
    '''
    try:
        return hana.HanaInstance.create_conf_file(
            software_path, conf_file, root_user, root_password)
    except hana.HanaError as err:
        raise exceptions.CommandExecutionError(err)


def update_conf_file(
        conf_file,
        **extra_parameters):
    '''
    Update SAP HANA installation configuration file

    conf_file
        Path to the existing configuration file
    extra_parameters (dict): Dictionary with the values to be updated. Use the exact
        name of the SAP configuration file for the key

    Returns:
        str: Configuration file path

    CLI Example:

    .. code-block:: bash

        salt '*' hana.update_conf_file /home/myuser /home/myuser/hana.conf sid=PRD
    '''
    try:
        return hana.HanaInstance.update_conf_file(conf_file, **extra_parameters)
    except IOError as err:
        raise exceptions.CommandExecutionError(err)

def update_hdb_pwd_file(
        hdb_pwd_file,
        **extra_parameters):
    '''
    Update SAP HANA XML password file

    hdb_pwd_file
        Path to the existing XML password file
    extra_parameters (dict): Dictionary with the values to be updated. Use the exact
        name of the SAP XML password file for the key

    Returns:
        str: XML password file path

    CLI Example:

    .. code-block:: bash

        salt '*' hana.update_hdb_pwd_file /root /root/hdb_passwords.xml sapadm_password=DummyPasswd
    '''
    try:
        return hana.HanaInstance.update_hdb_pwd_file(hdb_pwd_file, **extra_parameters)
    except IOError as err:
        raise exceptions.CommandExecutionError(err)

def install(
        software_path,
        conf_file,
        root_user,
        root_password,
        hdb_pwd_file=None):
    '''
    Install SAP HANA with configuration file

    software_path
        Path where SAP HANA software is downloaded
    conf_file
        Path where configuration file will be created
    root_user
        Root user name
    root_password
        Root user password
    hdb_pwd_file
        Path where XML password file exists(optional)
    CLI Example:

    .. code-block:: bash

        salt '*' hana.install /installation_path /home/myuser/hana.conf root root /root/hdb_passwords.xml
    '''
    try:
        hana.HanaInstance.install(
            software_path, conf_file, root_user, root_password, hdb_pwd_file)
    except hana.HanaError as err:
        raise exceptions.CommandExecutionError(err)


def uninstall(
        root_user,
        root_password,
        installation_folder=None,
        sid=None,
        inst=None,
        password=None):
    '''
    Uninstall SAP HANA platform

    root_user
        Root user name
    root_password
        Root user password
    installation_folder
        Path where SAP HANA is installed (/hana/shared by default)
    sid
        HANA system id (PRD for example)
    inst
        HANA instance number (00 for example)
    password
        HANA instance password

    CLI Example:

    .. code-block:: bash

        salt '*' hana.uninstall root root
    '''
    hana_inst = _init(sid, inst, password)
    kwargs = {}
    if installation_folder:
        kwargs['installation_folder'] = installation_folder
    try:
        hana_inst.uninstall(root_user, root_password, **kwargs)
    except hana.HanaError as err:
        raise exceptions.CommandExecutionError(err)


def is_running(
        sid=None,
        inst=None,
        password=None):
    '''
    Check if SAP HANA daemon is running

    sid
        HANA system id (PRD for example)
    inst
        HANA instance number (00 for example)
    password
        HANA instance password

    Returns:
        bool: True if running, False otherwise

    CLI Example:

    .. code-block:: bash

        salt '*' hana.is_running prd '"00"' pass
    '''
    hana_inst = _init(sid, inst, password)
    return hana_inst.is_running()


# pylint:disable=W1401
def get_version(
        sid=None,
        inst=None,
        password=None):
    '''
    Get SAP HANA version

    sid
        HANA system id (PRD for example)
    inst
        HANA instance number (00 for example)
    password
        HANA instance password

    CLI Example:

    .. code-block:: bash

        salt '*' hana.get_version prd '"00"' pass
    '''
    hana_inst = _init(sid, inst, password)
    try:
        return hana_inst.get_version()
    except hana.HanaError as err:
        raise exceptions.CommandExecutionError(err)


def start(
        sid=None,
        inst=None,
        password=None):
    '''
    Start hana instance

    sid
        HANA system id (PRD for example)
    inst
        HANA instance number (00 for example)
    password
        HANA instance password

    CLI Example:

    .. code-block:: bash

        salt '*' hana.start prd '"00"' pass
    '''
    hana_inst = _init(sid, inst, password)
    try:
        hana_inst.start()
    except hana.HanaError as err:
        raise exceptions.CommandExecutionError(err)


def stop(
        sid=None,
        inst=None,
        password=None):
    '''
    Stop hana instance

    sid
        HANA system id (PRD for example)
    inst
        HANA instance number (00 for example)
    password
        HANA instance password

    CLI Example:

    .. code-block:: bash

        salt '*' hana.stop prd '"00"' pass
    '''
    hana_inst = _init(sid, inst, password)
    try:
        hana_inst.stop()
    except hana.HanaError as err:
        raise exceptions.CommandExecutionError(err)


def get_sr_state(
        sid=None,
        inst=None,
        password=None):
    '''
    Get system replication status in th current node

    sid
        HANA system id (PRD for example)
    inst
        HANA instance number (00 for example)
    password
        HANA instance password

    Returns:
        str: String between PRIMARY, SECONDARY and DISABLED

    CLI Example:

    .. code-block:: bash

        salt '*' hana.get_sr_state prd '"00"' pass
    '''
    hana_inst = _init(sid, inst, password)
    try:
        return hana_inst.get_sr_state()
    except hana.HanaError as err:
        raise exceptions.CommandExecutionError(err)


def sr_enable_primary(
        name,
        sid=None,
        inst=None,
        password=None):
    '''
    Enable SAP HANA system replication as primary node

    name
        Name to give to the node
    sid
        HANA system id (PRD for example)
    inst
        HANA instance number (00 for example)
    password
        HANA instance password

    CLI Example:

    .. code-block:: bash

        salt '*' hana.sr_enable_primary NUREMBERG prd '"00"' pass
    '''
    hana_inst = _init(sid, inst, password)
    try:
        hana_inst.sr_enable_primary(name)
    except hana.HanaError as err:
        raise exceptions.CommandExecutionError(err)


def sr_disable_primary(
        sid=None,
        inst=None,
        password=None):
    '''
    Disable SAP HANA system replication as primary node

    sid
        HANA system id (PRD for example)
    inst
        HANA instance number (00 for example)
    password
        HANA instance password

    CLI Example:

    .. code-block:: bash

        salt '*' hana.sr_disable_primary prd '"00"' pass
    '''
    hana_inst = _init(sid, inst, password)
    try:
        hana_inst.sr_disable_primary()
    except hana.HanaError as err:
        raise exceptions.CommandExecutionError(err)


def sr_register_secondary(
        name,
        remote_host,
        remote_instance,
        replication_mode,
        operation_mode,
        sid=None,
        inst=None,
        password=None,
        primary_pass=None,
        timeout=None,
        interval=None):
    '''
    Register SAP HANA system replication as secondary node

    name
        Name to give to the node
    remote_host
        Primary node hostname
    remote_instance
        Primary node instance
    replication_mode
        Replication mode
    operation_mode
        Operation mode
    sid
        HANA system id (PRD for example)
    inst
        HANA instance number (00 for example)
    password
        HANA instance password
    primary_pass
        Password of the xxxadm sap user where the node will be registered
    timeout
        Timeout in seconds to wait until the primary node system replication is available
    interval
        Interval in seconds to retry the secondary registration process if it fails until

    CLI Example:

    .. code-block:: bash

        salt '*' hana.sr_register_secondary PRAGUE hana01 00 sync logreplay prd '"00"' pass
    '''
    hana_inst = _init(sid, inst, password)
    try:
        kwargs = {}
        if primary_pass:
            kwargs['primary_pass'] = primary_pass
        if timeout:
            kwargs['timeout'] = timeout
        if interval:
            kwargs['interval'] = interval
        hana_inst.sr_register_secondary(
            name, remote_host, remote_instance,
            replication_mode, operation_mode,
            **kwargs)
    except hana.HanaError as err:
        raise exceptions.CommandExecutionError(err)


def sr_changemode_secondary(
        new_mode,
        sid=None,
        inst=None,
        password=None):
    '''
    Change secondary synchronization mode

    new_mode
        New mode between sync|syncmem|async
    sid
        HANA system id (PRD for example)
    inst
        HANA instance number (00 for example)
    password
        HANA instance password

    CLI Example:

    .. code-block:: bash

        salt '*' hana.sr_changemode_secondary sync prd '"00"' pass
    '''
    hana_inst = _init(sid, inst, password)
    try:
        hana_inst.sr_changemode_secondary(new_mode)
    except hana.HanaError as err:
        raise exceptions.CommandExecutionError(err)


def sr_unregister_secondary(
        primary_name,
        sid=None,
        inst=None,
        password=None):
    '''
    Unegister SAP HANA system replication from primary node

    name
        Name to give to the node
    sid
        HANA system id (PRD for example)
    inst
        HANA instance number (00 for example)
    password
        HANA instance password

    CLI Example:

    .. code-block:: bash

        salt '*' hana.sr_unregister_secondary NUREMBERG prd '"00"' pass
    '''
    hana_inst = _init(sid, inst, password)
    try:
        hana_inst.sr_unregister_secondary(primary_name)
    except hana.HanaError as err:
        raise exceptions.CommandExecutionError(err)


def check_user_key(
        key,
        sid=None,
        inst=None,
        password=None):
    '''
    Check the use key existance

    key
        User key name
    sid
        HANA system id (PRD for example)
    inst
        HANA instance number (00 for example)
    password
        HANA instance password

    Returns:
        bool: True if it exists, False otherwise

    CLI Example:

    .. code-block:: bash

        salt '*' hana.check_user_key key prd '"00"' pass
    '''
    hana_inst = _init(sid, inst, password)
    try:
        return hana_inst.check_user_key(key)
    except hana.HanaError as err:
        raise exceptions.CommandExecutionError(err)


def create_user_key(
        key_name,
        environment,
        user_name,
        user_password,
        database=None,
        sid=None,
        inst=None,
        password=None):
    '''
    Create user key entry for the database

    key_name
        User key
    environment
        Key environment
    user_name
        User name
    user_password
        User password
    database
        Database name
    sid
        HANA system id (PRD for example)
    inst
        HANA instance number (00 for example)
    password
        HANA instance password

    CLI Example:

    .. code-block:: bash

        salt '*' hana.create_user_key key hana01:30013 SYSTEM pass SYSTEMDB prd '"00"' pass
    '''
    hana_inst = _init(sid, inst, password)
    try:
        hana_inst.create_user_key(
            key_name, environment, user_name, user_password, database)
    except hana.HanaError as err:
        raise exceptions.CommandExecutionError(err)


def create_backup(
        database,
        backup_name,
        key_name=None,
        user_name=None,
        user_password=None,
        sid=None,
        inst=None,
        password=None):
    '''
    Create the primary node backup.

    key_name or user_name/user_password combination,
    one of them must be provided

    database
        Database name
    back_name
        Backup name
    key_name
        Keystore to connect to sap hana db
    user_name
        User to connect to sap hana db
    user_password
        Password to connecto to sap hana db
    sid
        HANA system id (PRD for example)
    inst
        HANA instance number (00 for example)
    password
        HANA instance password

    CLI Example:

    .. code-block:: bash

        salt '*' hana.create_backup key pass SYSTEMDB backup prd '"00"' pass
    '''
    hana_inst = _init(sid, inst, password)
    try:
        hana_inst.create_backup(
            database, backup_name, key_name, user_name, user_password)
    except hana.HanaError as err:
        raise exceptions.CommandExecutionError(err)


def sr_cleanup(
        sid=None,
        inst=None,
        password=None,
        force=False):
    '''
    Clean system replication state

    sid
        HANA system id (PRD for example)
    inst
        HANA instance number (00 for example)
    password
        HANA instance password
    force
        Force cleanup

    CLI Example:

    .. code-block:: bash

        salt '*' hana.sr_cleanup true prd '"00"' pass
    '''
    hana_inst = _init(sid, inst, password)
    try:
        hana_inst.sr_cleanup(force)
    except hana.HanaError as err:
        raise exceptions.CommandExecutionError(err)


def set_ini_parameter(
        ini_parameter_values,
        database,
        file_name,
        layer,
        layer_name=None,
        reconfig=False,
        key_name=None,
        user_name=None,
        user_password=None,
        sid=None,
        inst=None,
        password=None):
    '''
    Update HANA ini configuration parameter

    key_name or user_name/user_password combination,
    one of them must be provided

    ini_parameter_values
        List containing HANA parameter details where each entry looks like:
        {'section_name':'name', 'parameter_name':'param_name', 'parameter_value':'value'}
    database
        Database name
    file_name
        INI configuration file name
    layer
        Target layer for the configuration change
    layer_name
        Target either a tenant name or a host name(optional)
    reconfig
        If apply changes to running HANA instance(optional)
    key_name
        Keystore to connect to sap hana db
    user_name
        User to connect to sap hana db
    user_password
        Password to connecto to sap hana db
    sid
        HANA system id (PRD for example)
    inst
        HANA instance number (00 for example)
    password
        HANA instance password

    CLI Example:

    .. code-block:: bash

        salt '*' hana.set_ini_parameter '[{"section_name":"memorymanager",
        "parameter_name":"global_allocation_limit", "parameter_value":"26000"}]'
        SYSTEMDB global.ini HOST node01 key prd '"00"' pass
    '''
    hana_inst = _init(sid, inst, password)
    try:
        hana_inst.set_ini_parameter(
            ini_parameter_values=ini_parameter_values, database=database,
            file_name=file_name, layer=layer,
            layer_name=layer_name, reconfig=reconfig,
            key_name=key_name, user_name=user_name, user_password=user_password)
    except hana.HanaError as err:
        raise exceptions.CommandExecutionError(err)


def unset_ini_parameter(
        ini_parameter_names,
        database,
        file_name,
        layer,
        layer_name=None,
        reconfig=False,
        key_name=None,
        user_name=None,
        user_password=None,
        sid=None,
        inst=None,
        password=None):
    '''
    Update HANA ini configuration parameter

    key_name or user_name/user_password combination,
    one of them must be provided

    ini_parameter_names:
        List of HANA parameter names where each entry looks like
        {'section_name':'name', 'parameter_name':'param_name'}
    database
        Database name
    file_name
        INI configuration file name
    layer
        Target layer for the configuration change
    layer_name
        Target either a tenant name or a host name(optional)
    reconfig
        If apply changes to running HANA instance(optional)
    key_name
        Keystore to connect to sap hana db
    user_name
        User to connect to sap hana db
    user_password
        Password to connecto to sap hana db
    sid
        HANA system id (PRD for example)
    inst
        HANA instance number (00 for example)
    password
        HANA instance password

    CLI Example:

    .. code-block:: bash

        salt '*' hana.unset_ini_parameter '[{"section_name":"memorymanager",
        "parameter_name":"global_allocation_limit"}]'
        SYSTEMDB global.ini SYSTEM key prd '"00"' pass
    '''
    hana_inst = _init(sid, inst, password)
    try:
        hana_inst.unset_ini_parameter(
            ini_parameter_names=ini_parameter_names, database=database,
            file_name=file_name, layer=layer,
            layer_name=layer_name, reconfig=reconfig,
            key_name=key_name, user_name=user_name, user_password=user_password)
    except hana.HanaError as err:
        raise exceptions.CommandExecutionError(err)


def wait_for_connection(
        host,
        port,
        user,
        password,
        timeout=60,
        interval=5):
    '''
    Wait until HANA is ready trying to connect to the database

    host
        Host where HANA is running
    port
        HANA database port
    user
        User to connect to the databse
    password
        Password to connect to the database
    timeout
        Timeout to try to connect to the database
    interval
        Interval to try the connection

    CLI Example:

    .. code-block:: bash

        salt '*' hana.wait_for_hana 192.168.10.15 30015 SYSTEM pass
    '''
    connector = hdb_connector.HdbConnector()
    current_time = time.time()
    current_timeout = current_time + timeout
    while current_time <= current_timeout:
        try:
            connector.connect(host, port, user=user, password=password)
            connector.disconnect()
            break

        except base_connector.ConnectionError:
            time.sleep(interval)
            current_time = time.time()
    else:
        raise exceptions.CommandExecutionError(
            'HANA database not available after {} seconds in {}:{}'.format(
                timeout, host, port
            ))


def reload_hdb_connector():  # pragma: no cover
    '''
    As hdb_connector uses pyhdb or dbapi, if these packages are installed on the fly,
    we need to reload the connector to import the correct api
    '''

    def __import_mod(name):
        '''
        Find more info in: https://docs.python.org/2/library/imp.html
        '''
        try:
            return sys.modules[name]
        except KeyError:
            pass

        file_ptr, pathname, description = imp.find_module(name)

        try:
            return imp.load_module(name, file_ptr, pathname, description)
        finally:
            # Since we may exit via an exception, close file_ptr explicitly.
            if file_ptr:
                file_ptr.close()

    if sys.version_info.major == 2:
        # pyhdbcli has a cyclical import so it raises an error, but the module is loaded properly
        try:
            __import_mod('pyhdbcli')
        except ImportError:
            pass
        __import_mod('hdbcli/dbapi')
        __import_mod('hdbcli')

    reload_module(hdb_connector)


def _find_sap_folder(software_folders, folder_pattern, recursion_level=0):
    '''
    Find a SAP folder following a recursive approach using the LABEL and LABELIDX files

    Args:
        software_folder (list): List of subfolder where the SAP folder is looked for`
        folder_pattern (str): Pattern of the LABEL.ASC to look fo
        recursion_level (int): Number of subfolder levels to check
            Examples:
                1 means to check recursively in the subfolder present in software_folders folders
                2 means to check in the first subfolder and the folder within
    '''
    for folder in software_folders:
        label = '{}/{}'.format(folder, LABEL_FILE)
        try:
            with salt_files.fopen(label, 'r') as label_file_ptr:
                label_content = label_file_ptr.read().strip()
                if folder_pattern.match(label_content):
                    return folder
                else:
                    LOGGER.debug(
                        '%s folder does not contain %s pattern', folder, folder_pattern.pattern)
        except IOError:
            LOGGER.debug('%s file not found in %s. Skipping folder', LABEL_FILE, folder)

        labelidx = '{}/{}'.format(folder, LABELIDX_FILE)
        try:
            with salt_files.fopen(labelidx, 'r') as labelidx_file_ptr:
                labelidx_content = labelidx_file_ptr.read().splitlines()
                new_folders = [
                    '{}/{}'.format(folder, new_folder) for new_folder in labelidx_content]
                try:
                    return _find_sap_folder(new_folders, folder_pattern)
                except SapFolderNotFoundError:
                    continue
        except IOError:
            LOGGER.debug('%s file not found in %s. Skipping folder', LABELIDX_FILE, folder)

        if recursion_level:
            subfolders = [os.path.join(folder, found_dir) for found_dir in
                          os.listdir(folder) if os.path.isdir(os.path.join(folder, found_dir))]
            try:
                return _find_sap_folder(subfolders, folder_pattern, recursion_level-1)
            except SapFolderNotFoundError:
                continue

    raise SapFolderNotFoundError(
        'SAP folder with {} pattern not found'.format(folder_pattern.pattern))


def extract_pydbapi(
        name,
        software_folders,
        output_dir,
        hana_version='20',
        additional_extract_options=None):
    '''
    Extract HANA pydbapi python client from the provided software folders

    name
        Name of the package that needs to be installed
    software_folders
        Folders list where the HANA client is located. It's used as a list as the pydbapi client
        will be found automatically among different folders and providing several folders is a
        standard way in SAP landscape
    output_dir
        Folder where the package is extracted
    additional_extract_options
        Additional options to pass to the tar extraction command
    '''
    if not isinstance(software_folders, list):
        raise TypeError(
            "software_folders must be a list, not {} type".format(type(software_folders).__name__)
        )
    current_platform = hana.HanaInstance.get_platform()
    tar_options_str = ('{} -xvf'.format(additional_extract_options)
                       if additional_extract_options else '-xvf')
    hana_client_pattern = re.compile('^HDB_CLIENT:{}.*:{}:.*'.format(
        hana_version, current_platform))
    try:
        # recursion_level is set to 1 because the HANA client
        # is extracted in SAP_HANA_CLIENT if the file is compressed as SAR
        hana_client_folder = _find_sap_folder(
            software_folders, hana_client_pattern, recursion_level=1)
    except SapFolderNotFoundError:
        raise exceptions.CommandExecutionError('HANA client not found')
    pydbapi_file = '{}/client/{}'.format(hana_client_folder, name)
    __salt__['archive.tar'](options=tar_options_str, tarfile=pydbapi_file, cwd=output_dir)
    return pydbapi_file
