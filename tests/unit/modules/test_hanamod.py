
# -*- coding: utf-8 -*-
'''
    :codeauthor: Xabier Arbulu Insausti <xarbulu@suse.com>
'''

# Import Python Libs
from __future__ import absolute_import, print_function, unicode_literals
import pytest
import sys

from salt import exceptions

# Import Salt Testing Libs
from tests.support.mixins import LoaderModuleMockMixin
from tests.support.unit import TestCase, skipIf
from tests.support import mock
from tests.support.mock import (
    MagicMock,
    patch,
    mock_open
)

# Import Salt Libs
import salt.modules.hanamod as hanamod


class HanaModuleTest(TestCase, LoaderModuleMockMixin):
    '''
    This class contains a set of functions that test salt.modules.hana.
    '''

    def setup_loader_modules(self):
        return {hanamod: {}}

    @patch('salt.modules.hanamod.hana.HanaInstance')
    def test_init_return(self, mock_hana):
        '''
        Test _init method
        '''
        mock_hana_inst = MagicMock()
        mock_hana.return_value = mock_hana_inst
        hana_inst = hanamod._init('prd', '00', 'pass')
        mock_hana.assert_called_once_with('prd', '00', 'pass')
        assert mock_hana_inst == hana_inst

    @patch('salt.modules.hanamod.hana.HanaInstance')
    def test_init_return_conf(self, mock_hana):
        '''
        Test _init method
        '''
        mock_hana_inst = MagicMock()
        mock_hana.return_value = mock_hana_inst
        mock_config = MagicMock(side_effect=[
            'conf_sid',
            'conf_inst',
            'conf_password'
        ])

        with patch.dict(hanamod.__salt__, {'config.option': mock_config}):
            hana_inst = hanamod._init()
            mock_hana.assert_called_once_with(
                'conf_sid', 'conf_inst', 'conf_password')
            assert mock_hana_inst == hana_inst
            mock_config.assert_has_calls([
                mock.call('hana.sid', None),
                mock.call('hana.inst', None),
                mock.call('hana.password', None)
            ])

    @patch('salt.modules.hanamod.hana.HanaInstance')
    def test_init_raise(self, mock_hana):
        '''
        Test _init method
        '''
        mock_hana.side_effect = TypeError('error')
        with pytest.raises(exceptions.SaltInvocationError) as err:
            hanamod._init('prd', '00', 'pass')
        mock_hana.assert_called_once_with('prd', '00', 'pass')
        assert 'error' in str(err.value)

    def test_is_installed_return_true(self):
        '''
        Test is_installed method
        '''
        mock_hana_inst = MagicMock()
        mock_hana_inst.is_installed.return_value = True
        mock_hana = MagicMock(return_value=mock_hana_inst)
        with patch.object(hanamod, '_init', mock_hana):
            assert hanamod.is_installed('prd', '00', 'pass')
            mock_hana.assert_called_once_with('prd', '00', 'pass')
            mock_hana_inst.is_installed.assert_called_once_with()

    def test_is_installed_return_false(self):
        '''
        Test is_installed method
        '''
        mock_hana_inst = MagicMock()
        mock_hana_inst.is_installed.return_value = False
        mock_hana = MagicMock(return_value=mock_hana_inst)
        with patch.object(hanamod, '_init', mock_hana):
            assert not hanamod.is_installed('prd', '00', 'pass')
            mock_hana.assert_called_once_with('prd', '00', 'pass')
            mock_hana_inst.is_installed.assert_called_once_with()

    @patch('salt.modules.hanamod.hana.HanaInstance')
    def test_create_conf_file_return(self, mock_hana):
        '''
        Test create_conf_file method - return
        '''
        mock_hana.create_conf_file.return_value = 'hana.conf'
        conf_file = hanamod.create_conf_file(
            'software_path', 'hana.conf', 'root', 'root')
        assert u'hana.conf' == conf_file
        mock_hana.create_conf_file.assert_called_once_with(
            'software_path', 'hana.conf', 'root', 'root')

    @patch('salt.modules.hanamod.hana.HanaInstance')
    def test_create_conf_file_raise(self, mock_hana):
        '''
        Test create_conf_file method - raise
        '''
        mock_hana.create_conf_file.side_effect = hanamod.hana.HanaError(
            'hana error'
        )
        with pytest.raises(exceptions.CommandExecutionError) as err:
            hanamod.create_conf_file('software_path', 'hana.conf', 'root', 'root')
        mock_hana.create_conf_file.assert_called_once_with(
            'software_path', 'hana.conf', 'root', 'root')
        assert 'hana error' in str(err.value)

    @patch('salt.modules.hanamod.hana.HanaInstance')
    def test_update_conf_file_return(self, mock_hana):
        '''
        Test update_conf_file method - return
        '''
        mock_hana.update_conf_file.return_value = 'hana.conf'
        conf_file = hanamod.update_conf_file(
            'hana.conf', sid='sid', number='00')
        assert u'hana.conf' == conf_file
        mock_hana.update_conf_file.assert_called_once_with(
            'hana.conf', sid='sid', number='00')

    @patch('salt.modules.hanamod.hana.HanaInstance')
    def test_update_conf_file_raise(self, mock_hana):
        '''
        Test update_conf_file method - raise
        '''
        mock_hana.update_conf_file.side_effect = IOError('hana error')
        with pytest.raises(exceptions.CommandExecutionError) as err:
            hanamod.update_conf_file('hana.conf', sid='sid', number='00')
        mock_hana.update_conf_file.assert_called_once_with(
            'hana.conf', sid='sid', number='00')
        assert 'hana error' in str(err.value)

    @patch('salt.modules.hanamod.hana.HanaInstance')
    def test_update_hdb_pwd_file_return(self, mock_hana):
        '''
        Test update_hdb_pwd_file method - return
        '''
        mock_hana.update_hdb_pwd_file.return_value = 'hana.conf.xml'
        hdb_pwd_file = hanamod.update_hdb_pwd_file(
            'hana.conf.xml', sapadm_password='Test1234', system_user_password='Syst1234')
        assert u'hana.conf.xml' == hdb_pwd_file
        mock_hana.update_hdb_pwd_file.assert_called_once_with(
            'hana.conf.xml', sapadm_password='Test1234', system_user_password='Syst1234')

    @patch('salt.modules.hanamod.hana.HanaInstance')
    def test_update_hdb_pwd_file_raise(self, mock_hana):
        '''
        Test update_hdb_pwd_file method - raise
        '''
        mock_hana.update_hdb_pwd_file.side_effect = IOError('hana error')
        with pytest.raises(exceptions.CommandExecutionError) as err:
            hanamod.update_hdb_pwd_file('hana.conf.xml', sapadm_password='Test1234', system_user_password='Syst1234')
        mock_hana.update_hdb_pwd_file.assert_called_once_with(
            'hana.conf.xml', sapadm_password='Test1234', system_user_password='Syst1234')
        assert 'hana error' in str(err.value)

    @patch('salt.modules.hanamod.hana.HanaInstance')
    def test_install_return(self, mock_hana):
        '''
        Test install method - return
        '''
        mock_hana.install.return_value = 'hana.conf'
        hanamod.install(
            'software_path', 'hana.conf', 'root', 'root', 'hana.conf.xml')
        mock_hana.install.assert_called_once_with(
            'software_path', 'hana.conf', 'root', 'root', 'hana.conf.xml')

    @patch('salt.modules.hanamod.hana.HanaInstance')
    def test_install_raise(self, mock_hana):
        '''
        Test install method - raise
        '''
        mock_hana.install.side_effect = hanamod.hana.HanaError(
            'hana error'
        )
        with pytest.raises(exceptions.CommandExecutionError) as err:
            hanamod.install('software_path', 'hana.conf', 'root', 'root', 'hana.conf.xml')
        mock_hana.install.assert_called_once_with(
            'software_path', 'hana.conf', 'root', 'root', 'hana.conf.xml')
        assert 'hana error' in str(err.value)

    def test_uninstall_return(self):
        '''
        Test uninstall method - return
        '''
        mock_hana_inst = MagicMock()
        mock_hana = MagicMock(return_value=mock_hana_inst)
        with patch.object(hanamod, '_init', mock_hana):
            hanamod.uninstall('root', 'pass', '/hana', 'prd', '00', 'pass')
            mock_hana.assert_called_once_with(
                'prd', '00', 'pass')
            mock_hana_inst.uninstall.assert_called_once_with(
                'root', 'pass', installation_folder='/hana')

    def test_uninstall_return_default(self):
        '''
        Test uninstall method - return
        '''
        mock_hana_inst = MagicMock()
        mock_hana = MagicMock(return_value=mock_hana_inst)
        with patch.object(hanamod, '_init', mock_hana):
            hanamod.uninstall('root', 'pass', None, 'prd', '00', 'pass')
            mock_hana.assert_called_once_with(
                'prd', '00', 'pass')
            mock_hana_inst.uninstall.assert_called_once_with('root', 'pass')

    def test_uninstall_raise(self):
        '''
        Test uninstall method - raise
        '''
        mock_hana_inst = MagicMock()
        mock_hana_inst.uninstall.side_effect = hanamod.hana.HanaError(
            'hana error'
        )
        mock_hana = MagicMock(return_value=mock_hana_inst)
        with patch.object(hanamod, '_init', mock_hana):
            with pytest.raises(exceptions.CommandExecutionError) as err:
                hanamod.uninstall('root', 'pass', None, 'prd', '00', 'pass')
            mock_hana.assert_called_once_with('prd', '00', 'pass')
            mock_hana_inst.uninstall.assert_called_once_with('root', 'pass')
            assert 'hana error' in str(err.value)

    def test_is_running_return_true(self):
        '''
        Test is_running method
        '''
        mock_hana_inst = MagicMock()
        mock_hana_inst.is_running.return_value = True
        mock_hana = MagicMock(return_value=mock_hana_inst)
        with patch.object(hanamod, '_init', mock_hana):
            assert hanamod.is_running('prd', '00', 'pass')
            mock_hana.assert_called_once_with('prd', '00', 'pass')
            mock_hana_inst.is_running.assert_called_once_with()

    def test_is_running_return_false(self):
        '''
        Test is_running method
        '''
        mock_hana_inst = MagicMock()
        mock_hana_inst.is_running.return_value = False
        mock_hana = MagicMock(return_value=mock_hana_inst)
        with patch.object(hanamod, '_init', mock_hana):
            assert not hanamod.is_running('prd', '00', 'pass')
            mock_hana.assert_called_once_with('prd', '00', 'pass')
            mock_hana_inst.is_running.assert_called_once_with()

    def test_get_version_return(self):
        '''
        Test get_version method - return
        '''
        mock_hana_inst = MagicMock()
        mock_hana_inst.get_version.return_value = '1.2.3'
        mock_hana = MagicMock(return_value=mock_hana_inst)
        with patch.object(hanamod, '_init', mock_hana):
            assert u'1.2.3' == hanamod.get_version('prd', '00', 'pass')
            mock_hana.assert_called_once_with('prd', '00', 'pass')
            mock_hana_inst.get_version.assert_called_once_with()

    def test_get_version_raise(self):
        '''
        Test get_version method - raise
        '''
        mock_hana_inst = MagicMock()
        mock_hana_inst.get_version.side_effect = hanamod.hana.HanaError(
            'hana error'
        )
        mock_hana = MagicMock(return_value=mock_hana_inst)
        with patch.object(hanamod, '_init', mock_hana):
            with pytest.raises(exceptions.CommandExecutionError) as err:
                hanamod.get_version('prd', '00', 'pass')
            mock_hana.assert_called_once_with('prd', '00', 'pass')
            mock_hana_inst.get_version.assert_called_once_with()
            assert 'hana error' in str(err.value)

    def test_start_return(self):
        '''
        Test start method - return
        '''
        mock_hana_inst = MagicMock()
        mock_hana = MagicMock(return_value=mock_hana_inst)
        with patch.object(hanamod, '_init', mock_hana):
            hanamod.start('prd', '00', 'pass')
            mock_hana.assert_called_once_with('prd', '00', 'pass')
            mock_hana_inst.start.assert_called_once_with()

    def test_start_raise(self):
        '''
        Test start method - raise
        '''
        mock_hana_inst = MagicMock()
        mock_hana_inst.start.side_effect = hanamod.hana.HanaError(
            'hana error'
        )
        mock_hana = MagicMock(return_value=mock_hana_inst)
        with patch.object(hanamod, '_init', mock_hana):
            with pytest.raises(exceptions.CommandExecutionError) as err:
                hanamod.start('prd', '00', 'pass')
            mock_hana.assert_called_once_with('prd', '00', 'pass')
            mock_hana_inst.start.assert_called_once_with()
            assert 'hana error' in str(err.value)

    def test_stop_return(self):
        '''
        Test stop method - return
        '''
        mock_hana_inst = MagicMock()
        mock_hana = MagicMock(return_value=mock_hana_inst)
        with patch.object(hanamod, '_init', mock_hana):
            hanamod.stop('prd', '00', 'pass')
            mock_hana.assert_called_once_with('prd', '00', 'pass')
            mock_hana_inst.stop.assert_called_once_with()

    def test_stop_raise(self):
        '''
        Test stop method - raise
        '''
        mock_hana_inst = MagicMock()
        mock_hana_inst.stop.side_effect = hanamod.hana.HanaError(
            'hana error'
        )
        mock_hana = MagicMock(return_value=mock_hana_inst)
        with patch.object(hanamod, '_init', mock_hana):
            with pytest.raises(exceptions.CommandExecutionError) as err:
                hanamod.stop('prd', '00', 'pass')
            mock_hana.assert_called_once_with('prd', '00', 'pass')
            mock_hana_inst.stop.assert_called_once_with()
            assert 'hana error' in str(err.value)

    def test_get_sr_state_return(self):
        '''
        Test get_sr_state method - return
        '''
        mock_hana_inst = MagicMock()
        mock_hana_inst.get_sr_state.return_value = 1
        mock_hana = MagicMock(return_value=mock_hana_inst)
        with patch.object(hanamod, '_init', mock_hana):
            assert 1 == hanamod.get_sr_state('prd', '00', 'pass')
            mock_hana.assert_called_once_with('prd', '00', 'pass')
            mock_hana_inst.get_sr_state.assert_called_once_with()

    def test_get_sr_state_raise(self):
        '''
        Test get_sr_state method - raise
        '''
        mock_hana_inst = MagicMock()
        mock_hana_inst.get_sr_state.side_effect = hanamod.hana.HanaError(
            'hana error'
        )
        mock_hana = MagicMock(return_value=mock_hana_inst)
        with patch.object(hanamod, '_init', mock_hana):
            with pytest.raises(exceptions.CommandExecutionError) as err:
                hanamod.get_sr_state('prd', '00', 'pass')
            mock_hana.assert_called_once_with('prd', '00', 'pass')
            mock_hana_inst.get_sr_state.assert_called_once_with()
            assert 'hana error' in str(err.value)

    def test_sr_enable_primary_return(self):
        '''
        Test sr_enable_primary method - return
        '''
        mock_hana_inst = MagicMock()
        mock_hana = MagicMock(return_value=mock_hana_inst)
        with patch.object(hanamod, '_init', mock_hana):
            hanamod.sr_enable_primary('NUE', 'prd', '00', 'pass')
            mock_hana.assert_called_once_with('prd', '00', 'pass')
            mock_hana_inst.sr_enable_primary.assert_called_once_with('NUE')

    def test_sr_enable_primary_raise(self):
        '''
        Test sr_enable_primary method - raise
        '''
        mock_hana_inst = MagicMock()
        mock_hana_inst.sr_enable_primary.side_effect = hanamod.hana.HanaError(
            'hana error'
        )
        mock_hana = MagicMock(return_value=mock_hana_inst)
        with patch.object(hanamod, '_init', mock_hana):
            with pytest.raises(exceptions.CommandExecutionError) as err:
                hanamod.sr_enable_primary('NUE', 'prd', '00', 'pass')
            mock_hana.assert_called_once_with('prd', '00', 'pass')
            mock_hana_inst.sr_enable_primary.assert_called_once_with('NUE')
            assert 'hana error' in str(err.value)

    def test_sr_disable_primary_return(self):
        '''
        Test sr_disable_primary method - return
        '''
        mock_hana_inst = MagicMock()
        mock_hana = MagicMock(return_value=mock_hana_inst)
        with patch.object(hanamod, '_init', mock_hana):
            hanamod.sr_disable_primary('prd', '00', 'pass')
            mock_hana.assert_called_once_with('prd', '00', 'pass')
            mock_hana_inst.sr_disable_primary.assert_called_once_with()

    def test_sr_disable_primary_raise(self):
        '''
        Test sr_disable_primary method - raise
        '''
        mock_hana_inst = MagicMock()
        mock_hana_inst.sr_disable_primary.side_effect = hanamod.hana.HanaError(
            'hana error'
        )
        mock_hana = MagicMock(return_value=mock_hana_inst)
        with patch.object(hanamod, '_init', mock_hana):
            with pytest.raises(exceptions.CommandExecutionError) as err:
                hanamod.sr_disable_primary('prd', '00', 'pass')
            mock_hana.assert_called_once_with('prd', '00', 'pass')
            mock_hana_inst.sr_disable_primary.assert_called_once_with()
            assert 'hana error' in str(err.value)

    def test_sr_register_secondary_return(self):
        '''
        Test sr_register_secondary method - return
        '''
        mock_hana_inst = MagicMock()
        mock_hana = MagicMock(return_value=mock_hana_inst)
        with patch.object(hanamod, '_init', mock_hana):
            hanamod.sr_register_secondary(
                'PRAGUE', 'hana01', '00', 'sync',
                'logreplay', 'prd', '00', 'pass',
                primary_pass='pass', timeout=10, interval=10)
            mock_hana.assert_called_once_with('prd', '00', 'pass')
            mock_hana_inst.sr_register_secondary.assert_called_once_with(
                'PRAGUE', 'hana01', '00', 'sync', 'logreplay',
                primary_pass='pass', timeout=10, interval=10)

    def test_sr_register_secondary_raise(self):
        '''
        Test sr_register_secondary method - raise
        '''
        mock_hana_inst = MagicMock()
        mock_hana_inst.sr_register_secondary.side_effect = hanamod.hana.HanaError(
            'hana error'
        )
        mock_hana = MagicMock(return_value=mock_hana_inst)
        with patch.object(hanamod, '_init', mock_hana):
            with pytest.raises(exceptions.CommandExecutionError) as err:
                hanamod.sr_register_secondary(
                    'PRAGUE', 'hana01', '00', 'sync',
                    'logreplay', 'prd', '00', 'pass')
            mock_hana.assert_called_once_with('prd', '00', 'pass')
            mock_hana_inst.sr_register_secondary.assert_called_once_with(
                'PRAGUE', 'hana01', '00', 'sync', 'logreplay')
            assert 'hana error' in str(err.value)

    def test_sr_changemode_secondary_return(self):
        '''
        Test sr_changemode_secondary method - return
        '''
        mock_hana_inst = MagicMock()
        mock_hana = MagicMock(return_value=mock_hana_inst)
        with patch.object(hanamod, '_init', mock_hana):
            hanamod.sr_changemode_secondary('sync', 'prd', '00', 'pass')
            mock_hana.assert_called_once_with('prd', '00', 'pass')
            mock_hana_inst.sr_changemode_secondary.assert_called_once_with('sync')

    def test_sr_changemode_secondary_raise(self):
        '''
        Test sr_changemode_secondary method - raise
        '''
        mock_hana_inst = MagicMock()
        mock_hana_inst.sr_changemode_secondary.side_effect = hanamod.hana.HanaError(
            'hana error'
        )
        mock_hana = MagicMock(return_value=mock_hana_inst)
        with patch.object(hanamod, '_init', mock_hana):
            with pytest.raises(exceptions.CommandExecutionError) as err:
                hanamod.sr_changemode_secondary('sync', 'prd', '00', 'pass')
            mock_hana.assert_called_once_with('prd', '00', 'pass')
            mock_hana_inst.sr_changemode_secondary.assert_called_once_with(
                'sync')
            assert 'hana error' in str(err.value)

    def test_sr_unregister_secondary_return(self):
        '''
        Test sr_unregister_secondary method - return
        '''
        mock_hana_inst = MagicMock()
        mock_hana = MagicMock(return_value=mock_hana_inst)
        with patch.object(hanamod, '_init', mock_hana):
            hanamod.sr_unregister_secondary('NUE', 'prd', '00', 'pass')
            mock_hana.assert_called_once_with('prd', '00', 'pass')
            mock_hana_inst.sr_unregister_secondary.assert_called_once_with(
                'NUE')

    def test_sr_unregister_secondary_raise(self):
        '''
        Test sr_unregister_secondary method - raise
        '''
        mock_hana_inst = MagicMock()
        mock_hana_inst.sr_unregister_secondary.side_effect = hanamod.hana.HanaError(
            'hana error'
        )
        mock_hana = MagicMock(return_value=mock_hana_inst)
        with patch.object(hanamod, '_init', mock_hana):
            with pytest.raises(exceptions.CommandExecutionError) as err:
                hanamod.sr_unregister_secondary('NUE', 'prd', '00', 'pass')
            mock_hana.assert_called_once_with('prd', '00', 'pass')
            mock_hana_inst.sr_unregister_secondary.assert_called_once_with(
                'NUE')
            assert 'hana error' in str(err.value)

    def test_check_user_key_return(self):
        '''
        Test check_user_key method - return
        '''
        mock_hana_inst = MagicMock()
        mock_hana = MagicMock(return_value=mock_hana_inst)
        with patch.object(hanamod, '_init', mock_hana):
            hanamod.check_user_key('key', 'prd', '00', 'pass')
            mock_hana.assert_called_once_with('prd', '00', 'pass')
            mock_hana_inst.check_user_key.assert_called_once_with(
                'key')

    def test_check_user_key_raise(self):
        '''
        Test check_user_key method - raise
        '''
        mock_hana_inst = MagicMock()
        mock_hana_inst.check_user_key.side_effect = hanamod.hana.HanaError(
            'hana error'
        )
        mock_hana = MagicMock(return_value=mock_hana_inst)
        with patch.object(hanamod, '_init', mock_hana):
            with pytest.raises(exceptions.CommandExecutionError) as err:
                hanamod.check_user_key('key', 'prd', '00', 'pass')
            mock_hana.assert_called_once_with('prd', '00', 'pass')
            mock_hana_inst.check_user_key.assert_called_once_with(
                'key')
            assert 'hana error' in str(err.value)

    def test_create_user_key_return(self):
        '''
        Test create_user_key method - return
        '''
        mock_hana_inst = MagicMock()
        mock_hana = MagicMock(return_value=mock_hana_inst)
        with patch.object(hanamod, '_init', mock_hana):
            hanamod.create_user_key(
                'key', 'env', 'user', 'pass', 'db', 'prd', '00', 'pass')
            mock_hana.assert_called_once_with('prd', '00', 'pass')
            mock_hana_inst.create_user_key.assert_called_once_with(
                'key', 'env', 'user', 'pass', 'db')

    def test_create_user_key_raise(self):
        '''
        Test create_user_key method - raise
        '''
        mock_hana_inst = MagicMock()
        mock_hana_inst.create_user_key.side_effect = hanamod.hana.HanaError(
            'hana error'
        )
        mock_hana = MagicMock(return_value=mock_hana_inst)
        with patch.object(hanamod, '_init', mock_hana):
            with pytest.raises(exceptions.CommandExecutionError) as err:
                hanamod.create_user_key(
                    'key', 'env', 'user', 'pass', 'db', 'prd', '00', 'pass')
            mock_hana.assert_called_once_with('prd', '00', 'pass')
            mock_hana_inst.create_user_key.assert_called_once_with(
                'key', 'env', 'user', 'pass', 'db')
            assert 'hana error' in str(err.value)

    def test_create_backup_return(self):
        '''
        Test create_backup method - return
        '''
        mock_hana_inst = MagicMock()
        mock_hana = MagicMock(return_value=mock_hana_inst)
        with patch.object(hanamod, '_init', mock_hana):
            hanamod.create_backup(
                'db', 'backup', 'key', 'key_user', 'key_password',
                'prd', '00', 'pass')
            mock_hana.assert_called_once_with('prd', '00', 'pass')
            mock_hana_inst.create_backup.assert_called_once_with(
                'db', 'backup', 'key', 'key_user', 'key_password')

    def test_create_backup_raise(self):
        '''
        Test create_backup method - raise
        '''
        mock_hana_inst = MagicMock()
        mock_hana_inst.create_backup.side_effect = hanamod.hana.HanaError(
            'hana error'
        )
        mock_hana = MagicMock(return_value=mock_hana_inst)
        with patch.object(hanamod, '_init', mock_hana):
            with pytest.raises(exceptions.CommandExecutionError) as err:
                hanamod.create_backup(
                    'db', 'backup', 'key', 'key_user', 'key_password',
                    'prd', '00', 'pass')
            mock_hana.assert_called_once_with('prd', '00', 'pass')
            mock_hana_inst.create_backup.assert_called_once_with(
                'db', 'backup', 'key', 'key_user', 'key_password')
            assert 'hana error' in str(err.value)

    def test_sr_cleanup_return(self):
        '''
        Test sr_cleanup method - return
        '''
        mock_hana_inst = MagicMock()
        mock_hana = MagicMock(return_value=mock_hana_inst)
        with patch.object(hanamod, '_init', mock_hana):
            hanamod.sr_cleanup('prd', '00', 'pass', True)
            mock_hana.assert_called_once_with('prd', '00', 'pass')
            mock_hana_inst.sr_cleanup.assert_called_once_with(True)

    def test_sr_cleanup_raise(self):
        '''
        Test sr_cleanup method - raise
        '''
        mock_hana_inst = MagicMock()
        mock_hana_inst.sr_cleanup.side_effect = hanamod.hana.HanaError(
            'hana error'
        )
        mock_hana = MagicMock(return_value=mock_hana_inst)
        with patch.object(hanamod, '_init', mock_hana):
            with pytest.raises(exceptions.CommandExecutionError) as err:
                hanamod.sr_cleanup('prd', '00', 'pass', False)
            mock_hana.assert_called_once_with('prd', '00', 'pass')
            mock_hana_inst.sr_cleanup.assert_called_once_with(False)
            assert 'hana error' in str(err.value)

    def test_set_ini_parameter_return(self):
        '''
        Test set_ini_parameter method - return
        '''
        mock_hana_inst = MagicMock()
        mock_hana = MagicMock(return_value=mock_hana_inst)
        ini_parameter_values = [{'section_name': 'memorymanager',
                                 'parameter_name': 'global_allocation_limit',
                                 'parameter_value': '25000'}]
        with patch.object(hanamod, '_init', mock_hana):
            hanamod.set_ini_parameter(ini_parameter_values=ini_parameter_values,
                                      database='db', file_name='global.ini',
                                      layer='SYSTEM', layer_name=None,
                                      reconfig=True, key_name='key',
                                      user_name='key_user',
                                      user_password='key_password',
                                      sid='prd', inst='00', password='pass')
            mock_hana.assert_called_once_with('prd', '00', 'pass')
            mock_hana_inst.set_ini_parameter.assert_called_once_with(
                ini_parameter_values=[{'section_name': 'memorymanager',
                                       'parameter_name': 'global_allocation_limit',
                                       'parameter_value': '25000'}],
                database='db', file_name='global.ini',
                layer='SYSTEM', layer_name=None, reconfig=True,
                key_name='key', user_name='key_user', user_password='key_password')

    def test_set_ini_parameter_raise(self):
        '''
        Test set_ini_parameter method - raise
        '''
        mock_hana_inst = MagicMock()
        mock_hana_inst.set_ini_parameter.side_effect = hanamod.hana.HanaError(
            'hana error'
        )
        mock_hana = MagicMock(return_value=mock_hana_inst)
        ini_parameter_values = [{'section_name': 'memorymanager',
                                 'parameter_name': 'global_allocation_limit',
                                 'parameter_value': '25000'}]
        with patch.object(hanamod, '_init', mock_hana):
            with pytest.raises(exceptions.CommandExecutionError) as err:
                hanamod.set_ini_parameter(
                    ini_parameter_values=ini_parameter_values,
                    database='db', file_name='global.ini', layer='SYSTEM',
                    layer_name=None, reconfig=True, key_name='key',
                    user_name='key_user', user_password='key_password',
                    sid='prd', inst='00', password='pass')
            mock_hana.assert_called_once_with('prd', '00', 'pass')
            mock_hana_inst.set_ini_parameter.assert_called_once_with(
                ini_parameter_values=[{'section_name': 'memorymanager',
                                       'parameter_name': 'global_allocation_limit',
                                       'parameter_value': '25000'}],
                database='db', file_name='global.ini',
                layer='SYSTEM', layer_name=None, reconfig=True,
                key_name='key', user_name='key_user', user_password='key_password')
            assert 'hana error' in str(err.value)

    def test_unset_ini_parameter_return(self):
        '''
        Test unset_ini_parameter method - return
        '''
        mock_hana_inst = MagicMock()
        mock_hana = MagicMock(return_value=mock_hana_inst)
        with patch.object(hanamod, '_init', mock_hana):
            hanamod.unset_ini_parameter(
                ini_parameter_names=[{'section_name': 'memorymanager',
                                      'parameter_name': 'global_allocation_limit'}],
                database='db', file_name='global.ini', layer='SYSTEM',
                layer_name=None, reconfig=True, key_name='key',
                user_name='key_user', user_password='key_password',
                sid='prd', inst='00', password='pass')
            mock_hana.assert_called_once_with('prd', '00', 'pass')
            mock_hana_inst.unset_ini_parameter.assert_called_once_with(
                ini_parameter_names=[{'section_name': 'memorymanager',
                                      'parameter_name': 'global_allocation_limit'}],
                database='db', file_name='global.ini',
                layer='SYSTEM', layer_name=None, reconfig=True,
                key_name='key', user_name='key_user', user_password='key_password')

    def test_unset_ini_parameter_raise(self):
        '''
        Test unset_ini_parameter method - raise
        '''
        mock_hana_inst = MagicMock()
        mock_hana_inst.unset_ini_parameter.side_effect = hanamod.hana.HanaError(
            'hana error'
        )
        mock_hana = MagicMock(return_value=mock_hana_inst)
        with patch.object(hanamod, '_init', mock_hana):
            with pytest.raises(exceptions.CommandExecutionError) as err:
                hanamod.unset_ini_parameter(
                    ini_parameter_names=[{'section_name': 'memorymanager',
                                          'parameter_name':
                                          'global_allocation_limit'}],
                    database='db', file_name='global.ini', layer='SYSTEM',
                    layer_name=None, reconfig=True, key_name='key',
                    user_name='key_user', user_password='key_password',
                    sid='prd', inst='00', password='pass')
            mock_hana.assert_called_once_with('prd', '00', 'pass')
            mock_hana_inst.unset_ini_parameter.assert_called_once_with(
                ini_parameter_names=[{'section_name': 'memorymanager',
                                      'parameter_name': 'global_allocation_limit'}],
                database='db', file_name='global.ini',
                layer_name=None, layer='SYSTEM', reconfig=True,
                key_name='key', user_name='key_user', user_password='key_password')
            assert 'hana error' in str(err.value)

    @mock.patch('salt.modules.hanamod.hdb_connector.HdbConnector')
    @mock.patch('time.time')
    def test_wait_for_connection(self, mock_time, mock_hdb_connector):
        mock_hdb_instance = mock.Mock()
        mock_hdb_connector.return_value = mock_hdb_instance
        mock_time.return_value = 0
        hanamod.wait_for_connection('192.168.10.15', 30015, 'SYSTEM', 'pass')

        mock_time.assert_called_once_with()
        mock_hdb_instance.connect.assert_called_once_with(
            '192.168.10.15', 30015, user='SYSTEM', password='pass')
        mock_hdb_instance.disconnect.assert_called_once_with()

    @mock.patch('salt.modules.hanamod.hdb_connector.HdbConnector')
    @mock.patch('time.sleep')
    @mock.patch('time.time')
    def test_wait_for_connection_loop(self, mock_time, mock_sleep, mock_hdb_connector):
        mock_hdb_instance = mock.Mock()
        mock_hdb_connector.return_value = mock_hdb_instance
        mock_hdb_instance.connect.side_effect = [
            hanamod.base_connector.ConnectionError, hanamod.base_connector.ConnectionError, None]
        mock_time.side_effect = [0, 1, 2, 3]
        hanamod.wait_for_connection('192.168.10.15', 30015, 'SYSTEM', 'pass', timeout=2)

        assert mock_time.call_count == 3
        assert mock_sleep.call_count == 2
        mock_sleep.assert_has_calls([
            mock.call(5),
            mock.call(5)
        ])
        mock_hdb_instance.connect.assert_has_calls([
            mock.call('192.168.10.15', 30015, user='SYSTEM', password='pass'),
            mock.call('192.168.10.15', 30015, user='SYSTEM', password='pass'),
            mock.call('192.168.10.15', 30015, user='SYSTEM', password='pass')
        ])
        mock_hdb_instance.disconnect.assert_called_once_with()

    @mock.patch('salt.modules.hanamod.hdb_connector.HdbConnector')
    @mock.patch('time.sleep')
    @mock.patch('time.time')
    def test_wait_for_connection_error(self, mock_time, mock_sleep, mock_hdb_connector):
        mock_hdb_instance = mock.Mock()
        mock_hdb_connector.return_value = mock_hdb_instance
        mock_hdb_instance.connect.side_effect = [
            hanamod.base_connector.ConnectionError, hanamod.base_connector.ConnectionError,
            hanamod.base_connector.ConnectionError]
        mock_time.side_effect = [0, 1, 2, 3]
        with pytest.raises(exceptions.CommandExecutionError) as err:
            hanamod.wait_for_connection('192.168.10.15', 30015, 'SYSTEM', 'pass', timeout=2)

        assert mock_time.call_count == 4
        assert mock_sleep.call_count == 3
        mock_sleep.assert_has_calls([
            mock.call(5),
            mock.call(5),
            mock.call(5)
        ])
        mock_hdb_instance.connect.assert_has_calls([
            mock.call('192.168.10.15', 30015, user='SYSTEM', password='pass'),
            mock.call('192.168.10.15', 30015, user='SYSTEM', password='pass'),
            mock.call('192.168.10.15', 30015, user='SYSTEM', password='pass')
        ])
        assert 'HANA database not available after 2 seconds in 192.168.10.15:30015' in str(err.value)

    @mock.patch('salt.modules.hanamod.hdb_connector')
    @mock.patch('salt.modules.hanamod.reload_module')
    def test_reload_hdb_connector_py3(self, mock_reload, mock_hdb_connector):
        if sys.version_info.major == 2:
            self.skipTest('python3 only')
        hanamod.reload_hdb_connector()
        mock_reload.assert_called_once_with(mock_hdb_connector)

    @mock.patch('salt.modules.hanamod.hdb_connector')
    @mock.patch('salt.modules.hanamod.reload_module')
    @mock.patch('imp.find_module')
    @mock.patch('imp.load_module')
    def test_reload_hdb_connector_py2(
            self, mock_load, mock_find, mock_reload, mock_hdb_connector):
        if sys.version_info.major == 3:
            self.skipTest('python2 only')

        pyhdbcli_ptr = mock.Mock()
        dbapi_ptr = mock.Mock()
        hdbcli_ptr = mock.Mock()

        mock_find.side_effect = [
            (pyhdbcli_ptr, 2, 3), (dbapi_ptr, 6, 7), (hdbcli_ptr, 10, 11)]

        hanamod.reload_hdb_connector()

        mock_reload.assert_called_once_with(mock_hdb_connector)
        mock_find.assert_has_calls([
            mock.call('pyhdbcli'),
            mock.call('hdbcli/dbapi'),
            mock.call('hdbcli')
        ])
        mock_load.assert_has_calls([
            mock.call('pyhdbcli', pyhdbcli_ptr, 2, 3),
            mock.call('hdbcli/dbapi', dbapi_ptr, 6, 7),
            mock.call('hdbcli', hdbcli_ptr, 10, 11)
        ])

        pyhdbcli_ptr.close.assert_called_once_with()
        dbapi_ptr.close.assert_called_once_with()
        hdbcli_ptr.close.assert_called_once_with()

    @mock.patch('logging.Logger.debug')
    @mock.patch('salt.utils.files.fopen')
    def test_find_sap_folder_error(self, mock_fopen, mock_debug):
        mock_pattern = mock.Mock(pattern='my_pattern')
        mock_fopen.side_effect = [
            IOError, IOError, IOError, IOError]
        with pytest.raises(hanamod.SapFolderNotFoundError) as err:
            hanamod._find_sap_folder(['1234', '5678'], mock_pattern)

        assert 'SAP folder with my_pattern pattern not found' in str(err.value)
        mock_debug.assert_has_calls([
            mock.call('%s file not found in %s. Skipping folder', 'LABEL.ASC', '1234'),
            mock.call('%s file not found in %s. Skipping folder', 'LABELIDX.ASC', '1234'),
            mock.call('%s file not found in %s. Skipping folder', 'LABEL.ASC', '5678'),
            mock.call('%s file not found in %s. Skipping folder', 'LABELIDX.ASC', '5678')
        ])

    def test_find_sap_folder_contain_hana(self):
        mock_pattern = mock.Mock(return_value=True)
        with patch('salt.utils.files.fopen', mock_open(read_data='data\n')) as mock_file:
            folder = hanamod._find_sap_folder(['1234', '5678'], mock_pattern)

        mock_pattern.match.assert_called_once_with('data')
        assert folder in '1234'

    @mock.patch('logging.Logger.debug')
    def test_find_sap_folder_contain_units(self, mock_debug):
        mock_pattern = mock.Mock(pattern='my_pattern')
        mock_pattern.match.side_effect = [False, True]
        with patch('salt.utils.files.fopen', mock_open(read_data=[
                'data\n', 'DATA_UNITS\n', 'data_2\n'])) as mock_file:
            folder = hanamod._find_sap_folder(['1234', '5678'], mock_pattern)

        mock_pattern.match.assert_has_calls([
            mock.call('data'),
            mock.call('data_2')
        ])
        mock_debug.assert_has_calls([
            mock.call('%s folder does not contain %s pattern', '1234', 'my_pattern')
        ])
        assert folder in '1234/DATA_UNITS'

    @mock.patch('logging.Logger.debug')
    @mock.patch('os.path.isdir')
    @mock.patch('os.listdir')
    def test_find_sap_folder_contain_subfolder(
            self, mock_listdir, mock_isdir, mock_debug):
        mock_pattern = mock.Mock(pattern='my_pattern')
        mock_pattern.match.side_effect = [True]
        mock_listdir.return_value = ['folder1', 'folder2', 'file1']
        mock_isdir.side_effect = [True, True, False]

        with patch('salt.utils.files.fopen', mock_open(
                read_data=[IOError, IOError, 'subfolder\n'])) as mock_file:
            with patch('salt.modules.hanamod._find_sap_folder',
                       side_effect=hanamod._find_sap_folder) as mock_find_sap_folder:
                folder = mock_find_sap_folder(['1234', '5678'], mock_pattern, 2)

                mock_find_sap_folder.assert_has_calls([
                    mock.call(['1234', '5678'], mock_pattern, 2),
                    mock.call(['1234/folder1', '1234/folder2'], mock_pattern, 1)
                ])

        mock_listdir.assert_called_once_with('1234')

        mock_isdir.assert_has_calls([
            mock.call('1234/folder1'),
            mock.call('1234/folder2'),
            mock.call('1234/file1')
        ])

        assert folder == '1234/folder1'

    @mock.patch('logging.Logger.debug')
    @mock.patch('os.path.isdir')
    @mock.patch('os.listdir')
    def test_find_sap_folder_contain_subfolder_error(
            self, mock_listdir, mock_isdir, mock_debug):
        mock_pattern = mock.Mock(pattern='my_pattern')
        mock_listdir.return_value = ['folder1', 'file1', 'file2']
        mock_isdir.side_effect = [True, False, False]

        with patch('salt.utils.files.fopen', mock_open(
                read_data=[IOError, IOError, IOError, IOError])) as mock_file:
            with patch('salt.modules.hanamod._find_sap_folder',
                       side_effect=hanamod._find_sap_folder) as mock_find_sap_folder:
                with pytest.raises(hanamod.SapFolderNotFoundError) as err:
                    mock_find_sap_folder(['1234'], mock_pattern, 1)

                mock_find_sap_folder.assert_has_calls([
                    mock.call(['1234'], mock_pattern, 1),
                    mock.call(['1234/folder1'], mock_pattern, 0)
                ])

        mock_listdir.assert_called_once_with('1234')

        mock_isdir.assert_has_calls([
            mock.call('1234/folder1'),
            mock.call('1234/file1'),
            mock.call('1234/file2')
        ])

    @mock.patch('logging.Logger.debug')
    def test_find_sap_folder_contain_units_error(self, mock_debug):
        mock_pattern = mock.Mock(pattern='my_pattern')
        mock_pattern.match.side_effect = [False, False]
        with patch('salt.utils.files.fopen', mock_open(read_data=[
                'data\n', 'DATA_UNITS\n', 'data_2\n', IOError])) as mock_file:
            with pytest.raises(hanamod.SapFolderNotFoundError) as err:
                hanamod._find_sap_folder(['1234'], mock_pattern)

        mock_pattern.match.assert_has_calls([
            mock.call('data'),
            mock.call('data_2')
        ])
        mock_debug.assert_has_calls([
            mock.call('%s folder does not contain %s pattern', '1234', 'my_pattern')
        ])
        assert 'SAP folder with my_pattern pattern not found' in str(err.value)

    @mock.patch('re.compile')
    @mock.patch('salt.modules.hanamod._find_sap_folder')
    @mock.patch('salt.modules.hanamod.hana.HanaInstance.get_platform')
    def test_extract_pydbapi(self, mock_get_platform, mock_find_sap_folders, mock_compile):
        mock_get_platform.return_value = 'LINUX_X86_64'
        mock_find_sap_folders.return_value = 'my_folder'
        compile_mocked = mock.Mock()
        mock_compile.return_value = compile_mocked
        mock_tar = MagicMock()
        with patch.dict(hanamod.__salt__, {'archive.tar': mock_tar}):
            pydbapi_file = hanamod.extract_pydbapi(
                'PYDBAPI.tar.gz', ['1234', '5678'], '/tmp/output', additional_extract_options='-l')

        mock_compile.assert_called_once_with('^HDB_CLIENT:20.*:LINUX_X86_64:.*')
        mock_find_sap_folders.assert_called_once_with(
            ['1234', '5678'], compile_mocked, recursion_level=1)
        mock_tar.assert_called_once_with(
            options='-l -xvf', tarfile='my_folder/client/PYDBAPI.tar.gz', cwd='/tmp/output')
        assert pydbapi_file == 'my_folder/client/PYDBAPI.tar.gz'

    @mock.patch('re.compile')
    @mock.patch('salt.modules.hanamod._find_sap_folder')
    @mock.patch('salt.modules.hanamod.hana.HanaInstance.get_platform')
    def test_extract_pydbapi_error(self, mock_get_platform, mock_find_sap_folders, mock_compile):
        mock_get_platform.return_value = 'LINUX_X86_64'
        compile_mocked = mock.Mock()
        mock_compile.return_value = compile_mocked
        mock_find_sap_folders.side_effect = hanamod.SapFolderNotFoundError
        with pytest.raises(exceptions.CommandExecutionError) as err:
            pydbapi_file = hanamod.extract_pydbapi(
                'PYDBAPI.tar.gz', ['1234', '5678'], '/tmp/output', additional_extract_options='-l')

        mock_compile.assert_called_once_with('^HDB_CLIENT:20.*:LINUX_X86_64:.*')
        mock_find_sap_folders.assert_called_once_with(
            ['1234', '5678'], compile_mocked, recursion_level=1)
        assert 'HANA client not found' in str(err.value)

    def test_extract_pydbapi_software_folders_type_error(self):
        software_folders = '1234'
        with pytest.raises(TypeError) as err:
            pydbapi_file = hanamod.extract_pydbapi(
                'PYDBAPI.tar.gz', software_folders, '/tmp/output', additional_extract_options='-l')
        assert 'software_folders must be a list, not {} type'.format(
            type(software_folders).__name__) in str(err.value)
