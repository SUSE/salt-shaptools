
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
import salt.states.hanamod as hanamod


class HanamodTestCase(TestCase, LoaderModuleMockMixin):
    '''
    Test cases for salt.states.hanamod
    '''
    def setup_loader_modules(self):
        return {hanamod: {'__opts__': {'test': False}}}

    # 'available' function tests

    def test_available_test(self):
        '''
        Test to check available in test mode
        '''

        ret = {'name': '192.168.10.15:30015',
               'changes': {},
               'result': None,
               'comment': 'hana connection would be checked'}

        with patch.dict(hanamod.__opts__, {'test': True}):
            assert hanamod.available(
                '192.168.10.15', 30015, 'SYSTEM', 'pass', 60, 5) == ret

    def test_available_true(self):
        '''
        Test to check available when it returns True
        '''

        ret = {'name': '192.168.10.15:30015',
               'changes': {},
               'result': True,
               'comment': 'HANA is available'}

        mock_wait = mock.MagicMock()

        with patch.dict(hanamod.__salt__, {'hana.wait_for_connection': mock_wait}):
            assert hanamod.available(
                '192.168.10.15', 30015, 'SYSTEM', 'pass', 60, 5) == ret
        mock_wait.assert_called_once_with(
            host='192.168.10.15',
            port=30015,
            user='SYSTEM',
            password='pass',
            timeout=60,
            interval=5
        )

    def test_available_false(self):
        '''
        Test to check available when it returns False
        '''

        ret = {'name': '192.168.10.15:30015',
               'changes': {},
               'result': False,
               'comment': 'error'}

        mock_wait = mock.MagicMock(side_effect=exceptions.CommandExecutionError('error'))

        with patch.dict(hanamod.__salt__, {'hana.wait_for_connection': mock_wait}):
            assert hanamod.available(
                '192.168.10.15', 30015, 'SYSTEM', 'pass', 60, 5) == ret
        mock_wait.assert_called_once_with(
            host='192.168.10.15',
            port=30015,
            user='SYSTEM',
            password='pass',
            timeout=60,
            interval=5
        )

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
        Test to check installed when config file is imported and XML password file is created
        '''

        ret = {'name': 'prd',
               'changes': {'sid': 'prd', 'config_file': 'hana.conf', 'hdb_pwd_file': 'new'},
               'result': True,
               'comment': 'HANA installed'}

        mock_installed = MagicMock(return_value=False)
        mock_cp = MagicMock()
        mock_mv = MagicMock()
        mock_create_xml = MagicMock(return_value='temp.conf')
        mock_update_xml = MagicMock(return_value=hanamod.TMP_HDB_PWD_FILE)
        mock_update = MagicMock(return_value='hana_updated.conf')
        mock_install = MagicMock()
        mock_remove = MagicMock()
        with patch.dict(hanamod.__salt__, {'hana.is_installed': mock_installed,
                                           'cp.get_file': mock_cp,
                                           'file.move': mock_mv,
                                           'hana.create_conf_file': mock_create_xml,
                                           'hana.update_hdb_pwd_file': mock_update_xml,
                                           'hana.update_conf_file': mock_update,
                                           'hana.install': mock_install,
                                           'file.remove': mock_remove}):
            assert hanamod.installed(
                'prd', '00', 'pass', '/software',
                'root', config_file='hana.conf', root_password='Test1234',
                sapadm_password='Test1234', system_user_password='Test1234',
                extra_parameters=[{'hostname': 'hana01', 'org_manager_password': 'pass'}]) == ret

            mock_create_xml.assert_called_once_with(
                software_path='/software',
                conf_file=hanamod.TMP_CONFIG_FILE,
                root_user='root',
                root_password='Test1234')
            mock_mv.assert_called_once_with(
                src='/tmp/hana.conf.xml',
                dst=hanamod.TMP_HDB_PWD_FILE)
            mock_update_xml.assert_called_once_with(
                hdb_pwd_file=hanamod.TMP_HDB_PWD_FILE, root_password='Test1234',
                password='pass', sapadm_password='Test1234', system_user_password='Test1234',
                org_manager_password='pass')
            mock_cp.assert_called_once_with(
                path='hana.conf',
                dest=hanamod.TMP_CONFIG_FILE)
            mock_update.assert_called_once_with(
                conf_file=hanamod.TMP_CONFIG_FILE,
                hostname='hana01')
            mock_install.assert_called_once_with(
                software_path='/software',
                conf_file='hana_updated.conf',
                root_user='root', root_password='Test1234',
                hdb_pwd_file=hanamod.TMP_HDB_PWD_FILE)
            mock_remove.assert_has_calls([
                mock.call('{}.xml'.format(hanamod.TMP_CONFIG_FILE))
            ])

    def test_installed_dump(self):
        '''
        Test to check installed when new config file is created and XML password file is imported
        '''

        ret = {'name': 'prd',
               'changes': {'sid': 'prd', 'config_file': 'new', 'hdb_pwd_file': 'passwords.xml'},
               'result': True,
               'comment': 'HANA installed'}

        mock_installed = MagicMock(return_value=False)
        mock_cp = MagicMock()
        mock_create = MagicMock(return_value='hana_created.conf')
        mock_update = MagicMock(return_value='hana_updated.conf')
        mock_install = MagicMock()
        mock_remove = MagicMock()
        with patch.dict(hanamod.__salt__, {'hana.is_installed': mock_installed,
                                           'cp.get_file': mock_cp,
                                           'hana.create_conf_file': mock_create,
                                           'hana.update_conf_file': mock_update,
                                           'hana.install': mock_install,
                                           'file.remove': mock_remove}):
            assert hanamod.installed(
                'prd', 0, 'pass', '/software',
                'root', 'pass',
                hdb_pwd_file='passwords.xml',
                extra_parameters=[{'hostname': 'hana01'}]) == ret

            mock_cp.assert_called_once_with(
                path='passwords.xml',
                dest=hanamod.TMP_HDB_PWD_FILE)
            mock_create.assert_called_once_with(
                software_path='/software',
                conf_file=hanamod.TMP_CONFIG_FILE,
                root_user='root',
                root_password='pass')
            mock_update.assert_has_calls([
                mock.call(
                    conf_file='hana_created.conf', sid='PRD', number='00',
                    root_user='root'),
                mock.call(
                    conf_file='hana_updated.conf',
                    hostname='hana01')
            ])

            mock_install.assert_called_once_with(
                software_path='/software',
                conf_file='hana_updated.conf',
                root_user='root',
                root_password='pass',
                hdb_pwd_file=hanamod.TMP_HDB_PWD_FILE)
            mock_remove.assert_has_calls([
                mock.call('{}.xml'.format(hanamod.TMP_CONFIG_FILE))
            ])

    def test_installed_invalid_params(self):
        '''
        Test to check installed when install fails
        '''

        ret = {'name': 'prd',
               'changes': {},
               'result': False,
               'comment': 'If XML password file is not provided '
                          'system_user_password and sapadm_password are mandatory'}

        mock_installed = MagicMock(return_value=False)
        mock_create = MagicMock(return_value='hana_created.conf')

        mock_remove = MagicMock()
        with patch.dict(hanamod.__salt__, {'hana.is_installed': mock_installed,
                                           'hana.create_conf_file': mock_create,
                                           'file.remove': mock_remove}):
            assert hanamod.installed(
                'prd', '00', 'pass', '/software',
                'root', 'pass') == ret

            mock_create.assert_called_once_with(
                software_path='/software',
                conf_file=hanamod.TMP_CONFIG_FILE,
                root_user='root',
                root_password='pass')

            mock_remove.assert_has_calls([
                mock.call('{}.xml'.format(hanamod.TMP_CONFIG_FILE))
            ])

    def test_installed_error(self):
        '''
        Test to check installed when install fails
        '''

        ret = {'name': 'prd',
               'changes': {'config_file': 'new', 'hdb_pwd_file': 'passwords.xml'},
               'result': False,
               'comment': 'hana command error'}

        mock_installed = MagicMock(return_value=False)
        mock_cp = MagicMock()
        mock_create = MagicMock(return_value='hana_created.conf')
        mock_update = MagicMock(return_value='hana_updated.conf')
        mock_install = MagicMock(
            side_effect=exceptions.CommandExecutionError('hana command error'))
        mock_remove = MagicMock()
        with patch.dict(hanamod.__salt__, {'hana.is_installed': mock_installed,
                                           'cp.get_file': mock_cp,
                                           'hana.create_conf_file': mock_create,
                                           'hana.update_conf_file': mock_update,
                                           'hana.install': mock_install,
                                           'file.remove': mock_remove}):
            assert hanamod.installed(
                'prd', '00', 'pass', '/software',
                'root', 'pass', hdb_pwd_file='passwords.xml') == ret

            mock_create.assert_called_once_with(
                software_path='/software',
                conf_file=hanamod.TMP_CONFIG_FILE,
                root_user='root',
                root_password='pass')
            mock_cp.assert_called_with(
                path='passwords.xml',
                dest=hanamod.TMP_HDB_PWD_FILE)
            mock_update.assert_called_once_with(
                    conf_file='hana_created.conf', sid='PRD', number='00',
                    root_user='root')

            mock_install.assert_called_once_with(
                software_path='/software',
                conf_file='hana_updated.conf',
                root_user='root',
                root_password='pass',
                hdb_pwd_file=hanamod.TMP_HDB_PWD_FILE)
            mock_remove.assert_has_calls([
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
                'logreplay', 'pdr', '00', 'pass',
                primary_pass='pass', timeout=10, interval=15) == ret
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
                primary_pass='pass',
                timeout=10,
                interval=15,
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
                primary_pass=None,
                timeout=None,
                interval=None,
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
                   'global_allocation_limit': '25000',
                   'preload_column_tables': False
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

    def test_pydbapi_extracted_already_exists(self):
        ret = {'name': 'PYDBAPI.tar',
               'changes': {},
               'result': True,
               'comment': '/tmp/output already exists. Skipping extraction (set force to True to force the extraction)'}

        mock_dir_exists = MagicMock(return_value=True)

        with patch.dict(hanamod.__salt__, {'file.directory_exists': mock_dir_exists}):
            assert hanamod.pydbapi_extracted(
                'PYDBAPI.tar', ['1234', '5678'], '/tmp/output') == ret

        mock_dir_exists.assert_called_once_with('/tmp/output')

    def test_pydbapi_extracted_test(self):
        ret = {'name': 'PYDBAPI.tar',
               'changes': {'output_dir': '/tmp/output'},
               'result': None,
               'comment': 'PYDBAPI.tar would be extracted'}

        with patch.dict(hanamod.__opts__, {'test': True}):
            assert hanamod.pydbapi_extracted(
                'PYDBAPI.tar', ['1234', '5678'], '/tmp/output', force=True) == ret

    def test_pydbapi_extracted_error(self):
        ret = {'name': 'PYDBAPI.tar',
               'changes': {},
               'result': False,
               'comment': 'error extracting'}

        mock_mkdir = MagicMock()
        mock_extract_pydbapi = MagicMock(
            side_effect=exceptions.CommandExecutionError('error extracting'))

        with patch.dict(hanamod.__salt__, {'file.mkdir': mock_mkdir,
                                           'hana.extract_pydbapi': mock_extract_pydbapi}):
            assert hanamod.pydbapi_extracted(
                'PYDBAPI.tar', ['1234', '5678'], '/tmp/output',
                additional_extract_options='-l', force=True) == ret

        mock_mkdir.assert_called_once_with('/tmp/output')
        mock_extract_pydbapi.assert_called_once_with(
            'PYDBAPI.tar', ['1234', '5678'], '/tmp/output', '20', '-l')

    def test_pydbapi_extracted_correct(self):
        ret = {'name': 'PYDBAPI.tar',
               'changes': {'pydbapi': 'py_client', 'output_dir': '/tmp/output'},
               'result': True,
               'comment': 'py_client correctly extracted'}

        mock_mkdir = MagicMock()
        mock_extract_pydbapi = MagicMock(return_value='py_client')

        with patch.dict(hanamod.__salt__, {'file.mkdir': mock_mkdir,
                                           'hana.extract_pydbapi': mock_extract_pydbapi}):
            assert hanamod.pydbapi_extracted(
                'PYDBAPI.tar', ['1234', '5678'], '/tmp/output',
                force=True, additional_extract_options='-l') == ret

        mock_mkdir.assert_called_once_with('/tmp/output')
        mock_extract_pydbapi.assert_called_once_with(
            'PYDBAPI.tar', ['1234', '5678'], '/tmp/output', '20', '-l')
