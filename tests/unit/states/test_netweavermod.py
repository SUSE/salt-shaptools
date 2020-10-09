
# -*- coding: utf-8 -*-
'''
    :codeauthor: Xabier Arbulu Insausti <xarbulu@suse.com>
'''
# Import Python libs
from __future__ import absolute_import, unicode_literals, print_function

from salt import exceptions

# Import Salt Testing Libs
from tests.support.mixins import LoaderModuleMockMixin
from tests.support.unit import skipIf, TestCase
from tests.support import mock
from tests.support.mock import (
    MagicMock,
    patch
)

# Import Salt Libs
import salt.states.netweavermod as netweavermod


class NetweavermodTestCase(TestCase, LoaderModuleMockMixin):
    '''
    Test cases for salt.states.netweavermod
    '''
    def setup_loader_modules(self):
        return {netweavermod: {'__opts__': {'test': False}}}

    def test_get_sap_instance_type(self):
        ret = netweavermod._get_sap_instance_type('NW_ABAP_ASCS:NW750.HDB.ABAPHA')
        assert ret == 'ascs'

        ret = netweavermod._get_sap_instance_type('NW_ERS:NW750.HDB.ABAPHA')
        assert ret == 'ers'

    # 'installed' function tests

    @mock.patch('salt.states.netweavermod._get_sap_instance_type')
    def test_installed_installed(self, mock_get):
        '''
        Test to check installed when netweaver is already installed
        '''

        ret = {'name': 'prd',
               'changes': {},
               'result': True,
               'comment': 'Netweaver ascs is already installed'}

        mock_installed = MagicMock(return_value=True)
        mock_get.return_value = 'ascs'
        with patch.dict(netweavermod.__salt__, {'netweaver.is_installed': mock_installed}):
            assert netweavermod.installed(
                'prd', '00', 'pass', '/software', 'root', 'pass',
                'config_file', 'vhost', 'eth1', 'productID') == ret
            mock_installed.assert_called_once_with(
                sid='prd', inst='00', password='pass', sap_instance='ascs')
            mock_get.assert_called_once_with('productID')

    @mock.patch('salt.states.netweavermod._get_sap_instance_type')
    def test_installed_test(self, mock_get):
        '''
        Test to check installed in test mode
        '''

        ret = {'name': 'prd',
               'changes': {'sid': 'prd'},
               'result': None,
               'comment': '{}:ascs would be installed'.format('prd')}

        mock_installed = MagicMock(return_value=False)
        mock_get.return_value = 'ascs'
        with patch.dict(netweavermod.__salt__, {'netweaver.is_installed': mock_installed}):
            with patch.dict(netweavermod.__opts__, {'test': True}):
                assert netweavermod.installed(
                    'prd', '00', 'pass', '/software', 'root', 'pass',
                    'config_file', 'vhost', 'eth1', 'productID') == ret
            mock_installed.assert_called_once_with(
                sid='prd', inst='00', password='pass', sap_instance='ascs')
            mock_get.assert_called_once_with('productID')

    @mock.patch('salt.states.netweavermod._get_sap_instance_type')
    def test_installed_command_error(self, mock_get):
        '''
        Test to check installed when it raises an error
        '''

        ret = {'name': 'prd',
               'changes': {},
               'result': False,
               'comment': 'error'}

        mock_installed = MagicMock(return_value=False)
        mock_get.return_value = 'ascs'
        mock_attach = MagicMock(side_effect=exceptions.CommandExecutionError('error'))
        with patch.dict(netweavermod.__salt__, {'netweaver.is_installed': mock_installed,
                                                'netweaver.attach_virtual_host': mock_attach}):
            assert netweavermod.installed(
                'prd', '00', 'pass', '/software', 'root', 'pass',
                'config_file', 'vhost', 'eth1', 'productID') == ret
            mock_installed.assert_called_once_with(
                sid='prd', inst='00', password='pass', sap_instance='ascs')
            mock_get.assert_called_once_with('productID')
            mock_attach.assert_called_once_with(
                virtual_host='vhost', virtual_host_interface='eth1', virtual_host_mask=24)

    @mock.patch('salt.states.netweavermod._get_sap_instance_type')
    def test_installed_correct(self, mock_get):
        '''
        Test to check installed when it is installed correctly
        '''

        ret = {'name': 'prd',
               'changes': {'sid': 'prd'},
               'result': True,
               'comment': 'Netweaver di installed'}

        mock_installed = MagicMock(side_effect=[False, True])
        mock_get.return_value = 'di'
        mock_attach = MagicMock(return_value='192.168.15.1')
        mock_setup_cwd = MagicMock(return_value='/tmp_nw')
        mock_install = MagicMock()
        mock_chown = MagicMock()
        with patch.dict(netweavermod.__salt__, {'netweaver.is_installed': mock_installed,
                                                'netweaver.attach_virtual_host': mock_attach,
                                                'netweaver.setup_cwd': mock_setup_cwd,
                                                'netweaver.install': mock_install,
                                                'file.chown': mock_chown}):
            assert netweavermod.installed(
                'prd', '00', 'pass', '/software', 'root', 'pass',
                'config_file', 'vhost', 'eth1', 'productID',
                cwd='/tmp', virtual_host_mask=32) == ret
            mock_installed.assert_has_calls([
                mock.call(sid='prd', inst='00', password='pass', sap_instance='di'),
                mock.call(sid='prd', inst='00', password='pass', sap_instance='di'),
            ])

            mock_get.assert_called_once_with('productID')
            mock_attach.assert_called_once_with(
                virtual_host='vhost', virtual_host_interface='eth1', virtual_host_mask=32)
            mock_setup_cwd.assert_called_once_with(
                software_path='/software', cwd='/tmp', additional_dvds=None)
            mock_install.assert_called_once_with(
                software_path='/software', virtual_host='vhost',
                product_id='productID', conf_file='config_file',
                root_user='root', root_password='pass', cwd='/tmp_nw')

    @mock.patch('salt.states.netweavermod._get_sap_instance_type')
    def test_installed_ers_correct(self, mock_get):
        '''
        Test to check installed when ers is installed correctly
        '''

        ret = {'name': 'prd',
               'changes': {'sid': 'prd'},
               'result': True,
               'comment': 'Netweaver ers installed'}

        mock_installed = MagicMock(side_effect=[False, True])
        mock_get.return_value = 'ers'
        mock_attach = MagicMock(return_value='192.168.15.1')
        mock_setup_cwd = MagicMock(return_value='/tmp_nw')
        mock_install = MagicMock()
        mock_chown = MagicMock()
        with patch.dict(netweavermod.__salt__, {'netweaver.is_installed': mock_installed,
                                                'netweaver.attach_virtual_host': mock_attach,
                                                'netweaver.setup_cwd': mock_setup_cwd,
                                                'netweaver.install_ers': mock_install,
                                                'file.chown': mock_chown}):
            assert netweavermod.installed(
                'prd', '00', 'pass', '/software', 'root', 'pass',
                'config_file', 'vhost', 'eth1', 'productID', ascs_password='ascs_pass') == ret
            mock_installed.assert_has_calls([
                mock.call(sid='prd', inst='00', password='pass', sap_instance='ers'),
                mock.call(sid='prd', inst='00', password='pass', sap_instance='ers'),
            ])

            assert mock_chown.call_count == 0
            mock_get.assert_called_once_with('productID')
            mock_attach.assert_called_once_with(
                virtual_host='vhost', virtual_host_interface='eth1', virtual_host_mask=24)
            mock_setup_cwd.assert_called_once_with(
                software_path='/software', cwd='/tmp/swpm_unattended', additional_dvds=None)
            mock_install.assert_called_once_with(
                software_path='/software', virtual_host='vhost',
                product_id='productID', conf_file='config_file',
                root_user='root', root_password='pass',
                cwd='/tmp_nw', ascs_password='ascs_pass', timeout=0, interval=5)

    @mock.patch('salt.states.netweavermod._get_sap_instance_type')
    def test_installed_not_installed(self, mock_get):
        '''
        Test to check installed when the installation fails
        '''

        ret = {'name': 'prd',
               'changes': {},
               'result': False,
               'comment': 'Netweaver was not installed'}

        mock_installed = MagicMock(side_effect=[False, False])
        mock_get.return_value = ''
        mock_attach = MagicMock(return_value='192.168.15.1')
        mock_setup_cwd = MagicMock(return_value='/tmp_nw')
        mock_install = MagicMock()
        with patch.dict(netweavermod.__salt__, {'netweaver.is_installed': mock_installed,
                                                'netweaver.attach_virtual_host': mock_attach,
                                                'netweaver.setup_cwd': mock_setup_cwd,
                                                'netweaver.install': mock_install}):
            assert netweavermod.installed(
                'prd', '00', 'pass', '/software', 'root', 'pass',
                'config_file', 'vhost', 'eth1', 'productID') == ret
            mock_installed.assert_has_calls([
                mock.call(sid='prd', inst='00', password='pass', sap_instance=''),
                mock.call(sid='prd', inst='00', password='pass', sap_instance=''),
            ])

            mock_get.assert_called_once_with('productID')
            mock_attach.assert_called_once_with(
                virtual_host='vhost', virtual_host_interface='eth1', virtual_host_mask=24)
            mock_setup_cwd.assert_called_once_with(
                software_path='/software', cwd='/tmp/swpm_unattended', additional_dvds=None)
            mock_install.assert_called_once_with(
                software_path='/software', virtual_host='vhost',
                product_id='productID', conf_file='config_file',
                root_user='root', root_password='pass', cwd='/tmp_nw')

    # 'db_installed' function tests

    def test_db_installed_installed(self):
        '''
        Test to check db installed when netweaver is already installed
        '''

        ret = {'name': '192.168.10.15:30015',
               'changes': {},
               'result': True,
               'comment': 'Netweaver DB instance is already installed'}

        mock_db_installed = MagicMock(return_value=True)
        with patch.dict(netweavermod.__salt__, {'netweaver.is_db_installed': mock_db_installed}):
            assert netweavermod.db_installed(
                '192.168.10.15', 30015, 'SAPABAP1', 'schema_pass',
                '/software', 'root', 'pass',
                'config_file', 'vhost', 'eth1', 'productID') == ret
            mock_db_installed.assert_called_once_with(
                host='192.168.10.15', port=30015, schema_name='SAPABAP1', schema_password='schema_pass')

    def test_db_installed_test(self):
        '''
        Test to check db_installed in test mode
        '''

        ret = {'name': '192.168.10.15:30015',
               'changes': {'host': '192.168.10.15:30015'},
               'result': None,
               'comment': 'Netweaver DB instance would be installed'}

        mock_db_installed = MagicMock(return_value=False)
        with patch.dict(netweavermod.__salt__, {'netweaver.is_db_installed': mock_db_installed}):
            with patch.dict(netweavermod.__opts__, {'test': True}):
                assert netweavermod.db_installed(
                    '192.168.10.15', 30015, 'SAPABAP1', 'schema_pass',
                    '/software', 'root', 'pass',
                    'config_file', 'vhost', 'eth1', 'productID') == ret
            mock_db_installed.assert_called_once_with(
                host='192.168.10.15', port=30015, schema_name='SAPABAP1', schema_password='schema_pass')

    def test_db_installed_command_error(self):
        '''
        Test to check db_installed when it raises an error
        '''

        ret = {'name': '192.168.10.15:30015',
               'changes': {},
               'result': False,
               'comment': 'error'}

        mock_db_installed = MagicMock(return_value=False)
        mock_attach = MagicMock(side_effect=exceptions.CommandExecutionError('error'))
        with patch.dict(netweavermod.__salt__, {'netweaver.is_db_installed': mock_db_installed,
                                                'netweaver.attach_virtual_host': mock_attach}):
            assert netweavermod.db_installed(
                '192.168.10.15', 30015, 'SAPABAP1', 'schema_pass',
                '/software', 'root', 'pass',
                'config_file', 'vhost', 'eth1', 'productID') == ret
            mock_db_installed.assert_called_once_with(
                host='192.168.10.15', port=30015, schema_name='SAPABAP1', schema_password='schema_pass')
            mock_attach.assert_called_once_with(
                virtual_host='vhost', virtual_host_interface='eth1', virtual_host_mask=24)

    def test_db_installed_correct(self):
        '''
        Test to check installed when it is installed correctly
        '''

        ret = {'name': '192.168.10.15:30015',
               'changes': {'host': '192.168.10.15:30015'},
               'result': True,
               'comment': 'Netweaver DB instance installed'}

        mock_db_installed = MagicMock(side_effect=[False, True])
        mock_attach = MagicMock(return_value='192.168.15.1')
        mock_setup_cwd = MagicMock(return_value='/tmp_nw')
        mock_install = MagicMock()
        with patch.dict(netweavermod.__salt__, {'netweaver.is_db_installed': mock_db_installed,
                                                'netweaver.attach_virtual_host': mock_attach,
                                                'netweaver.setup_cwd': mock_setup_cwd,
                                                'netweaver.install': mock_install}):
            assert netweavermod.db_installed(
                '192.168.10.15', 30015, 'SAPABAP1', 'schema_pass',
                '/software', 'root', 'pass',
                'config_file', 'vhost', 'eth1', 'productID', virtual_host_mask=32) == ret
            mock_db_installed.assert_has_calls([
                mock.call(
                    host='192.168.10.15', port=30015,
                    schema_name='SAPABAP1', schema_password='schema_pass'),
                mock.call(
                    host='192.168.10.15', port=30015,
                    schema_name='SAPABAP1', schema_password='schema_pass'),
            ])

            mock_attach.assert_called_once_with(
                virtual_host='vhost', virtual_host_interface='eth1', virtual_host_mask=32)
            mock_setup_cwd.assert_called_once_with(
                software_path='/software', cwd='/tmp/swpm_unattended', additional_dvds=None)
            mock_install.assert_called_once_with(
                software_path='/software', virtual_host='vhost',
                product_id='productID', conf_file='config_file',
                root_user='root', root_password='pass', cwd='/tmp_nw')

    def test_db_installed_not_installed(self):
        '''
        Test to check installed when the installation fails
        '''

        ret = {'name': '192.168.10.15:30015',
               'changes': {},
               'result': False,
               'comment': 'Netweaver DB instance was not installed'}

        mock_db_installed = MagicMock(side_effect=[False, False])
        mock_attach = MagicMock(return_value='192.168.15.1')
        mock_setup_cwd = MagicMock(return_value='/tmp_nw')
        mock_install = MagicMock()
        with patch.dict(netweavermod.__salt__, {'netweaver.is_db_installed': mock_db_installed,
                                                'netweaver.attach_virtual_host': mock_attach,
                                                'netweaver.setup_cwd': mock_setup_cwd,
                                                'netweaver.install': mock_install}):
            assert netweavermod.db_installed(
                '192.168.10.15', 30015, 'SAPABAP1', 'schema_pass',
                '/software', 'root', 'pass',
                'config_file', 'vhost', 'eth1', 'productID') == ret
            mock_db_installed.assert_has_calls([
                mock.call(
                    host='192.168.10.15', port=30015,
                    schema_name='SAPABAP1', schema_password='schema_pass'),
                mock.call(
                    host='192.168.10.15', port=30015,
                    schema_name='SAPABAP1', schema_password='schema_pass'),
            ])

            mock_attach.assert_called_once_with(
                virtual_host='vhost', virtual_host_interface='eth1', virtual_host_mask=24)
            mock_setup_cwd.assert_called_once_with(
                software_path='/software', cwd='/tmp/swpm_unattended', additional_dvds=None)
            mock_install.assert_called_once_with(
                software_path='/software', virtual_host='vhost',
                product_id='productID', conf_file='config_file',
                root_user='root', root_password='pass', cwd='/tmp_nw')

    def test_check_instance_present_test(self):
        '''
        Test check_instance_present in test mode
        '''

        ret = {'name': 'MESSAGESERVER',
               'changes': {},
               'result': None,
               'comment': 'Netweaver instance MESSAGESERVER presence would be checked'}

        mock_is_instance_installed = MagicMock(return_value=False)
        with patch.dict(netweavermod.__salt__, {'netweaver.is_instance_installed': mock_is_instance_installed}):
            with patch.dict(netweavermod.__opts__, {'test': True}):
                assert netweavermod.check_instance_present(
                    'MESSAGESERVER', 'GREEN', 'virtual',
                    'prd', 00, 'pass') == ret

    def test_check_instance_present_command_error(self):
        '''
        Test to check check_instance_present when it raises an error
        '''

        ret = {'name': 'MESSAGESERVER',
               'changes': {},
               'result': False,
               'comment': 'error'}

        mock_is_instance_installed = MagicMock(side_effect=exceptions.CommandExecutionError('error'))
        with patch.dict(netweavermod.__salt__, {'netweaver.is_instance_installed': mock_is_instance_installed}):
            assert netweavermod.check_instance_present(
                'MESSAGESERVER', 'GREEN', 'virtual',
                'prd', 00, 'pass') == ret

        mock_is_instance_installed.assert_called_once_with(
            sap_instance='MESSAGESERVER',
            dispstatus='GREEN',
            virtual_host='virtual',
            sid='prd',
            inst=00,
            password='pass')

    def test_check_instance_not_present(self):
        '''
        Test to check check_instance_present when the instance is not present
        '''

        ret = {'name': 'MESSAGESERVER',
               'changes': {},
               'result': False,
               'comment': 'Netweaver instance MESSAGESERVER is not present'}

        mock_is_instance_installed = MagicMock(return_value=False)
        with patch.dict(netweavermod.__salt__, {'netweaver.is_instance_installed': mock_is_instance_installed}):
            assert netweavermod.check_instance_present(
                'MESSAGESERVER', 'GREEN', 'virtual',
                'prd', 00, 'pass') == ret

        mock_is_instance_installed.assert_called_once_with(
            sap_instance='MESSAGESERVER',
            dispstatus='GREEN',
            virtual_host='virtual',
            sid='prd',
            inst=00,
            password='pass')

    def test_check_instance_present(self):
        '''
        Test to check check_instance_present when the instance is present
        '''

        ret = {'name': 'MESSAGESERVER',
               'changes': {},
               'result': True,
               'comment': 'Netweaver instance MESSAGESERVER present in virtualhost'}

        mock_is_instance_installed = MagicMock(return_value={'hostname': 'virtualhost'})
        with patch.dict(netweavermod.__salt__, {'netweaver.is_instance_installed': mock_is_instance_installed}):
            assert netweavermod.check_instance_present(
                'MESSAGESERVER', 'GREEN', 'virtual',
                'prd', 00, 'pass') == ret

        mock_is_instance_installed.assert_called_once_with(
            sap_instance='MESSAGESERVER',
            dispstatus='GREEN',
            virtual_host='virtual',
            sid='prd',
            inst=00,
            password='pass')

    def test_sapservices_updated_invalid_instance(self):
        '''
        Test sapservices_updated when the instance is invalid
        '''

        ret = {'name': 'other',
               'changes': {},
               'result': False,
               'comment': 'invalid sap_instance. Only \'ascs\' and \'ers\' are valid options'}

        assert netweavermod.sapservices_updated(
            'other', 'prd', 00, 'pass') == ret

    def test_sapservices_updated_already_update(self):
        '''
        Test sapservices_updated when the sapservice file is already updated
        '''

        ret = {'name': 'ascs',
               'changes': {},
               'result': True,
               'comment': 'sapservices file is already updated for instance ascs'}

        mock_retcode = MagicMock(return_value=0)
        with patch.dict(netweavermod.__salt__, {'cmd.retcode': mock_retcode}):
            assert netweavermod.sapservices_updated(
                'ascs', 'prd', 00, 'pass') == ret

        mock_retcode.assert_called_once_with(
            'cat /usr/sap/sapservices | grep \'.*ERS.*\'', python_shell=True)

        ret = {'name': 'ers',
               'changes': {},
               'result': True,
               'comment': 'sapservices file is already updated for instance ers'}

        mock_retcode = MagicMock(return_value=0)
        with patch.dict(netweavermod.__salt__, {'cmd.retcode': mock_retcode}):
            assert netweavermod.sapservices_updated(
                'ers', 'prd', 00, 'pass') == ret

        mock_retcode.assert_called_once_with(
            'cat /usr/sap/sapservices | grep \'.*ASCS.*\'', python_shell=True)

    def test_sapservices_updated_test(self):
        '''
        Test sapservices_updated using test mode
        '''

        ret = {'name': 'ascs',
               'changes': {'sap_instance': 'ascs'},
               'result': None,
               'comment': 'sapservices of the instance ascs would be updated'}

        mock_retcode = MagicMock(return_value=1)
        with patch.dict(netweavermod.__salt__, {'cmd.retcode': mock_retcode}):
            with patch.dict(netweavermod.__opts__, {'test': True}):
                assert netweavermod.sapservices_updated(
                    'ascs', 'prd', 00, 'pass') == ret

        mock_retcode.assert_called_once_with(
            'cat /usr/sap/sapservices | grep \'.*ERS.*\'', python_shell=True)

    def test_sapservices_updated_correct(self):
        '''
        Test sapservices_updated when it is done correctly
        '''

        new_profile = 'LD_LIBRARY_PATH=/usr/sap/PRD/ERS10/exe:$LD_LIBRARY_PATH; '\
        'export LD_LIBRARY_PATH; /usr/sap/PRD/ERS10/exe/sapstartsrv '\
        'pf=/usr/sap/PRD/SYS/profile/PRD_ERS10_virtual '\
        '-D -u prdadm'

        ret = {'name': 'ascs',
               'changes': {'sap_instance': 'ascs', 'profile': new_profile},
               'result': True,
               'comment': '/usr/sap/sapservices file updated properly'}

        mock_retcode = MagicMock(return_value=1)
        mock_is_installed = MagicMock(return_value={'hostname': 'virtual', 'instance': 10})
        mock_append = MagicMock()
        with patch.dict(netweavermod.__salt__, {'netweaver.is_instance_installed': mock_is_installed,
                                                'cmd.retcode': mock_retcode}):
            with patch.dict(netweavermod.__states__, {'file.append': mock_append}):
                assert netweavermod.sapservices_updated(
                    'ascs', 'prd', 00, 'pass') == ret

        mock_retcode.assert_called_once_with(
            'cat /usr/sap/sapservices | grep \'.*ERS.*\'', python_shell=True)
        mock_is_installed.assert_called_once_with(
            sap_instance='ENQREP', sid='prd', inst=00, password='pass')
        mock_append.assert_called_once_with(name='/usr/sap/sapservices', text=new_profile)

        new_profile = 'LD_LIBRARY_PATH=/usr/sap/PRD/ASCS00/exe:$LD_LIBRARY_PATH; '\
            'export LD_LIBRARY_PATH; /usr/sap/PRD/ASCS00/exe/sapstartsrv '\
            'pf=/usr/sap/PRD/SYS/profile/PRD_ASCS00_virtual '\
            '-D -u prdadm'

        ret = {'name': 'ers',
               'changes': {'sap_instance': 'ers', 'profile': new_profile},
               'result': True,
               'comment': '/usr/sap/sapservices file updated properly'}

        mock_retcode = MagicMock(return_value=1)
        mock_is_installed = MagicMock(return_value={'hostname': 'virtual', 'instance': 00})
        mock_append = MagicMock()
        with patch.dict(netweavermod.__salt__, {'netweaver.is_instance_installed': mock_is_installed,
                                                'cmd.retcode': mock_retcode}):
            with patch.dict(netweavermod.__states__, {'file.append': mock_append}):
                assert netweavermod.sapservices_updated(
                    'ers', 'prd', 10, 'pass') == ret

        mock_retcode.assert_called_once_with(
            'cat /usr/sap/sapservices | grep \'.*ASCS.*\'', python_shell=True)
        mock_is_installed.assert_called_once_with(
            sap_instance='MESSAGESERVER', sid='prd', inst=10, password='pass')
        mock_append.assert_called_once_with(name='/usr/sap/sapservices', text=new_profile)

    def test_sapservices_updated_no_data(self):
        '''
        Test sapservices_updated when the instance is not found
        '''

        ret = {'name': 'ascs',
               'changes': {},
               'result': False,
               'comment': 'the required sap instances to make these changes are not installed or running'}

        mock_retcode = MagicMock(return_value=1)
        mock_is_installed = MagicMock(return_value=False)
        with patch.dict(netweavermod.__salt__, {'netweaver.is_instance_installed': mock_is_installed,
                                                'cmd.retcode': mock_retcode}):
            assert netweavermod.sapservices_updated(
                'ascs', 'prd', 00, 'pass') == ret

        mock_retcode.assert_called_once_with(
            'cat /usr/sap/sapservices | grep \'.*ERS.*\'', python_shell=True)
        mock_is_installed.assert_called_once_with(
            sap_instance='ENQREP', sid='prd', inst=00, password='pass')

    def test_sapservices_updated_error(self):
        '''
        Test sapservices_updated when the there is an execution error
        '''

        ret = {'name': 'ascs',
               'changes': {},
               'result': False,
               'comment': 'error'}

        mock_retcode = MagicMock(return_value=1)
        mock_is_installed = MagicMock(side_effect=exceptions.CommandExecutionError('error'))
        with patch.dict(netweavermod.__salt__, {'netweaver.is_instance_installed': mock_is_installed,
                                                'cmd.retcode': mock_retcode}):
            assert netweavermod.sapservices_updated(
                'ascs', 'prd', 00, 'pass') == ret

        mock_retcode.assert_called_once_with(
            'cat /usr/sap/sapservices | grep \'.*ERS.*\'', python_shell=True)
        mock_is_installed.assert_called_once_with(
            sap_instance='ENQREP', sid='prd', inst=00, password='pass')

    def test_ensa_version_grains_present_test(self):
        '''
        Test ensa_version_grains_present using test mode
        '''

        ret = {'name': 'ascs',
               'changes': {},
               'result': None,
               'comment': 'ENSA version grain would be set'}

        with patch.dict(netweavermod.__opts__, {'test': True}):
            assert netweavermod.ensa_version_grains_present(
                'ascs', 'prd', 00, 'pass') == ret

    def test_ensa_version_grains_present_error(self):
        '''
        Test ensa_version_grains_present with the error
        '''

        ret = {'name': 'ascs',
               'changes': {},
               'result': False,
               'comment': 'err'}

        mock_get_ensa_version = mock.Mock(side_effect=exceptions.CommandExecutionError('err'))

        with patch.dict(netweavermod.__salt__, {
                'netweaver.get_ensa_version': mock_get_ensa_version}):
            assert netweavermod.ensa_version_grains_present(
                'ascs', 'prd', 00, 'pass') == ret

    def test_ensa_version_grains_present(self):
        '''
        Test ensa_version_grains_present with correct execution
        '''

        ret = {'name': 'ascs',
               'changes': {'ensa_version_prd_00': 1},
               'result': True,
               'comment': 'ENSA version grain set'}

        mock_get_ensa_version = mock.Mock(return_value=1)
        mock_grains_set = mock.Mock()

        with patch.dict(netweavermod.__salt__, {
                'netweaver.get_ensa_version': mock_get_ensa_version,
                'grains.set': mock_grains_set}):
            assert netweavermod.ensa_version_grains_present(
                'ascs', 'prd', '00', 'pass') == ret
        mock_grains_set.assert_called_once_with('ensa_version_prd_00', 1)

        mock_grains_set.reset_mock()

        with patch.dict(netweavermod.__salt__, {
                'netweaver.get_ensa_version': mock_get_ensa_version,
                'grains.set': mock_grains_set}):
            assert netweavermod.ensa_version_grains_present(
                'ascs', 'prd', 0, 'pass') == ret
        mock_grains_set.assert_called_once_with('ensa_version_prd_00', 1)
