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
        cwd='/tmp/swpm_unattended',
        additional_dvds=None,
        ascs_password=None,
        virtual_host_mask=24,
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
        CAUTION: All of the files stored in this path will be removed except the
        start_dir.cd. This folder only will contain temporary files about the installation
    additional_dvds
        Additional folder where to retrieve required software for the installation
    ascs_password (Only used when the Product is ERS.)
        Password of the SAP user in the machine hosting the ASCS instance.
        If it's not set the same password used to install ERS will be used
    virtual_host_mask
        Ip address mask for the virtual address (24 be default)
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
            virtual_host_interface=virtual_host_interface,
            virtual_host_mask=virtual_host_mask)

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
        cwd='/tmp/swpm_unattended',
        additional_dvds=None,
        virtual_host_mask=24):
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
    virtual_host_mask
        Ip address mask for the virtual address (24 be default)
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
            virtual_host_interface=virtual_host_interface,
            virtual_host_mask=virtual_host_mask)

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


def check_instance_present(
            name,
            dispstatus=None,
            virtual_host=None,
            sid=None,
            inst=None,
            password=None):
    '''
    Check if a SAP Netweaver instance is installed among all the nodes

    name:
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
    sap_instance = name

    ret = {'name': sap_instance,
           'changes': {},
           'result': False,
           'comment': ''}

    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = 'Netweaver instance {} presence would be checked'.format(sap_instance)
        return ret

    try:
        data = __salt__['netweaver.is_instance_installed'](
            sap_instance=sap_instance,
            dispstatus=dispstatus,
            virtual_host=virtual_host,
            sid=sid,
            inst=inst,
            password=password)

        if not data:
            ret['comment'] = 'Netweaver instance {} is not present'.format(sap_instance)
            return ret

        ret['comment'] = 'Netweaver instance {} present in {}'.format(
            sap_instance, data['hostname'])
        ret['result'] = True
        return ret

    except exceptions.CommandExecutionError as err:
        ret['comment'] = six.text_type(err)
        return ret


def sapservices_updated(
        name,
        sid=None,
        inst=None,
        password=None):
    '''
    Update the file /usr/sap/sapservices to include the other sap instances data. This method
    is used to enable HA in Netweaver.
    Both ASCS and ERS must be running.

    sap_instance
        Current node sap instance. If the current node sap instance is 'ascs' it will include 'ers'
        data, and if current node sap instance is 'ers' it will include 'ascs' data.
    sid
        Netweaver system id (PRD for example)
    inst
        Netweaver instance number (00 for example)
    password
        Netweaver instance password
    '''
    sap_instance = name

    ret = {'name': sap_instance,
           'changes': {},
           'result': False,
           'comment': ''}

    sapservice_file = '/usr/sap/sapservices'

    if sap_instance not in ['ascs', 'ers']:
        ret['comment'] = 'invalid sap_instance. Only \'ascs\' and \'ers\' are valid options'
        return ret

    if not __salt__['cmd.retcode']('cat {} | grep \'.*{}.*\''.format(
            sapservice_file, 'ASCS' if sap_instance == 'ers' else 'ERS'), python_shell=True):
        ret['result'] = True
        ret['comment'] = 'sapservices file is already updated for instance {}'.format(sap_instance)
        return ret

    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = 'sapservices of the instance {} would be updated'.format(sap_instance)
        ret['changes']['sap_instance'] = sap_instance
        return ret

    try:
        if sap_instance == 'ascs':
            data = __salt__['netweaver.is_instance_installed'](
                sap_instance='ENQREP', sid=sid, inst=inst, password=password)
        else:
            data = __salt__['netweaver.is_instance_installed'](
                sap_instance='MESSAGESERVER', sid=sid, inst=inst, password=password)

        if not data:
            ret['comment'] = \
                'the required sap instances to make these changes are not installed or running'
            return ret

        new_profile = \
            'LD_LIBRARY_PATH=/usr/sap/{sid}/{sap_instance}{instance}/exe:$LD_LIBRARY_PATH; '\
            'export LD_LIBRARY_PATH; /usr/sap/{sid}/{sap_instance}{instance}/exe/sapstartsrv '\
            'pf=/usr/sap/{sid}/SYS/profile/{sid}_{sap_instance}{instance}_{virtual_host} '\
            '-D -u {sid_lower}adm'.format(
                sid=sid.upper(),
                sap_instance='ASCS' if sap_instance == 'ers' else 'ERS',
                instance='{:0>2}'.format(data['instance']),
                virtual_host=data['hostname'],
                sid_lower=sid)

        __states__['file.append'](
            name=sapservice_file,
            text=new_profile
        )

        ret['comment'] = '{} file updated properly'.format(sapservice_file)
        ret['changes']['sap_instance'] = sap_instance
        ret['changes']['profile'] = new_profile
        ret['result'] = True
        return ret

    except exceptions.CommandExecutionError as err:
        ret['comment'] = six.text_type(err)
        return ret


def ensa_version_grains_present(
        name,
        sid=None,
        inst=None,
        password=None):
    '''
    Set the `ensa_version_{sid}_{inst}` grain with the currently installed ENSA version

    name (sap_instance)
        Check for specific SAP instances. Available options: ascs, ers.
    sid
        Netweaver system id (PRD for example)
    inst
        Netweaver instance number (00 for example)
    password
        Netweaver instance password
    '''

    sap_instance = name
    inst = '{:0>2}'.format(inst)

    changes = {}
    ret = {'name': name,
           'changes': changes,
           'result': False,
           'comment': ''}

    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = 'ENSA version grain would be set'
        ret['changes'] = changes
        return ret

    try:
        ensa_version = __salt__['netweaver.get_ensa_version'](
            sap_instance, sid, inst, password)
    except exceptions.CommandExecutionError as err:
        ret['comment'] = six.text_type(err)
        return ret

    grain_key = 'ensa_version_{}_{}'.format(sid, inst)
    __salt__['grains.set'](grain_key, ensa_version)
    changes[grain_key] = ensa_version

    ret['changes'] = changes
    ret['comment'] = 'ENSA version grain set'
    ret['result'] = True
    return ret
