
# -*- coding: utf-8 -*-
'''
    :codeauthor: Xabier Arbulu Insausti <xarbulu@suse.com>
'''

# Import Python Libs
from __future__ import absolute_import, print_function, unicode_literals

from salt import exceptions

# Import Salt Testing Libs
from tests.support.mixins import LoaderModuleMockMixin
from tests.support.unit import TestCase, skipIf
from tests.support.mock import (
    MagicMock,
    patch,
    NO_MOCK,
    NO_MOCK_REASON
)

# Import Salt Libs
import salt.modules.hanamod as hanamod

@skipIf(NO_MOCK, NO_MOCK_REASON)
class HanaModuleTest(TestCase):
    '''
    This class contains a set of functions that test salt.modules.hana.
    '''

    def test_is_installed_return_true(self):
        '''
        Test is_installed method
        '''
        mock_hana_inst = MagicMock()
        mock_hana_inst.is_installed.return_value = True
        mock_hana = MagicMock(return_value=mock_hana_inst)
        with patch.object(hanamod, '_init', mock_hana):
            self.assertTrue(hanamod.is_installed('prd', '00', 'pass'))
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
            self.assertFalse(hanamod.is_installed('prd', '00', 'pass'))
            mock_hana.assert_called_once_with('prd', '00', 'pass')
            mock_hana_inst.is_installed.assert_called_once_with()

    def test_is_running_return_true(self):
        '''
        Test is_running method
        '''
        mock_hana_inst = MagicMock()
        mock_hana_inst.is_running.return_value = True
        mock_hana = MagicMock(return_value=mock_hana_inst)
        with patch.object(hanamod, '_init', mock_hana):
            self.assertTrue(hanamod.is_running('prd', '00', 'pass'))
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
            self.assertFalse(hanamod.is_running('prd', '00', 'pass'))
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
            self.assertEqual(u'1.2.3', hanamod.get_version('prd', '00', 'pass'))
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
            with self.assertRaises(exceptions.CommandExecutionError) as err:
                hanamod.get_version('prd', '00', 'pass')
            mock_hana.assert_called_once_with('prd', '00', 'pass')
            mock_hana_inst.get_version.assert_called_once_with()
            self.assertTrue('hana error' in str(err.exception))

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
            with self.assertRaises(exceptions.CommandExecutionError) as err:
                hanamod.start('prd', '00', 'pass')
            mock_hana.assert_called_once_with('prd', '00', 'pass')
            mock_hana_inst.start.assert_called_once_with()
            self.assertTrue('hana error' in str(err.exception))

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
            with self.assertRaises(exceptions.CommandExecutionError) as err:
                hanamod.stop('prd', '00', 'pass')
            mock_hana.assert_called_once_with('prd', '00', 'pass')
            mock_hana_inst.stop.assert_called_once_with()
            self.assertTrue('hana error' in str(err.exception))

    def test_get_sr_state_return(self):
        '''
        Test get_sr_state method - return
        '''
        mock_hana_inst = MagicMock()
        mock_hana_inst.get_sr_state.return_value = 1
        mock_hana = MagicMock(return_value=mock_hana_inst)
        with patch.object(hanamod, '_init', mock_hana):
            self.assertEqual(1, hanamod.get_sr_state('prd', '00', 'pass'))
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
            with self.assertRaises(exceptions.CommandExecutionError) as err:
                hanamod.get_sr_state('prd', '00', 'pass')
            mock_hana.assert_called_once_with('prd', '00', 'pass')
            mock_hana_inst.get_sr_state.assert_called_once_with()
            self.assertTrue('hana error' in str(err.exception))

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
            with self.assertRaises(exceptions.CommandExecutionError) as err:
                hanamod.sr_enable_primary('NUE', 'prd', '00', 'pass')
            mock_hana.assert_called_once_with('prd', '00', 'pass')
            mock_hana_inst.sr_enable_primary.assert_called_once_with('NUE')
            self.assertTrue('hana error' in str(err.exception))

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
            with self.assertRaises(exceptions.CommandExecutionError) as err:
                hanamod.sr_disable_primary('prd', '00', 'pass')
            mock_hana.assert_called_once_with('prd', '00', 'pass')
            mock_hana_inst.sr_disable_primary.assert_called_once_with()
            self.assertTrue('hana error' in str(err.exception))

    def test_sr_register_secondary_return(self):
        '''
        Test sr_register_secondary method - return
        '''
        mock_hana_inst = MagicMock()
        mock_hana = MagicMock(return_value=mock_hana_inst)
        with patch.object(hanamod, '_init', mock_hana):
            hanamod.sr_register_secondary('PRAGUE', 'hana01', '00', 'sync',
                'logreplay', 'prd', '00', 'pass')
            mock_hana.assert_called_once_with('prd', '00', 'pass')
            mock_hana_inst.sr_register_secondary.assert_called_once_with(
                'PRAGUE', 'hana01', '00', 'sync', 'logreplay')

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
            with self.assertRaises(exceptions.CommandExecutionError) as err:
                hanamod.sr_register_secondary('PRAGUE', 'hana01', '00', 'sync',
                    'logreplay', 'prd', '00', 'pass')
            mock_hana.assert_called_once_with('prd', '00', 'pass')
            mock_hana_inst.sr_register_secondary.assert_called_once_with(
                'PRAGUE', 'hana01', '00', 'sync', 'logreplay')
            self.assertTrue('hana error' in str(err.exception))

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
            with self.assertRaises(exceptions.CommandExecutionError) as err:
                hanamod.sr_unregister_secondary('NUE', 'prd', '00', 'pass')
            mock_hana.assert_called_once_with('prd', '00', 'pass')
            mock_hana_inst.sr_unregister_secondary.assert_called_once_with(
                'NUE')
            self.assertTrue('hana error' in str(err.exception))

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
            with self.assertRaises(exceptions.CommandExecutionError) as err:
                hanamod.check_user_key('key', 'prd', '00', 'pass')
            mock_hana.assert_called_once_with('prd', '00', 'pass')
            mock_hana_inst.check_user_key.assert_called_once_with(
                'key')
            self.assertTrue('hana error' in str(err.exception))

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
            with self.assertRaises(exceptions.CommandExecutionError) as err:
                hanamod.create_user_key(
                'key', 'env', 'user', 'pass', 'db', 'prd', '00', 'pass')
            mock_hana.assert_called_once_with('prd', '00', 'pass')
            mock_hana_inst.create_user_key.assert_called_once_with(
                'key', 'env', 'user', 'pass', 'db')
            self.assertTrue('hana error' in str(err.exception))

    def test_create_backup_return(self):
        '''
        Test create_backup method - return
        '''
        mock_hana_inst = MagicMock()
        mock_hana = MagicMock(return_value=mock_hana_inst)
        with patch.object(hanamod, '_init', mock_hana):
            hanamod.create_backup(
                'key', 'pass', 'db', 'bakcup', 'prd', '00', 'pass')
            mock_hana.assert_called_once_with('prd', '00', 'pass')
            mock_hana_inst.create_backup.assert_called_once_with(
                'key', 'pass', 'db', 'bakcup')

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
            with self.assertRaises(exceptions.CommandExecutionError) as err:
                hanamod.create_backup(
                'key', 'pass', 'db', 'bakcup', 'prd', '00', 'pass')
            mock_hana.assert_called_once_with('prd', '00', 'pass')
            mock_hana_inst.create_backup.assert_called_once_with(
                'key', 'pass', 'db', 'bakcup')
            self.assertTrue('hana error' in str(err.exception))
