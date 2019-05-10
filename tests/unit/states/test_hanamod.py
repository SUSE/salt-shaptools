
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
import salt.states.hanamod as hanamod


@skipIf(NO_MOCK, NO_MOCK_REASON)
class HanamodTestCase(TestCase, LoaderModuleMockMixin):
    '''
    Test cases for salt.states.hanamod
    '''
    def setup_loader_modules(self):
        return {hanamod: {'__opts__': {'test': False}}}

    # 'installed' function tests

    def test_installed_installed(self):
        '''
        Test to check installed when hana is already installed
        '''

        ret = {'name': 'prd',
               'changes': {},
               'result': True,
               'comment': 'HANA is already installed'}

        mock_installed = MagicMock(return_value=True)
        with patch.dict(hanamod.__salt__, {'hana.is_installed': mock_installed}):
            assert hanamod.installed(
                'prd', '00', 'pass', '/software', 'root', 'pass') == ret

    def test_installed_test(self):
        '''
        Test to check installed in test mode
        '''

        ret = {'name': 'prd',
               'changes': {'sid': 'prd'},
               'result': None,
               'comment': '{} would be installed'.format('prd')}

        mock_installed = MagicMock(return_value=False)
        with patch.dict(hanamod.__salt__, {'hana.is_installed': mock_installed}):
            with patch.dict(hanamod.__opts__, {'test': True}):
                assert hanamod.installed(
                    'prd', '00', 'pass', '/software', 'root', 'pass') == ret

    def test_installed_config_file(self):
        '''
        Test to check installed when config file is imported
        '''

        ret = {'name': 'prd',
               'changes': {'sid': 'prd', 'config_file': 'hana.conf'},
               'result': True,
               'comment': 'HANA installed'}

        mock_installed = MagicMock(return_value=False)
        mock_cp = MagicMock()
        mock_update = MagicMock(return_value='hana_updated.conf')
        mock_install = MagicMock()
        mock_remove = MagicMock()
        with patch.dict(hanamod.__salt__, {'hana.is_installed': mock_installed,
                                           'cp.get_file': mock_cp,
                                           'hana.update_conf_file': mock_update,
                                           'hana.install': mock_install,
                                           'file.remove': mock_remove}):
            assert hanamod.installed(
                'prd', '00', 'pass', '/software',
                'root', 'pass', config_file='hana.conf',
                extra_parameters=[{'hostname': 'hana01'}]) == ret

            mock_cp.assert_called_once_with(
                path='hana.conf',
                dest=hanamod.TMP_CONFIG_FILE)
            mock_update.assert_called_once_with(
                conf_file=hanamod.TMP_CONFIG_FILE,
                extra_parameters={u'hostname': u'hana01'})
            mock_install.assert_called_once_with(
                software_path='/software',
                conf_file='hana_updated.conf',
                root_user='root',
                root_password='pass')
            mock_remove.assert_has_calls([
                mock.call(hanamod.TMP_CONFIG_FILE),
                mock.call('{}.xml'.format(hanamod.TMP_CONFIG_FILE))
            ])

    def test_installed_dump(self):
        '''
        Test to check installed when new config file is created
        '''

        ret = {'name': 'prd',
               'changes': {'sid': 'prd', 'config_file': 'new'},
               'result': True,
               'comment': 'HANA installed'}

        mock_installed = MagicMock(return_value=False)
        mock_create = MagicMock(return_value='hana_created.conf')
        mock_update = MagicMock(return_value='hana_updated.conf')
        mock_install = MagicMock()
        mock_remove = MagicMock()
        with patch.dict(hanamod.__salt__, {'hana.is_installed': mock_installed,
                                           'hana.create_conf_file': mock_create,
                                           'hana.update_conf_file': mock_update,
                                           'hana.install': mock_install,
                                           'file.remove': mock_remove}):
            assert hanamod.installed(
                'prd', 0, 'pass', '/software',
                'root', 'pass',
                system_user_password='sys_pass',
                sapadm_password='pass',
                extra_parameters=[{'hostname': 'hana01'}]) == ret

            mock_create.assert_called_once_with(
                software_path='/software',
                conf_file=hanamod.TMP_CONFIG_FILE,
                root_user='root',
                root_password='pass')
            mock_update.assert_has_calls([
                mock.call(
                    conf_file='hana_created.conf', sid='PRD', number='00',
                    password='pass', root_user='root', root_password='pass',
                    sapadm_password='pass', system_user_password='sys_pass'),
                mock.call(
                    conf_file='hana_updated.conf',
                    extra_parameters={u'hostname': u'hana01'})
            ])

            mock_install.assert_called_once_with(
                software_path='/software',
                conf_file='hana_updated.conf',
                root_user='root',
                root_password='pass')
            mock_remove.assert_has_calls([
                mock.call(hanamod.TMP_CONFIG_FILE),
                mock.call('{}.xml'.format(hanamod.TMP_CONFIG_FILE))
            ])

    def test_installed_invalid_params(self):
        '''
        Test to check installed when install fails
        '''

        ret = {'name': 'prd',
               'changes': {},
               'result': False,
               'comment': 'If config_file is not provided '
                          'system_user_password and sapadm_password are mandatory'}

        mock_installed = MagicMock(return_value=False)

        mock_remove = MagicMock()
        with patch.dict(hanamod.__salt__, {'hana.is_installed': mock_installed,
                                           'file.remove': mock_remove}):
            assert hanamod.installed(
                'prd', '00', 'pass', '/software',
                'root', 'pass') == ret

            mock_remove.assert_has_calls([
                mock.call(hanamod.TMP_CONFIG_FILE),
                mock.call('{}.xml'.format(hanamod.TMP_CONFIG_FILE))
            ])

    def test_installed_error(self):
        '''
        Test to check installed when install fails
        '''

        ret = {'name': 'prd',
               'changes': {'config_file': 'new'},
               'result': False,
               'comment': 'hana command error'}

        mock_installed = MagicMock(return_value=False)
        mock_create = MagicMock(return_value='hana_created.conf')
        mock_update = MagicMock(return_value='hana_updated.conf')
        mock_install = MagicMock(
            side_effect=exceptions.CommandExecutionError('hana command error'))
        mock_remove = MagicMock()
        with patch.dict(hanamod.__salt__, {'hana.is_installed': mock_installed,
                                           'hana.create_conf_file': mock_create,
                                           'hana.update_conf_file': mock_update,
                                           'hana.install': mock_install,
                                           'file.remove': mock_remove}):
            assert hanamod.installed(
                'prd', '00', 'pass', '/software',
                'root', 'pass',
                sapadm_password='pass',
                system_user_password='sys_pass') == ret

            mock_create.assert_called_once_with(
                software_path='/software',
                conf_file=hanamod.TMP_CONFIG_FILE,
                root_user='root',
                root_password='pass')
            mock_update.assert_called_once_with(
                    conf_file='hana_created.conf', sid='PRD', number='00',
                    password='pass', root_user='root', root_password='pass',
                    sapadm_password='pass', system_user_password='sys_pass')

            mock_install.assert_called_once_with(
                software_path='/software',
                conf_file='hana_updated.conf',
                root_user='root',
                root_password='pass')
            mock_remove.assert_has_calls([
                mock.call(hanamod.TMP_CONFIG_FILE),
                mock.call('{}.xml'.format(hanamod.TMP_CONFIG_FILE))
            ])

    # 'uninstalled' function tests

    def test_uninstalled_uinstalled(self):
        '''
        Test to check uninstalled when hana is already installed
        '''

        ret = {'name': 'prd',
               'changes': {},
               'result': True,
               'comment': 'HANA already not installed'}

        mock_installed = MagicMock(return_value=False)
        with patch.dict(hanamod.__salt__, {'hana.is_installed': mock_installed}):
            assert hanamod.uninstalled(
                'prd', '00', 'pass', 'root', 'pass') == ret

    def test_uninstalled_test(self):
        '''
        Test to check uninstalled in test mode
        '''

        ret = {'name': 'prd',
               'changes': {'sid': 'prd'},
               'result': None,
               'comment': '{} would be uninstalled'.format('prd')}

        mock_installed = MagicMock(return_value=True)
        with patch.dict(hanamod.__salt__, {'hana.is_installed': mock_installed}):
            with patch.dict(hanamod.__opts__, {'test': True}):
                assert hanamod.uninstalled(
                    'prd', '00', 'pass', 'root', 'pass') == ret

    def test_uninstalled(self):
        '''
        Test to check uninstalled when hana is installed
        '''

        ret = {'name': 'prd',
               'changes': {'sid': 'prd'},
               'result': True,
               'comment': 'HANA uninstalled'}

        mock_is_installed = MagicMock(return_value=True)
        mock_uninstall = MagicMock()
        with patch.dict(hanamod.__salt__, {'hana.is_installed': mock_is_installed,
                                           'hana.uninstall': mock_uninstall}):
            assert hanamod.uninstalled(
                'prd', '00', 'pass', 'root', 'pass',
                installation_folder='/hana') == ret
            mock_uninstall.assert_called_once_with(
                root_user='root', root_password='pass',
                sid='prd', inst='00', password='pass',
                installation_folder='/hana')

    def test_uninstalled_error(self):
        '''
        Test to check uninstalled when hana uninstall method fails
        '''

        ret = {'name': 'prd',
               'changes': {},
               'result': False,
               'comment': 'hana command error'}

        mock_installed = MagicMock(return_value=True)
        mock_uninstall = MagicMock(
            side_effect=exceptions.CommandExecutionError('hana command error'))
        with patch.dict(hanamod.__salt__, {'hana.is_installed': mock_installed,
                                           'hana.uninstall': mock_uninstall}):
            assert hanamod.uninstalled(
                'prd', '00', 'pass', 'root', 'pass',
                installation_folder='/hana') == ret
            mock_uninstall.assert_called_once_with(
                root_user='root', root_password='pass',
                sid='prd', inst='00', password='pass',
                installation_folder='/hana')

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

        mock_installed = MagicMock(return_value=False)
        with patch.dict(hanamod.__salt__, {'hana.is_installed': mock_installed}):
            assert hanamod.sr_primary_enabled(
                name, 'pdr', '00', 'pass') == ret

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

        mock_installed = MagicMock(return_value=True)
        with patch.dict(hanamod.__salt__, {'hana.is_installed': mock_installed}):
            mock_running = MagicMock(return_value=True)
            mock_state = MagicMock(return_value='PRIMARY')

            with patch.dict(hanamod.__salt__, {'hana.is_running': mock_running,
                                               'hana.get_sr_state': mock_state}):
                assert hanamod.sr_primary_enabled(
                    name, 'pdr', '00', 'pass') == ret

    def test_sr_primary_enabled_test(self):
        '''
        Test to check sr_primary_enabled in test mode
        '''
        name = 'SITE1'

        ret = {'name': name,
               'changes': {
                   'primary': name,
                   'backup': None,
                   'userkey': None
               },
               'result': None,
               'comment': '{} would be enabled as a primary node'.format(name)}

        mock_installed = MagicMock(return_value=True)
        mock_running = MagicMock(return_value=True)
        mock_state = MagicMock()
        with patch.dict(hanamod.__salt__, {'hana.is_installed': mock_installed,
                                           'hana.is_running': mock_running,
                                           'hana.get_sr_state': mock_state}):
            with patch.dict(hanamod.__opts__, {'test': True}):
                assert hanamod.sr_primary_enabled(
                    name, 'pdr', '00', 'pass') == ret

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

        mock_installed = MagicMock(return_value=True)
        mock_running = MagicMock(return_value=True)
        mock_state = MagicMock(side_effect=['DISABLED', 'PRIMARY'])
        mock_enable = MagicMock()
        with patch.dict(hanamod.__salt__, {'hana.is_installed': mock_installed,
                                           'hana.is_running': mock_running,
                                           'hana.get_sr_state': mock_state,
                                           'hana.sr_enable_primary': mock_enable}):
            assert hanamod.sr_primary_enabled(
                name, 'pdr', '00', 'pass') == ret
            mock_enable.assert_called_once_with(
                name=name,
                sid='pdr',
                inst='00',
                password='pass')

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
            {'key_name': 'key'},
            {'environment': 'env'},
            {'user_name': 'user'},
            {'user_password': 'password'},
            {'database': 'database'}
        ]

        backup = [
            {'key_name': 'key'},
            {'user_name': 'user'},
            {'user_password': 'password'},
            {'database': 'database'},
            {'file': 'file'}
        ]

        mock_installed = MagicMock(return_value=True)
        mock_running = MagicMock(return_value=False)
        mock_state = MagicMock(side_effect=['DISABLED', 'PRIMARY'])
        mock_start = MagicMock()
        mock_enable = MagicMock()
        mock_userkey = MagicMock()
        mock_backup = MagicMock()
        with patch.dict(hanamod.__salt__, {'hana.is_installed': mock_installed,
                                           'hana.is_running': mock_running,
                                           'hana.get_sr_state': mock_state,
                                           'hana.start': mock_start,
                                           'hana.sr_enable_primary': mock_enable,
                                           'hana.create_user_key': mock_userkey,
                                           'hana.create_backup': mock_backup}):
            assert hanamod.sr_primary_enabled(
                name, 'pdr', '00', 'pass', userkey=userkey, backup=backup) == ret
            mock_start.assert_called_once_with(
                sid='pdr',
                inst='00',
                password='pass')
            mock_enable.assert_called_once_with(
                name=name,
                sid='pdr',
                inst='00',
                password='pass')
            mock_userkey.assert_called_once_with(
                key_name='key',
                environment='env',
                user_name='user',
                user_password='password',
                database='database',
                sid='pdr',
                inst='00',
                password='pass')
            mock_backup.assert_called_once_with(
                key_name='key',
                user_name='user',
                user_password='password',
                database='database',
                backup_name='file',
                sid='pdr',
                inst='00',
                password='pass')

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

        mock_installed = MagicMock(return_value=True)
        mock_running = MagicMock(return_value=False)
        mock_state = MagicMock(side_effect=['DISABLED', 'PRIMARY'])
        mock_start = MagicMock()
        mock_enable = MagicMock(
            side_effect=exceptions.CommandExecutionError('hana command error'))
        with patch.dict(hanamod.__salt__, {'hana.is_installed': mock_installed,
                                           'hana.is_running': mock_running,
                                           'hana.get_sr_state': mock_state,
                                           'hana.start': mock_start,
                                           'hana.sr_enable_primary': mock_enable}):
            assert hanamod.sr_primary_enabled(
                name, 'pdr', '00', 'pass') == ret
            mock_start.assert_called_once_with(
                sid='pdr',
                inst='00',
                password='pass')
            mock_enable.assert_called_once_with(
                name=name,
                sid='pdr',
                inst='00',
                password='pass')

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

        mock_installed = MagicMock(return_value=False)
        with patch.dict(hanamod.__salt__, {'hana.is_installed': mock_installed}):
            assert hanamod.sr_secondary_registered(
                name, 'pdr', '00', 'pass', 'hana01', '00', 'sync',
                'logreplay') == ret

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

        mock_installed = MagicMock(return_value=True)
        with patch.dict(hanamod.__salt__, {'hana.is_installed': mock_installed}):
            mock_running = MagicMock(return_value=True)
            mock_state = MagicMock(return_value='SECONDARY')

            with patch.dict(hanamod.__salt__, {'hana.is_running': mock_running,
                                               'hana.get_sr_state': mock_state}):
                assert hanamod.sr_secondary_registered(
                    name, 'pdr', '00', 'pass', 'hana01', '00', 'sync',
                    'logreplay') == ret

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

        mock_installed = MagicMock(return_value=True)
        mock_running = MagicMock(return_value=True)
        mock_state = MagicMock(return_value='DISABLED')
        with patch.dict(hanamod.__salt__, {'hana.is_installed': mock_installed,
                                           'hana.is_running': mock_running,
                                           'hana.get_sr_state': mock_state}):
            with patch.dict(hanamod.__opts__, {'test': True}):
                assert hanamod.sr_secondary_registered(
                    name, 'pdr', '00', 'pass', 'hana01', '00', 'sync',
                    'logreplay') == ret

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

        mock_installed = MagicMock(return_value=True)
        mock_running = MagicMock(return_value=True)
        mock_state = MagicMock(side_effect=['DISABLED', 'SECONDARY'])
        mock_stop = MagicMock()
        mock_start = MagicMock()
        mock_register = MagicMock()
        with patch.dict(hanamod.__salt__, {'hana.is_installed': mock_installed,
                                           'hana.is_running': mock_running,
                                           'hana.get_sr_state': mock_state,
                                           'hana.stop': mock_stop,
                                           'hana.start': mock_start,
                                           'hana.sr_register_secondary': mock_register}):
            assert hanamod.sr_secondary_registered(
                name, 'hana01', '00', 'sync',
                'logreplay', 'pdr', '00', 'pass') == ret
            mock_stop.assert_called_once_with(
                sid='pdr',
                inst='00',
                password='pass')
            mock_start.assert_called_once_with(
                sid='pdr',
                inst='00',
                password='pass')
            mock_register.assert_called_once_with(
                name=name,
                remote_host='hana01',
                remote_instance='00',
                replication_mode='sync',
                operation_mode='logreplay',
                sid='pdr',
                inst='00',
                password='pass')

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

        mock_installed = MagicMock(return_value=True)
        mock_running = MagicMock(return_value=False)
        mock_state = MagicMock(return_value='SECONDARY')
        mock_register = MagicMock(
            side_effect=exceptions.CommandExecutionError('hana command error'))
        with patch.dict(hanamod.__salt__, {'hana.is_installed': mock_installed,
                                           'hana.is_running': mock_running,
                                           'hana.get_sr_state': mock_state,
                                           'hana.sr_register_secondary': mock_register}):
            assert hanamod.sr_secondary_registered(
                name, 'hana01', '00', 'sync',
                'logreplay', 'pdr', '00', 'pass') == ret
            mock_register.assert_called_once_with(
                name=name,
                remote_host='hana01',
                remote_instance='00',
                replication_mode='sync',
                operation_mode='logreplay',
                sid='pdr',
                inst='00',
                password='pass')

    # 'sr_clean' function tests

    def test_sr_clean_not_installed(self):
        '''
        Test to check sr_clean when hana is not installed
        '''
        name = 'pdr'

        ret = {'name': name,
               'changes': {},
               'result': False,
               'comment': 'HANA is not installed properly with the provided data'}

        mock_installed = MagicMock(return_value=False)
        with patch.dict(hanamod.__salt__, {'hana.is_installed': mock_installed}):
            assert hanamod.sr_clean(
                'pdr', '00', 'pass', True) == ret

    def test_sr_clean(self):
        '''
        Test to check sr_clean when hana is already disabled
        node
        '''
        name = 'pdr'

        ret = {'name': name,
               'changes': {},
               'result': True,
               'comment': 'HANA node already clean'}

        mock_installed = MagicMock(return_value=True)
        with patch.dict(hanamod.__salt__, {'hana.is_installed': mock_installed}):
            mock_running = MagicMock(return_value=True)
            mock_state = MagicMock(return_value='DISABLED')

            with patch.dict(hanamod.__salt__, {'hana.is_running': mock_running,
                                               'hana.get_sr_state': mock_state}):
                assert hanamod.sr_clean(
                    'pdr', '00', 'pass', True) == ret

    def test_sr_clean_test(self):
        '''
        Test to check sr_clean when hana is not disabled
        node in test mode
        '''
        name = 'pdr'

        ret = {'name': name,
               'changes': {
                   'disabled': name
               },
               'result': None,
               'comment': '{} would be clean'.format(name)}

        mock_installed = MagicMock(return_value=True)
        mock_running = MagicMock(return_value=True)
        mock_state = MagicMock(return_value='PRIMARY')
        with patch.dict(hanamod.__salt__, {'hana.is_installed': mock_installed,
                                           'hana.is_running': mock_running,
                                           'hana.get_sr_state': mock_state}):
            with patch.dict(hanamod.__opts__, {'test': True}):
                assert hanamod.sr_clean(
                    'pdr', '00', 'pass', True) == ret

    def test_sr_clean_basic(self):
        '''
        Test to check sr_clean when hana is already set as secondary
        node with basic setup
        '''
        name = 'pdr'

        ret = {'name': name,
               'changes': {
                   'disabled': name
               },
               'result': True,
               'comment': 'HANA node set as {}'.format('DISABLED')}

        mock_installed = MagicMock(return_value=True)
        mock_running = MagicMock(return_value=True)
        mock_state = MagicMock(side_effect=['PRIMARY', 'DISABLED'])
        mock_stop = MagicMock()
        mock_clean = MagicMock()
        with patch.dict(hanamod.__salt__, {'hana.is_installed': mock_installed,
                                           'hana.is_running': mock_running,
                                           'hana.get_sr_state': mock_state,
                                           'hana.stop': mock_stop,
                                           'hana.sr_cleanup': mock_clean}):
            assert hanamod.sr_clean(
                'pdr', '00', 'pass', True) == ret
            mock_stop.assert_called_once_with(
                sid='pdr',
                inst='00',
                password='pass')
            mock_clean.assert_called_once_with(
                sid='pdr',
                inst='00',
                password='pass',
                force=True)

    def test_sr_clean_error(self):
        '''
        Test to check sr_clean when hana is already not disabled
        node and some hana command fail
        '''
        name = 'pdr'

        ret = {'name': name,
               'changes': {},
               'result': False,
               'comment': 'hana command error'}

        mock_insatlled = MagicMock(return_value=True)
        mock_running = MagicMock(return_value=False)
        state = MagicMock()
        mock_state = MagicMock(return_value=state)
        mock_clean = MagicMock(
            side_effect=exceptions.CommandExecutionError('hana command error'))
        with patch.dict(hanamod.__salt__, {'hana.is_installed': mock_insatlled,
                                           'hana.is_running': mock_running,
                                           'hana.get_sr_state': mock_state,
                                           'hana.sr_cleanup': mock_clean}):
            assert hanamod.sr_clean(
                'pdr', '00', 'pass', True) == ret
            mock_clean.assert_called_once_with(
                sid='pdr',
                inst='00',
                password='pass',
                force=True)

    # 'memory_resources_updated' function tests

    def test_memory_resources_updated_not_installed(self):
        '''
        Test to check memory_resources_updated when hana is not installed
        '''
        name = 'prd'

        ret = {'name': name,
               'changes': {},
               'result': False,
               'comment': 'HANA is not installed properly with the provided data'}

        mock_installed = MagicMock(return_value=False)
        with patch.dict(hanamod.__salt__, {'hana.is_installed': mock_installed}):
            assert hanamod.memory_resources_updated(
                name=name, sid='prd', inst='00', password='pass',
                global_allocation_limit='25000', preload_column_tables=False,
                user_name='key_user', user_password='key_password') == ret
    
    def test_memory_resources_updated_test(self):
        '''
        Test to check memory_resources_updated in test mode
        '''
        name = 'prd'

        ret = {'name': name,
               'changes': {
                   'sid': 'prd',
                   'global_allocation_limit' : '25000',
                   'preload_column_tables' : False
               },
               'result': None,
               'comment': 'Memory resources would be updated on {}-{}'.format(
                   name, 'prd')}

        mock_installed = MagicMock(return_value=True)
        mock_running = MagicMock(return_value=True)
        with patch.dict(hanamod.__salt__, {'hana.is_installed': mock_installed,
                                           'hana.is_running': mock_running}):
            with patch.dict(hanamod.__opts__, {'test': True}):
                assert hanamod.memory_resources_updated(
                    name=name, sid='prd', inst='00', password='pass',
                    global_allocation_limit='25000', preload_column_tables=False,
                    user_name='key_user', user_password='key_password') == ret

    def test_memory_resources_updated_basic(self):
        '''
        Test to check memory_resources_updated with basic setup
        '''
        name = 'prd'

        ret = {'name': name,
               'changes': {
                   'sid': 'prd',
                   'global_allocation_limit': '25000',
                   'preload_column_tables': False
               },
               'result': True,
               'comment': 'Memory resources updated on {}-{}'.format(name, 'prd')}

        mock_installed = MagicMock(return_value=True)
        mock_running = MagicMock(return_value=True)
        mock_stop = MagicMock()
        mock_start = MagicMock()
        mock_set_ini_parameter = MagicMock()
        ini_parameter_values = [{'section_name': 'system_replication',
                                 'parameter_name': 'preload_column_tables',
                                 'parameter_value': False},
                                {'section_name': 'memorymanager',
                                 'parameter_name': 'global_allocation_limit',
                                 'parameter_value': '25000'}]

        with patch.dict(hanamod.__salt__,
                        {'hana.is_installed': mock_installed,
                         'hana.is_running': mock_running,
                         'hana.set_ini_parameter': mock_set_ini_parameter,
                         'hana.stop': mock_stop,
                         'hana.start': mock_start}):
            assert hanamod.memory_resources_updated(
                    name=name, sid='prd', inst='00', password='pass',
                    global_allocation_limit='25000', preload_column_tables=False,
                    user_name='key_user', user_password='key_password') == ret
            mock_stop.assert_called_once_with(
                sid='prd',
                inst='00',
                password='pass')
            mock_start.assert_called_once_with(
                sid='prd',
                inst='00',
                password='pass')
            mock_set_ini_parameter.assert_called_once_with(
                ini_parameter_values=ini_parameter_values,
                database='SYSTEMDB',
                file_name='global.ini',
                layer='SYSTEM',
                layer_name=None,
                reconfig=True,
                user_name='key_user',
                user_password='key_password',
                sid='prd',
                inst='00',
                password='pass')

    def test_memory_resources_updated_error(self):
        '''
        Test to check memory_resources_updated when some hana command fails
        '''
        name = 'prd'

        ret = {'name': name,
               'changes': {},
               'result': False,
               'comment': 'hana command error'}

        mock_installed = MagicMock(return_value=True)
        mock_running = MagicMock(return_value=False)
        mock_stop = MagicMock()
        mock_start = MagicMock()
        mock_set_ini_parameter = MagicMock(
            side_effect=exceptions.CommandExecutionError('hana command error'))
        ini_parameter_values = [{'section_name': 'system_replication',
                                 'parameter_name': 'preload_column_tables',
                                 'parameter_value': False},
                                {'section_name': 'memorymanager',
                                 'parameter_name': 'global_allocation_limit',
                                 'parameter_value': '25000'}]

        with patch.dict(hanamod.__salt__,
                        {'hana.is_installed': mock_installed,
                         'hana.is_running': mock_running,
                         'hana.set_ini_parameter': mock_set_ini_parameter,
                         'hana.stop': mock_stop,
                         'hana.start': mock_start}):
            assert hanamod.memory_resources_updated(
                    name=name, sid='prd', inst='00', password='pass',
                    global_allocation_limit='25000', preload_column_tables=False,
                    user_name='key_user', user_password='key_password') == ret
            mock_set_ini_parameter.assert_called_once_with(
                ini_parameter_values=ini_parameter_values,
                database='SYSTEMDB',
                file_name='global.ini',
                layer='SYSTEM',
                layer_name=None,
                reconfig=True,
                user_name='key_user',
                user_password='key_password',
                sid='prd',
                inst='00',
                password='pass')