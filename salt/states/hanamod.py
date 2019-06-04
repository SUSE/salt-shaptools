# -*- coding: utf-8 -*-
'''
State module to provide SAP HANA functionality to Salt

.. versionadded:: pending

:maintainer:    Xabier Arbulu Insausti <xarbulu@suse.com>
:maturity:      alpha
:depends:       shaptools
:platform:      all

:configuration: This module requires the shaptools python module and uses the
    following defaults which may be overridden in the minion configuration:

.. code-block:: yaml

    hana.sid: 'prd'
    hana.inst: '00'
    hana.password: 'Qwerty1234'

:usage:

.. code-block:: yaml
    hana-install:
      hana.installed:
        - root_user: 'root'
        - root_password: 's'
        - software_path: '/root/sap_inst/51052481'
        - name: 'prd'
        - inst: '00'
        - password: 'Qwerty1234'
        - config_file: salt://hana_conf/hana.conf
        - extra_parameters:
          - hostname: 'hana01'

    NUREMBERG:
      hana.sr_primary_enabled:
        - sid: 'prd'
        - inst: '00'
        - password: 'Qwerty1234'
        - cleanup: true
        - backup:
          - user: 'backupkey'
          - password:  'Qwerty1234'
          - database: 'SYSTEMDB'
          - file: 'backup'
        - userkey:
          - key: 'backupkey'
          - environment: 'hana01:30013'
          - user: 'SYSTEM'
          - password: 'Qwerty1234'
          - database: 'SYSTEMDB'
        - require:
          - hana-install
'''


# Import python libs
from __future__ import absolute_import, unicode_literals, print_function


# Import salt libs
from salt import exceptions
from salt.ext import six


__virtualname__ = 'hana'

TMP_CONFIG_FILE = '/tmp/hana.conf'
INI_PARAM_PRELOAD_CS = {'section_name': 'system_replication', 'parameter_name': 'preload_column_tables'}
INI_PARAM_GAL = {'section_name': 'memorymanager', 'parameter_name': 'global_allocation_limit'}


def __virtual__():  # pragma: no cover
    '''
    Only load if the hana module is in __salt__
    '''
    return 'hana.is_installed' in __salt__


def _parse_dict(dict_params):
    '''
    Get dictionary type variable from sls list type
    '''
    output = {}
    for item in dict_params:
        for key, value in item.items():
            output[key] = value
    return output


def installed(
        name,
        inst,
        password,
        software_path,
        root_user,
        root_password,
        config_file=None,
        sapadm_password=None,
        system_user_password=None,
        extra_parameters={}):
    """
    Install SAP HANA if the platform is not installed yet. There are two ways of
    using in. The configuration file might be imported from the master to the minions
    using the *config_file* option, or if this value is not set, the sapadm_password
    and system_user_password values are mandatory

    name
        System id of the installed hana platform
    inst
        Instance number of the installed hana platform
    password
        Password of the installed hana platform user
    software_path:
        Path where the SAP HANA software is downloaded, it must be located in
        the minion itself
    root_user
        Root user name
    root_password
        Root user password
    config_file
        If config_file paremeter is set, it will be downloaded from the master
        to the minion and used in the installation. Values in this file might
        be changed setting then in the extra_parameters dictionary using the
        exact name as in the config file as a key
    sapadm_password
        If the config file is not set, the sapadm_password is mandatory. The
        password of the sap administrator user
    system_user_password
        If the config file is not set, the system_user_password is mandatory. The
        password of the database SYSTEM (superuser) user
    extra_parameters
        Optional configuration parameters (exact name as in the config file as a key)
    """
    sid = name

    ret = {'name': sid,
           'changes': {},
           'result': False,
           'comment': ''}

    if __salt__['hana.is_installed'](
            sid=sid,
            inst=inst,
            password=password):
        ret['result'] = True
        ret['comment'] = 'HANA is already installed'
        return ret

    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = '{} would be installed'.format(sid)
        ret['changes']['sid'] = sid
        return ret

    try:
        #  Here starts the actual process
        if config_file:
            __salt__['cp.get_file'](
                path=config_file,
                dest=TMP_CONFIG_FILE)
            ret['changes']['config_file'] = config_file
            config_file = TMP_CONFIG_FILE
        elif system_user_password is None or sapadm_password is None:
            ret['comment'] = 'If config_file is not provided '\
                'system_user_password and sapadm_password are mandatory'
            return ret
        else:
            config_file = __salt__['hana.create_conf_file'](
                software_path=software_path,
                conf_file=TMP_CONFIG_FILE,
                root_user=root_user,
                root_password=root_password)
            config_file = __salt__['hana.update_conf_file'](
                conf_file=config_file,
                sid=sid.upper(),
                password=password,
                number='{:0>2}'.format(inst),
                root_user=root_user,
                root_password=root_password,
                sapadm_password=sapadm_password,
                system_user_password=system_user_password)
            ret['changes']['config_file'] = 'new'
        if extra_parameters:
            extra_parameters = _parse_dict(extra_parameters)
            config_file = __salt__['hana.update_conf_file'](
                conf_file=config_file,
                extra_parameters=extra_parameters)

        __salt__['hana.install'](
            software_path=software_path,
            conf_file=config_file,
            root_user=root_user,
            root_password=root_password)
        ret['changes']['sid'] = sid
        ret['comment'] = 'HANA installed'
        ret['result'] = True
        return ret

    except exceptions.CommandExecutionError as err:
        ret['comment'] = six.text_type(err)
        return ret
    finally:
        __salt__['file.remove'](TMP_CONFIG_FILE)
        __salt__['file.remove']('{}.xml'.format(TMP_CONFIG_FILE))


def uninstalled(
        name,
        inst,
        password,
        root_user,
        root_password,
        installation_folder=None):
    '''
    Uninstall SAP HANA from node
    name
        System id of the installed hana platform
    inst
        Instance number of the installed hana platform
    password
        Password of the installed hana platform user
    root_user
        Root user name
    root_password
        Root user password
    instalation_folder
        HANA installation folder
    '''
    sid = name

    ret = {'name': sid,
           'changes': {},
           'result': False,
           'comment': ''}

    if not __salt__['hana.is_installed'](
            sid=sid,
            ints=inst,
            password=password):
        ret['result'] = True
        ret['comment'] = 'HANA already not installed'
        return ret

    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = '{} would be uninstalled'.format(sid)
        ret['changes']['sid'] = sid
        return ret

    try:
        #  Here starts the actual process
        __salt__['hana.uninstall'](
            root_user=root_user,
            root_password=root_password,
            sid=sid,
            inst=inst,
            password=password,
            installation_folder=installation_folder)
        ret['changes']['sid'] = sid
        ret['comment'] = 'HANA uninstalled'
        ret['result'] = True
        return ret

    except exceptions.CommandExecutionError as err:
        ret['comment'] = six.text_type(err)
        return ret


def sr_primary_enabled(
        name,
        sid,
        inst,
        password,
        backup=None,
        userkey=None):
    '''
    Set the node as a primary hana node and in running state

    name
        The name of the primary node
    sid
        System id of the installed hana platform
    inst
        Instance number of the installed hana platform
    password
        Password of the installed hana platform user
    userkey (optional)
        Create a new key user
        key_name (str):
            Key name
        environment:
            Database location (host:port)
        user_name:
            User to connect to sap hana db
        user_password
            Password to connect to sap hana db
        database (optional)
            Database name in MDC environment
    backup (optional)
        Create a new backup of the current database
        key_name
            Keystore to connect to sap hana db
        user_name
            User to connect to sap hana db
        user_password
            Password to connect to sap hana db
        database:
            Database name to backup
        file:
            Backup file name
    '''

    ret = {'name': name,
           'changes': {},
           'result': False,
           'comment': ''}

    if not __salt__['hana.is_installed'](sid, inst, password):
        ret['comment'] = 'HANA is not installed properly with the provided data'
        return ret

    current_state = __salt__['hana.get_sr_state'](
        sid=sid,
        inst=inst,
        password=password)
    running = __salt__['hana.is_running'](
        sid=sid,
        inst=inst,
        password=password)

    if running and current_state == 'PRIMARY':
        ret['result'] = True
        ret['comment'] = 'HANA node already set as primary and running'
        return ret

    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = '{} would be enabled as a primary node'.format(name)
        ret['changes']['primary'] = name
        ret['changes']['backup'] = backup
        ret['changes']['userkey'] = userkey
        return ret

    try:
        #  Here starts the actual process
        if not running:
            __salt__['hana.start'](
                sid=sid,
                inst=inst,
                password=password)
        if userkey:
            userkey_data = _parse_dict(userkey)
            __salt__['hana.create_user_key'](
                key_name=userkey_data.get('key_name'),
                environment=userkey_data.get('environment'),
                user_name=userkey_data.get('user_name'),
                user_password=userkey_data.get('user_password'),
                database=userkey_data.get('database', None),
                sid=sid,
                inst=inst,
                password=password)
            ret['changes']['userkey'] = userkey_data.get('key_name')
        if backup:
            backup_data = _parse_dict(backup)
            __salt__['hana.create_backup'](
                key_name=backup_data.get('key_name', None),
                user_name=backup_data.get('user_name', None),
                user_password=backup_data.get('user_password', None),
                database=backup_data.get('database'),
                backup_name=backup_data.get('file'),
                sid=sid,
                inst=inst,
                password=password)
            ret['changes']['backup'] = backup_data.get('file')
        __salt__['hana.sr_enable_primary'](
            name=name,
            sid=sid,
            inst=inst,
            password=password)
        new_state = __salt__['hana.get_sr_state'](
            sid=sid,
            inst=inst,
            password=password)
        ret['changes']['primary'] = name
        ret['comment'] = 'HANA node set as {}'.format(new_state)
        ret['result'] = True
        return ret

    except exceptions.CommandExecutionError as err:
        ret['comment'] = six.text_type(err)
        return ret


def sr_secondary_registered(
        name,
        remote_host,
        remote_instance,
        replication_mode,
        operation_mode,
        sid,
        inst,
        password,
        primary_pass=None,
        timeout=None,
        interval=None):
    '''
    Register a secondary node to an already enabled primary node

    name
        The name of the secondary node
    remote_host
        Primary node hostname
    remote_instance
        Primary node instance
    replication_mode
        Replication mode
    operation_mode
        Operation mode
    sid
        System id of the installed hana platform
    inst
        Instance number of the installed hana platform
    password
        Password of the installed hana platform user
    primary_pass
        Password of the xxxadm sap user where the node will be registered
    timeout
        Timeout in seconds to wait until the primary node system replication is available
    interval
        Interval in seconds to retry the secondary registration process if it fails until
    '''

    ret = {'name': name,
           'changes': {},
           'result': False,
           'comment': ''}

    if not __salt__['hana.is_installed'](
            sid=sid,
            inst=inst,
            password=password):
        ret['comment'] = 'HANA is not installed properly with the provided data'
        return ret

    current_state = __salt__['hana.get_sr_state'](
        sid=sid,
        inst=inst,
        password=password)
    running = __salt__['hana.is_running'](
        sid=sid,
        inst=inst,
        password=password)

    if running and current_state == 'SECONDARY':
        ret['result'] = True
        ret['comment'] = 'HANA node already set as secondary and running'
        return ret

    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = '{} would be registered as a secondary node'.format(name)
        ret['changes']['secondary'] = name
        return ret

    try:
        #  Here starts the actual process
        if running:
            __salt__['hana.stop'](
                sid=sid,
                inst=inst,
                password=password)
        __salt__['hana.sr_register_secondary'](
            name=name,
            remote_host=remote_host,
            remote_instance=remote_instance,
            replication_mode=replication_mode,
            operation_mode=operation_mode,
            primary_pass=primary_pass,
            timeout=timeout,
            interval=interval,
            sid=sid,
            inst=inst,
            password=password)
        __salt__['hana.start'](
            sid=sid,
            inst=inst,
            password=password)
        new_state = __salt__['hana.get_sr_state'](
            sid=sid,
            inst=inst,
            password=password)
        ret['changes']['secondary'] = name
        ret['comment'] = 'HANA node set as {}'.format(new_state)
        ret['result'] = True
        return ret

    except exceptions.CommandExecutionError as err:
        ret['comment'] = six.text_type(err)
        return ret


def sr_clean(
        name,
        inst,
        password,
        force):
    '''
    Clean the current node system replication mode
    name:
        System id of the installed hana platform
    inst
        Instance number of the installed hana platform
    password
        Password of the installed hana platform user
    force
        Force cleanup process
    '''

    sid = name

    ret = {'name': sid,
           'changes': {},
           'result': False,
           'comment': ''}

    if not __salt__['hana.is_installed'](
            sid=sid,
            inst=inst,
            password=password):
        ret['comment'] = 'HANA is not installed properly with the provided data'
        return ret

    current_state = __salt__['hana.get_sr_state'](
        sid=sid,
        inst=inst,
        password=password)
    running = __salt__['hana.is_running'](
        sid=sid,
        inst=inst,
        password=password)

    if current_state == 'DISABLED':
        ret['result'] = True
        ret['comment'] = 'HANA node already clean'
        return ret

    if __opts__['test']:
        ret['result'] = None
        ret['changes']['disabled'] = name
        ret['comment'] = '{} would be clean'.format(name)
        return ret

    try:
        #  Here starts the actual process
        if running:
            __salt__['hana.stop'](
                sid=sid,
                inst=inst,
                password=password)
        __salt__['hana.sr_cleanup'](
            sid=sid,
            inst=inst,
            password=password,
            force=force)
        new_state = __salt__['hana.get_sr_state'](
            sid=sid,
            inst=inst,
            password=password)
        ret['changes']['disabled'] = name
        ret['comment'] = 'HANA node set as {}'.format(new_state)
        ret['result'] = True
        return ret

    except exceptions.CommandExecutionError as err:
        ret['comment'] = six.text_type(err)
        return ret


def memory_resources_updated(
        name,
        global_allocation_limit,
        preload_column_tables,
        user_name,
        user_password,
        sid,
        inst,
        password):
    '''
    Update memory resources of a running HANA system by changing column preload behavior
    and changing the memory allocation size of HANA instance
    name:
        Host name of system installed hana platform
    global_allocation_limit:
        Max memory allocation limit for hana instance
    preload_column_tables:
        If preload HANA column tables on startup
    user_name
        User to connect to sap hana db
    user_password
        Password to connect to sap hana db
    sid
        System id of the installed hana platform
    inst
        Instance number of the installed hana platform
    password
        Password of the installed hana platform user
    '''
    INI_PARAM_PRELOAD_CS['parameter_value'] = preload_column_tables
    INI_PARAM_GAL['parameter_value'] = global_allocation_limit
    ini_parameter_values = [INI_PARAM_PRELOAD_CS, INI_PARAM_GAL]

    ret = {'name': sid,
           'changes': {},
           'result': False,
           'comment': ''}

    if not __salt__['hana.is_installed'](
            sid=sid,
            inst=inst,
            password=password):
        ret['comment'] = 'HANA is not installed properly with the provided data'
        return ret

    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = 'Memory resources would be updated on {}-{}'.format(name, sid)
        ret['changes']['sid'] = sid
        ret['changes']['global_allocation_limit'] = global_allocation_limit
        ret['changes']['preload_column_tables'] = preload_column_tables
        return ret

    running = __salt__['hana.is_running'](
        sid=sid,
        inst=inst,
        password=password)
    # TODO: check existing memory settings

    try:
        # ensure HANA is running for SQL to execute
        if not running:
            __salt__['hana.start'](
                sid=sid,
                inst=inst,
                password=password)

        __salt__['hana.set_ini_parameter'](
            ini_parameter_values=ini_parameter_values,
            database='SYSTEMDB',
            file_name='global.ini',
            layer='SYSTEM',
            layer_name=None,
            reconfig=True,
            user_name=user_name,
            user_password=user_password,
            sid=sid,
            inst=inst,
            password=password)
        ret['changes']['global_allocation_limit'] = global_allocation_limit
        ret['changes']['preload_column_tables'] = preload_column_tables
        # restart HANA for memory changes to take effect
        __salt__['hana.stop'](
            sid=sid,
            inst=inst,
            password=password)
        __salt__['hana.start'](
            sid=sid,
            inst=inst,
            password=password)
        ret['changes']['sid'] = sid
        ret['comment'] = 'Memory resources updated on {}-{}'.format(name, sid)
        ret['result'] = True
        return ret

    except exceptions.CommandExecutionError as err:
        ret['comment'] = six.text_type(err)
        return ret
