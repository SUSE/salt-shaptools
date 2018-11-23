
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
from tests.support.mock import (
    NO_MOCK,
    NO_MOCK_REASON,
    MagicMock,
    patch
)

# Import Salt Libs
import salt.states.hanamod as hanamod


@skipIf(NO_MOCK, NO_MOCK_REASON)
class HanamodTestCase(TestCase, LoaderModuleMockMixin):
    '''
    Test cases for salt.states.hanamod
    '''
    def setup_loader_modules(self):
        return {hanamod: {'__opts__': {'test': False}}}

    # 'sr_primary_enabled' function tests

    def test_sr_primary_enabled_not_installed(self):
        '''
        Test to check sr_primary_enabled when hana is not installed
        '''
        name = 'SITE1'

        ret = {'name': name,
               'changes': {},
               'result': False,
               'comment': 'HANA is not installed properly with the provided data'}

        mock = MagicMock(return_value=False)
        with patch.dict(hanamod.__salt__, {'hana.is_installed': mock}):
            self.assertDictEqual(hanamod.sr_primary_enabled(
                name, 'pdr', '00', 'pass'), ret)

    def test_sr_primary_enabled(self):
        '''
        Test to check sr_primary_enabled when hana is already set as primary
        node
        '''
        name = 'SITE1'

        ret = {'name': name,
               'changes': {},
               'result': True,
               'comment': 'HANA node already set as primary and running'}

        mock = MagicMock(return_value=True)
        with patch.dict(hanamod.__salt__, {'hana.is_installed': mock}):
            mock_running = MagicMock(return_value=True)
            state = MagicMock()
            state.value = 1
            mock_state = MagicMock(return_value=state)

            with patch.dict(hanamod.__salt__, {'hana.is_running': mock_running,
                                               'hana.get_sr_state': mock_state}):
                self.assertDictEqual(hanamod.sr_primary_enabled(
                    name, 'pdr', '00', 'pass'), ret)

    def test_sr_primary_enabled_test(self):
        '''
        Test to check sr_primary_enabled when hana is already set as primary
        node in test mode
        '''
        name = 'SITE1'

        ret = {'name': name,
               'changes': {
                   'primary': name,
                   'backup': False,
                   'userkey': False
               },
               'result': None,
               'comment': '{} would be enabled as a primary node'.format(name)}

        mock = MagicMock(return_value=True)
        mock_running = MagicMock(return_value=True)
        state = MagicMock()
        state.value = 0
        mock_state = MagicMock(return_value=state)
        with patch.dict(hanamod.__salt__, {'hana.is_installed': mock,
                                           'hana.is_running': mock_running,
                                           'hana.get_sr_state': mock_state}):
            with patch.dict(hanamod.__opts__, {'test': True}):
                self.assertDictEqual(hanamod.sr_primary_enabled(
                    name, 'pdr', '00', 'pass'), ret)

    def test_sr_primary_enabled_basic(self):
        '''
        Test to check sr_primary_enabled when hana is already set as primary
        node with basic setup
        '''
        name = 'SITE1'

        ret = {'name': name,
               'changes': {
                   'primary': name
               },
               'result': True,
               'comment': 'HANA node set as {}'.format('PRIMARY')}

        mock = MagicMock(return_value=True)
        mock_running = MagicMock(return_value=False)
        state = MagicMock()
        state.value = 0
        state_primary = MagicMock()
        state_primary.value = 1
        state_primary.name = 'PRIMARY'
        mock_state = MagicMock(side_effect=[state, state_primary])
        mock_start = MagicMock()
        mock_enable = MagicMock()
        with patch.dict(hanamod.__salt__, {'hana.is_installed': mock,
                                           'hana.is_running': mock_running,
                                           'hana.get_sr_state': mock_state,
                                           'hana.start': mock_start,
                                           'hana.sr_enable_primary': mock_enable}):
            self.assertDictEqual(hanamod.sr_primary_enabled(
                name, 'pdr', '00', 'pass'), ret)
            mock_start.assert_called_once_with('pdr', '00', 'pass')
            mock_enable.assert_called_once_with(name, 'pdr', '00', 'pass')

    def test_sr_primary_enabled_complex(self):
        '''
        Test to check sr_primary_enabled when hana is already set as primary
        node with complex setup (backup and userkey created)
        '''
        name = 'SITE1'

        ret = {'name': name,
               'changes': {
                   'primary': name,
                   'userkey': 'key',
                   'backup': 'file'
               },
               'result': True,
               'comment': 'HANA node set as {}'.format('PRIMARY')}

        userkey = [
            {'key': 'key'},
            {'environment': 'env'},
            {'user': 'user'},
            {'password': 'password'},
            {'database': 'database'}
        ]

        backup = [
            {'user': 'user'},
            {'password': 'password'},
            {'database': 'database'},
            {'file': 'file'}
        ]

        mock = MagicMock(return_value=True)
        mock_running = MagicMock(return_value=False)
        state = MagicMock()
        state.value = 0
        state_primary = MagicMock()
        state_primary.value = 1
        state_primary.name = 'PRIMARY'
        mock_state = MagicMock(side_effect=[state, state_primary])
        mock_start = MagicMock()
        mock_enable = MagicMock()
        mock_userkey = MagicMock()
        mock_backup = MagicMock()
        with patch.dict(hanamod.__salt__, {'hana.is_installed': mock,
                                           'hana.is_running': mock_running,
                                           'hana.get_sr_state': mock_state,
                                           'hana.start': mock_start,
                                           'hana.sr_enable_primary': mock_enable,
                                           'hana.create_user_key': mock_userkey,
                                           'hana.create_backup': mock_backup}):
            self.assertDictEqual(hanamod.sr_primary_enabled(
                name, 'pdr', '00', 'pass', userkey=userkey, backup=backup), ret)
            mock_start.assert_called_once_with('pdr', '00', 'pass')
            mock_enable.assert_called_once_with(name, 'pdr', '00', 'pass')
            mock_userkey.assert_called_once_with(
                'key', 'env', 'user', 'password', 'database', 'pdr', '00', 'pass')
            mock_backup.assert_called_once_with(
                'user', 'password', 'database', 'file', 'pdr', '00', 'pass')

    def test_sr_primary_enabled_error(self):
        '''
        Test to check sr_primary_enabled when hana is already set as primary
        node and some hana command fail
        '''
        name = 'SITE1'

        ret = {'name': name,
               'changes': {},
               'result': False,
               'comment': 'hana command error'}

        mock = MagicMock(return_value=True)
        mock_running = MagicMock(return_value=False)
        state = MagicMock()
        state.value = 0
        state_primary = MagicMock()
        state_primary.value = 1
        state_primary.name = 'PRIMARY'
        mock_state = MagicMock(side_effect=[state, state_primary])
        mock_start = MagicMock()
        mock_enable = MagicMock(
            side_effect=exceptions.CommandExecutionError('hana command error'))
        with patch.dict(hanamod.__salt__, {'hana.is_installed': mock,
                                           'hana.is_running': mock_running,
                                           'hana.get_sr_state': mock_state,
                                           'hana.start': mock_start,
                                           'hana.sr_enable_primary': mock_enable}):
            self.assertDictEqual(hanamod.sr_primary_enabled(
                name, 'pdr', '00', 'pass'), ret)
            mock_start.assert_called_once_with('pdr', '00', 'pass')
            mock_enable.assert_called_once_with(name, 'pdr', '00', 'pass')

    # 'sr_secondary_registered' function tests

    def test_sr_secondary_registered_not_installed(self):
        '''
        Test to check sr_secondary_registered when hana is not installed
        '''
        name = 'SITE2'

        ret = {'name': name,
               'changes': {},
               'result': False,
               'comment': 'HANA is not installed properly with the provided data'}

        mock = MagicMock(return_value=False)
        with patch.dict(hanamod.__salt__, {'hana.is_installed': mock}):
            self.assertDictEqual(hanamod.sr_secondary_registered(
                name, 'pdr', '00', 'pass', 'hana01', '00', 'sync', 'logreplay'),
                ret)

    def test_sr_secondary_registered(self):
        '''
        Test to check sr_secondary_registered when hana is already set as secondary
        node
        '''
        name = 'SITE2'

        ret = {'name': name,
               'changes': {},
               'result': True,
               'comment': 'HANA node already set as secondary and running'}

        mock = MagicMock(return_value=True)
        with patch.dict(hanamod.__salt__, {'hana.is_installed': mock}):
            mock_running = MagicMock(return_value=True)
            state = MagicMock()
            state.value = 2
            mock_state = MagicMock(return_value=state)

            with patch.dict(hanamod.__salt__, {'hana.is_running': mock_running,
                                               'hana.get_sr_state': mock_state}):
                self.assertDictEqual(hanamod.sr_secondary_registered(
                    name, 'pdr', '00', 'pass', 'hana01', '00', 'sync',
                    'logreplay'), ret)

    def test_sr_secondary_registered_test(self):
        '''
        Test to check sr_secondary_registered when hana is already set as secondary
        node in test mode
        '''
        name = 'SITE2'

        ret = {'name': name,
               'changes': {
                   'secondary': name
               },
               'result': None,
               'comment': '{} would be registered as a secondary node'.format(name)}

        mock = MagicMock(return_value=True)
        mock_running = MagicMock(return_value=True)
        state = MagicMock()
        state.value = 0
        mock_state = MagicMock(return_value=state)
        with patch.dict(hanamod.__salt__, {'hana.is_installed': mock,
                                           'hana.is_running': mock_running,
                                           'hana.get_sr_state': mock_state}):
            with patch.dict(hanamod.__opts__, {'test': True}):
                self.assertDictEqual(hanamod.sr_secondary_registered(
                    name, 'pdr', '00', 'pass', 'hana01', '00', 'sync',
                    'logreplay'), ret)

    def test_sr_secondary_registered_basic(self):
        '''
        Test to check sr_secondary_registered when hana is already set as secondary
        node with basic setup
        '''
        name = 'SITE2'

        ret = {'name': name,
               'changes': {
                   'secondary': name
               },
               'result': True,
               'comment': 'HANA node set as {}'.format('SECONDARY')}

        mock = MagicMock(return_value=True)
        mock_running = MagicMock(return_value=True)
        state = MagicMock()
        state.value = 0
        state_secondary = MagicMock()
        state_secondary.value = 2
        state_secondary.name = 'SECONDARY'
        mock_state = MagicMock(side_effect=[state, state_secondary])
        mock_stop = MagicMock()
        mock_start = MagicMock()
        mock_register = MagicMock()
        with patch.dict(hanamod.__salt__, {'hana.is_installed': mock,
                                           'hana.is_running': mock_running,
                                           'hana.get_sr_state': mock_state,
                                           'hana.stop': mock_stop,
                                           'hana.start': mock_start,
                                           'hana.sr_register_secondary': mock_register}):
            self.assertDictEqual(hanamod.sr_secondary_registered(
                name, 'hana01', '00', 'sync',
                'logreplay', 'pdr', '00', 'pass'), ret)
            mock_stop.assert_called_once_with('pdr', '00', 'pass')
            mock_start.assert_called_once_with('pdr', '00', 'pass')
            mock_register.assert_called_once_with(
                name, 'hana01', '00', 'sync', 'logreplay', 'pdr', '00', 'pass')

    def test_sr_secondary_registered_error(self):
        '''
        Test to check sr_secondary_registered when hana is already set as secondary
        node and some hana command fail
        '''
        name = 'SITE2'

        ret = {'name': name,
               'changes': {},
               'result': False,
               'comment': 'hana command error'}

        mock = MagicMock(return_value=True)
        mock_running = MagicMock(return_value=False)
        state = MagicMock()
        state.value = 0
        mock_state = MagicMock(return_value=state)
        mock_register = MagicMock(
            side_effect=exceptions.CommandExecutionError('hana command error'))
        with patch.dict(hanamod.__salt__, {'hana.is_installed': mock,
                                           'hana.is_running': mock_running,
                                           'hana.get_sr_state': mock_state,
                                           'hana.sr_register_secondary': mock_register}):
            self.assertDictEqual(hanamod.sr_secondary_registered(
                name, 'hana01', '00', 'sync',
                'logreplay', 'pdr', '00', 'pass'), ret)
            mock_register.assert_called_once_with(
                name, 'hana01', '00', 'sync', 'logreplay', 'pdr', '00', 'pass')

    # 'sr_clean' function tests

    def test_sr_clean_not_installed(self):
        '''
        Test to check sr_clean when hana is not installed
        '''
        name = 'SITE1'

        ret = {'name': name,
               'changes': {},
               'result': False,
               'comment': 'HANA is not installed properly with the provided data'}

        mock = MagicMock(return_value=False)
        with patch.dict(hanamod.__salt__, {'hana.is_installed': mock}):
            self.assertDictEqual(hanamod.sr_clean(
                name, True, 'pdr', '00', 'pass'), ret)

    def test_sr_clean(self):
        '''
        Test to check sr_clean when hana is already disabled
        node
        '''
        name = 'SITE1'

        ret = {'name': name,
               'changes': {},
               'result': True,
               'comment': 'HANA node already clean'}

        mock = MagicMock(return_value=True)
        with patch.dict(hanamod.__salt__, {'hana.is_installed': mock}):
            mock_running = MagicMock(return_value=True)
            state = MagicMock()
            state.value = 0
            mock_state = MagicMock(return_value=state)

            with patch.dict(hanamod.__salt__, {'hana.is_running': mock_running,
                                               'hana.get_sr_state': mock_state}):
                self.assertDictEqual(hanamod.sr_clean(
                    name, True, 'pdr', '00', 'pass'), ret)

    def test_sr_clean_test(self):
        '''
        Test to check sr_clean when hana is already set as secondary
        node in test mode
        '''
        name = 'SITE1'

        ret = {'name': name,
               'changes': {
                   'disabled': name
               },
               'result': None,
               'comment': '{} would be clean'.format(name)}

        mock = MagicMock(return_value=True)
        mock_running = MagicMock(return_value=True)
        state = MagicMock()
        state.value = 1
        mock_state = MagicMock(return_value=state)
        with patch.dict(hanamod.__salt__, {'hana.is_installed': mock,
                                           'hana.is_running': mock_running,
                                           'hana.get_sr_state': mock_state}):
            with patch.dict(hanamod.__opts__, {'test': True}):
                self.assertDictEqual(hanamod.sr_clean(
                    name, True, 'pdr', '00', 'pass'), ret)

    def test_sr_clean_basic(self):
        '''
        Test to check sr_clean when hana is already set as secondary
        node with basic setup
        '''
        name = 'SITE1'

        ret = {'name': name,
               'changes': {
                   'disabled': name
               },
               'result': True,
               'comment': 'HANA node set as {}'.format('DISABLED')}

        mock = MagicMock(return_value=True)
        mock_running = MagicMock(return_value=True)
        state = MagicMock()
        state.value = 1
        state_disabled = MagicMock()
        state_disabled.value = 0
        state_disabled.name = 'DISABLED'
        mock_state = MagicMock(side_effect=[state, state_disabled])
        mock_stop = MagicMock()
        mock_clean = MagicMock()
        with patch.dict(hanamod.__salt__, {'hana.is_installed': mock,
                                           'hana.is_running': mock_running,
                                           'hana.get_sr_state': mock_state,
                                           'hana.stop': mock_stop,
                                           'hana.sr_cleanup': mock_clean}):
            self.assertDictEqual(hanamod.sr_clean(
                name, True, 'pdr', '00', 'pass'), ret)
            mock_stop.assert_called_once_with('pdr', '00', 'pass')
            mock_clean.assert_called_once_with(True, 'pdr', '00', 'pass')

    def test_sr_clean_error(self):
        '''
        Test to check sr_clean when hana is already set as secondary
        node and some hana command fail
        '''
        name = 'SITE1'

        ret = {'name': name,
               'changes': {},
               'result': False,
               'comment': 'hana command error'}

        mock = MagicMock(return_value=True)
        mock_running = MagicMock(return_value=False)
        state = MagicMock()
        state.value = 1
        mock_state = MagicMock(return_value=state)
        mock_clean = MagicMock(
            side_effect=exceptions.CommandExecutionError('hana command error'))
        with patch.dict(hanamod.__salt__, {'hana.is_installed': mock,
                                           'hana.is_running': mock_running,
                                           'hana.get_sr_state': mock_state,
                                           'hana.sr_cleanup': mock_clean}):
            self.assertDictEqual(hanamod.sr_clean(
                name, True, 'pdr', '00', 'pass'), ret)
            mock_clean.assert_called_once_with(True, 'pdr', '00', 'pass')
