
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
    NO_MOCK,
    NO_MOCK_REASON,
    MagicMock,
    patch
)

# Import Salt Libs
import salt.states.netweavermod as netweavermod


@skipIf(NO_MOCK, NO_MOCK_REASON)
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
        Test to check installed in test mode
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
                virtual_host='vhost', virtual_host_interface='eth1')

    @mock.patch('salt.states.netweavermod._get_sap_instance_type')
    def test_installed_correct(self, mock_get):
        '''
        Test to check installed in test mode
        '''

        ret = {'name': 'prd',
               'changes': {'sid': 'prd'},
               'result': True,
               'comment': 'Netweaver ascs installed'}

        mock_installed = MagicMock(side_effect=[False, True])
        mock_get.return_value = 'ascs'
        mock_attach = MagicMock(return_value='192.168.15.1')
        mock_setup_cwd = MagicMock(return_value='/tmp_nw')
        mock_install = MagicMock()
        with patch.dict(netweavermod.__salt__, {'netweaver.is_installed': mock_installed,
                                                'netweaver.attach_virtual_host': mock_attach,
                                                'netweaver.setup_cwd': mock_setup_cwd,
                                                'netweaver.install': mock_install}):
            assert netweavermod.installed(
                'prd', '00', 'pass', '/software', 'root', 'pass',
                'config_file', 'vhost', 'eth1', 'productID', cwd='/tmp') == ret
            mock_installed.assert_has_calls([
                mock.call(sid='prd', inst='00', password='pass', sap_instance='ascs'),
                mock.call(sid='prd', inst='00', password='pass', sap_instance='ascs'),
            ])

            mock_get.assert_called_once_with('productID')
            mock_attach.assert_called_once_with(
                virtual_host='vhost', virtual_host_interface='eth1')
            mock_setup_cwd.assert_called_once_with(
                software_path='/software', cwd='/tmp', additional_dvds=None)
            mock_install.assert_called_once_with(
                software_path='/software', virtual_host='vhost',
                product_id='productID', conf_file='config_file',
                root_user='root', root_password='pass', cwd='/tmp_nw')

    @mock.patch('salt.states.netweavermod._get_sap_instance_type')
    def test_installed_ers_correct(self, mock_get):
        '''
        Test to check installed in test mode
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
        with patch.dict(netweavermod.__salt__, {'netweaver.is_installed': mock_installed,
                                                'netweaver.attach_virtual_host': mock_attach,
                                                'netweaver.setup_cwd': mock_setup_cwd,
                                                'netweaver.install_ers': mock_install}):
            assert netweavermod.installed(
                'prd', '00', 'pass', '/software', 'root', 'pass',
                'config_file', 'vhost', 'eth1', 'productID', ascs_password='ascs_pass') == ret
            mock_installed.assert_has_calls([
                mock.call(sid='prd', inst='00', password='pass', sap_instance='ers'),
                mock.call(sid='prd', inst='00', password='pass', sap_instance='ers'),
            ])

            mock_get.assert_called_once_with('productID')
            mock_attach.assert_called_once_with(
                virtual_host='vhost', virtual_host_interface='eth1')
            mock_setup_cwd.assert_called_once_with(
                software_path='/software', cwd='/tmp/unattended', additional_dvds=None)
            mock_install.assert_called_once_with(
                software_path='/software', virtual_host='vhost',
                product_id='productID', conf_file='config_file',
                root_user='root', root_password='pass',
                cwd='/tmp_nw', ascs_password='ascs_pass', timeout=0, interval=5)

    @mock.patch('salt.states.netweavermod._get_sap_instance_type')
    def test_installed_not_installed(self, mock_get):
        '''
        Test to check installed in test mode
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
                virtual_host='vhost', virtual_host_interface='eth1')
            mock_setup_cwd.assert_called_once_with(
                software_path='/software', cwd='/tmp/unattended', additional_dvds=None)
            mock_install.assert_called_once_with(
                software_path='/software', virtual_host='vhost',
                product_id='productID', conf_file='config_file',
                root_user='root', root_password='pass', cwd='/tmp_nw')
