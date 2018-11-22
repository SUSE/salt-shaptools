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
    NUREMBERG:
      hana.primary_enabled:
        - sid: 'prd'
        - inst: '00'
        - password: 'Qwerty1234'
        - cleanup: true
        - backup:
          - user: 'backupkey'
          - password:  Qwerty1234
          - database: 'SYSTEMDB'
          - file: 'backup'
        - userkey:
          - key: 'backupkey'
          - environment: 'hana01:30013'
          - user: 'SYSTEM'
          - password: 'Qwerty1234'
          - database: 'SYSTEMDB'
'''


# Import python libs
from __future__ import absolute_import, unicode_literals, print_function


# Import salt libs
from salt import exceptions
from salt.ext import six

__virtualname__ = 'hana'


def __virtual__():
    '''
    Only load if the hana module is in __salt__
    '''
    if 'hana.is_installed' in __salt__:
        return __virtualname__
    return False


def _parse_dict(dict_params):
    '''
    Get dictionary type variable from sls list type
    '''
    output = {}
    for item in dict_params:
        for key, value in item.items():
            output[key] = value
    return output


def primary_enabled(name, sid, inst, password, **kwargs):
    '''
    Set the node as a primary hana node and in running state

    name
        The name of the primary node
    sid
        System id of the installed hana platform
    inst:
        Instance number of the installed hana platform
    password:
        Password of the installed hana platform user
    backup (optional):
        Create a new backup of the current database
        user:
            Database user
        password:
            Database user password
        database:
            Database name to backup
        file:
            Backup file name
    userkey (optional):
        Create a new key user
        key (str):
            Key name
        environment:
            Database location (host:port)
        user:
            User name
        user_password:
            User password
        database (optional):
            Database name in MDC environment
    '''

    ret = {'name': name,
           'changes': {},
           'result': False,
           'comment': ''}

    if not __salt__['hana.is_installed'](sid, inst, password):
        ret['comment'] = 'HANA is not installed properly with the provided data'
        return ret

    current_state = __salt__['hana.get_sr_state'](sid, inst, password)
    running = __salt__['hana.is_running'](sid, inst, password)
    #  Improve that comparison
    if running and current_state.value == 1:
        ret['result'] = True
        ret['comment'] = 'HANA node already set as primary and running'
        return ret

    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = '{} would be enabled as a primary node'.format(name)
        ret['changes']['primary'] = name
        ret['changes']['backup'] = kwargs.get('backup', False)
        ret['changes']['userkey'] = kwargs.get('userkey', False)
        return ret

    try:
        #  Here starts the actual process
        if not running:
            __salt__['hana.start'](sid, inst, password)
            ret['changes']['running'] = True
        if 'userkey' in kwargs:
            userkey_data = _parse_dict(kwargs.get('userkey'))
            __salt__['hana.create_user_key'](
                userkey_data.get('key'),
                userkey_data.get('environment'),
                userkey_data.get('user'),
                userkey_data.get('password'),
                userkey_data.get('database', None),
                sid, inst, password)
            ret['changes']['userkey'] = userkey_data.get('key')
        if 'backup' in kwargs:
            backup_data = _parse_dict(kwargs.get('backup'))
            __salt__['hana.create_backup'](
                backup_data.get('user'),
                backup_data.get('password'),
                backup_data.get('database'),
                backup_data.get('file'),
                sid, inst, password)
            ret['changes']['backup'] = backup_data.get('file')
        __salt__['hana.sr_enable_primary'](name, sid, inst, password)
        new_state = __salt__['hana.get_sr_state'](sid, inst, password)
        ret['comment'] = 'HANA node set as {}'.format(new_state.name)
        ret['result'] = True
        return ret

    except exceptions.CommandExecutionError as err:
        ret['comment'] = six.text_type(err)
        return ret
