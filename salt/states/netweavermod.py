# -*- coding: utf-8 -*-
'''
State module to provide SAP Netweaver functionality to Salt

.. versionadded:: pending

:maintainer:    Xabier Arbulu Insausti <xarbulu@suse.com>
:maturity:      alpha
:depends:       python-shaptools
:platform:      all

:configuration: This module requires the python-shaptools module and uses the
    following defaults which may be overridden in the minion configuration:

.. code-block:: yaml

    netweaver.sid: 'prd'
    netweaver.inst: '00'
    netweaver.password: 'Qwerty1234'

:usage:

.. code-block:: yaml
    my_netweaver_instance:
      netweaver.installed:
      - name: ha1
      - instance: '00'
      - password: Qwerty1234
      - software_path: /swpm
      - root_user: root
      - root_password: linux
      - config_file: /inifile.params
      - virtual_host: ha1virthost
      - virtual_host_interface: eth1
      - product_id: NW_ABAP_ASCS:NW750.HDB.ABAPHA
'''

# Import python libs
from __future__ import absolute_import, unicode_literals, print_function

# Import salt libs
from salt import exceptions
from salt.ext import six


__virtualname__ = 'netweaver'


def __virtual__():  # pragma: no cover
    '''
    Only load if the netweaver module is in __salt__
    '''
    return 'netweaver.is_installed' in __salt__


def _get_sap_instance_type(product_id):
    '''
    Get SAP instance type from the product id string
    '''
    return product_id.split(':')[0].split('_')[-1].lower()


def installed(
        name,
        inst,
        password,
        software_path,
        root_user,
        root_password,
        config_file,
        virtual_host,
        virtual_host_interface,
        product_id,
        cwd='/tmp/unattended',
        additional_dvds=None,
        ascs_password=None,
        timeout=0,
        interval=5):
    """
    Install SAP Netweaver instance if the instance is not installed yet.

    name
        System id of the installed netweaver platform
    inst
        Instance number of the installed netweaver platform
    password
        Password of the installed netweaver platform user
    software_path:
        Path where the SAP NETWEAVER software is downloaded, it must be located in
        the minion itself
    root_user
        Root user name
    root_password
        Root user password
    config_file
        inifile.params type configuration file. It must match with the used product id
    virtual_host
        Virtual host associated to the SAP instance
    virtual_host_interface:
        Network interface to attach the virtual host ip address
    product_id
        Id of the product to be installed. Example: NW_ABAP_ASCS:NW750.HDB.ABAPHA
    cwd
        New value for SAPINST_CWD parameter
    additional_dvds
        Additional folder where to retrieve required software for the installation
    ascs_password (Only used when the Product is ERS.)
        Password of the SAP user in the machine hosting the ASCS instance.
        If it's not set the same password used to install ERS will be used
    timeout (Only used when the Product is ERS.)
        Timeout of the installation process. If 0 it will try to install the instance only once
    interval (Only used when the Product is ERS.)
        Retry interval in seconds
    """
    sid = name
    sap_instance = _get_sap_instance_type(product_id)

    ret = {'name': sid,
           'changes': {},
           'result': False,
           'comment': ''}

    if __salt__['netweaver.is_installed'](
            sid=sid,
            inst=inst,
            password=password,
            sap_instance=sap_instance):
        ret['result'] = True
        ret['comment'] = 'Netweaver{} is already installed'.format(
            ' {}'.format(sap_instance) if sap_instance else '')
        return ret

    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = '{}{} would be installed'.format(
            sid, ':{}'.format(sap_instance) if sap_instance else '')
        ret['changes']['sid'] = sid
        return ret

    try:
        #  Here starts the actual process
        __salt__['netweaver.attach_virtual_host'](
            virtual_host=virtual_host,
            virtual_host_interface=virtual_host_interface)

        if cwd:
            cwd = __salt__['netweaver.setup_cwd'](
                software_path=software_path,
                cwd=cwd,
                additional_dvds=additional_dvds)

        # This state is applied due an error raised during AAS installation saying the permissions
        # to create files inside this folder are not valid
        if sap_instance == 'di':
            __salt__['file.chown'](
                '/usr/sap/{}'.format(sid.upper()), '{}adm'.format(sid.lower()), 'sapsys')

        if sap_instance == 'ers':
            __salt__['netweaver.install_ers'](
                software_path=software_path,
                virtual_host=virtual_host,
                product_id=product_id,
                conf_file=config_file,
                cwd=cwd,
                root_user=root_user,
                root_password=root_password,
                ascs_password=ascs_password,
                timeout=timeout,
                interval=interval)

        else:
            __salt__['netweaver.install'](
                software_path=software_path,
                virtual_host=virtual_host,
                product_id=product_id,
                conf_file=config_file,
                cwd=cwd,
                root_user=root_user,
                root_password=root_password)

        ret['result'] = __salt__['netweaver.is_installed'](
            sid=sid,
            inst=inst,
            password=password,
            sap_instance=sap_instance)

        if ret['result']:
            ret['changes']['sid'] = sid
            ret['comment'] = 'Netweaver{} installed'.format(
                ' {}'.format(sap_instance) if sap_instance else '')
        else:
            ret['comment'] = 'Netweaver{} was not installed'.format(
                ' {}'.format(sap_instance) if sap_instance else '')
        return ret

    except exceptions.CommandExecutionError as err:
        ret['comment'] = six.text_type(err)
        return ret


def db_installed(
        name,
        port,
        schema_name,
        schema_password,
        software_path,
        root_user,
        root_password,
        config_file,
        virtual_host,
        virtual_host_interface,
        product_id,
        cwd='/tmp/unattended',
        additional_dvds=None):
    """
    Install SAP Netweaver DB instance if the instance is not installed yet.

    name
        Host where HANA is running
    port
        HANA database port
    schema_name:
        Schema installed in the dabase
    schema_password:
        Password of the user for the schema
    software_path:
        Path where the SAP NETWEAVER software is downloaded, it must be located in
        the minion itself
    root_user
        Root user name
    root_password
        Root user password
    config_file
        inifile.params type configuration file. It must match with the used product id
    virtual_host
        Virtual host associated to the SAP instance
    virtual_host_interface:
        Network interface to attach the virtual host ip address
    product_id
        Id of the product to be installed. Example: NW_ABAP_ASCS:NW750.HDB.ABAPHA
    cwd
        New value for SAPINST_CWD parameter
    additional_dvds
        Additional folder where to retrieve required software for the installation
    """
    host = name

    ret = {'name': '{}:{}'.format(host, port),
           'changes': {},
           'result': False,
           'comment': ''}

    if __salt__['netweaver.is_db_installed'](
            host=host,
            port=port,
            schema_name=schema_name,
            schema_password=schema_password):
        ret['result'] = True
        ret['comment'] = 'Netweaver DB instance is already installed'
        return ret

    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = 'Netweaver DB instance would be installed'
        ret['changes']['host'] = '{}:{}'.format(host, port)
        return ret

    try:
        #  Here starts the actual process
        __salt__['netweaver.attach_virtual_host'](
            virtual_host=virtual_host,
            virtual_host_interface=virtual_host_interface)

        if cwd:
            cwd = __salt__['netweaver.setup_cwd'](
                software_path=software_path,
                cwd=cwd,
                additional_dvds=additional_dvds)

        __salt__['netweaver.install'](
            software_path=software_path,
            virtual_host=virtual_host,
            product_id=product_id,
            conf_file=config_file,
            cwd=cwd,
            root_user=root_user,
            root_password=root_password)

        ret['result'] = __salt__['netweaver.is_db_installed'](
            host=host,
            port=port,
            schema_name=schema_name,
            schema_password=schema_password)

        if ret['result']:
            ret['changes']['host'] = '{}:{}'.format(host, port)
            ret['comment'] = 'Netweaver DB instance installed'
        else:
            ret['comment'] = 'Netweaver DB instance was not installed'
        return ret

    except exceptions.CommandExecutionError as err:
        ret['comment'] = six.text_type(err)
        return ret
