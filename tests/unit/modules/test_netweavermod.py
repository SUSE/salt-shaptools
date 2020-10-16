# -*- coding: utf-8 -*-
'''
    :codeauthor: Xabier Arbulu Insausti <xarbulu@suse.com>
'''

# Import Python Libs
from __future__ import absolute_import, print_function, unicode_literals
import pytest

from salt import exceptions

# Import Salt Testing Libs
from tests.support.mixins import LoaderModuleMockMixin
from tests.support.unit import TestCase, skipIf
from tests.support import mock
from tests.support.mock import (
    MagicMock,
    patch
)

# Import Salt Libs
import salt.modules.netweavermod as netweavermod


class NetweaverModuleTest(TestCase, LoaderModuleMockMixin):
    '''
    This class contains a set of functions that test salt.modules.netweavermod.
    '''

    def setup_loader_modules(self):
        return {netweavermod: {}}

    @patch('salt.modules.netweavermod.netweaver.NetweaverInstance')
    def test_init_return(self, mock_netweaver):
        '''
        Test _init method
        '''
        mock_netweaver_inst = MagicMock()
        mock_netweaver.return_value = mock_netweaver_inst
        netweaver_inst = netweavermod._init('prd', '00', 'pass')
        mock_netweaver.assert_called_once_with('prd', '00', 'pass')
        assert mock_netweaver_inst == netweaver_inst

    @patch('salt.modules.netweavermod.netweaver.NetweaverInstance')
    def test_init_return_conf(self, mock_netweaver):
        '''
        Test _init method
        '''
        mock_netweaver_inst = MagicMock()
        mock_netweaver.return_value = mock_netweaver_inst
        mock_config = MagicMock(side_effect=[
            'conf_sid',
            'conf_inst',
            'conf_password'
        ])

        with patch.dict(netweavermod.__salt__, {'config.option': mock_config}):
            netweaver_inst = netweavermod._init()
            mock_netweaver.assert_called_once_with(
                'conf_sid', 'conf_inst', 'conf_password')
            assert mock_netweaver_inst == netweaver_inst
            mock_config.assert_has_calls([
                mock.call('netweaver.sid', None),
                mock.call('netweaver.inst', None),
                mock.call('netweaver.password', None)
            ])

    @patch('salt.modules.netweavermod.netweaver.NetweaverInstance')
    def test_init_raise(self, mock_netweaver):
        '''
        Test _init method
        '''
        mock_netweaver.side_effect = TypeError('error')
        with pytest.raises(exceptions.SaltInvocationError) as err:
            netweavermod._init('prd', '00', 'pass')
        mock_netweaver.assert_called_once_with('prd', '00', 'pass')
        assert 'error' in str(err.value)

    @patch('salt.modules.netweavermod.netweaver.NetweaverInstance')
    def test_execute_sapcontrol(self, mock_netweaver):
        '''
        Test execute_sapcontrol method
        '''
        mock_netweaver_inst = MagicMock()
        mock_netweaver.return_value = mock_netweaver_inst
        return_data = MagicMock(output='output')
        mock_netweaver_inst._execute_sapcontrol.return_value = return_data
        output = netweavermod.execute_sapcontrol('function', 'prd', '00', 'pass')
        mock_netweaver.assert_called_once_with('prd', '00', 'pass')
        mock_netweaver_inst._execute_sapcontrol.assert_called_once_with('function')
        assert output == 'output'

    @patch('salt.modules.netweavermod.netweaver.NetweaverInstance')
    def test_execute_sapcontrol_raise(self, mock_netweaver):
        '''
        Test execute_sapcontrol method
        '''
        mock_netweaver_inst = MagicMock()
        mock_netweaver.return_value = mock_netweaver_inst
        mock_netweaver_inst._execute_sapcontrol.side_effect = \
            netweavermod.netweaver.NetweaverError('error')
        with pytest.raises(exceptions.CommandExecutionError) as err:
            netweavermod.execute_sapcontrol('function', 'prd', '00', 'pass')
        mock_netweaver.assert_called_once_with('prd', '00', 'pass')
        mock_netweaver_inst._execute_sapcontrol.assert_called_once_with('function')
        assert 'error' in str(err.value)


    def test_is_installed_return_true(self):
        '''
        Test is_installed method
        '''
        mock_netweaver_inst = MagicMock()
        mock_netweaver_inst.is_installed.return_value = True
        mock_netweaver = MagicMock(return_value=mock_netweaver_inst)
        with patch.object(netweavermod, '_init', mock_netweaver):
            assert netweavermod.is_installed('prd', '00', 'pass', 'ascs')
            mock_netweaver.assert_called_once_with('prd', '00', 'pass')
            mock_netweaver_inst.is_installed.assert_called_once_with('ascs')

    def test_is_installed_return_false(self):
        '''
        Test is_installed method
        '''
        mock_netweaver_inst = MagicMock()
        mock_netweaver_inst.is_installed.return_value = False
        mock_netweaver = MagicMock(return_value=mock_netweaver_inst)
        with patch.object(netweavermod, '_init', mock_netweaver):
            assert not netweavermod.is_installed('prd', '00', 'pass', 'ascs')
            mock_netweaver.assert_called_once_with('prd', '00', 'pass')
            mock_netweaver_inst.is_installed.assert_called_once_with('ascs')

    def test_is_db_installed_return_true(self):
        '''
        Test is_db_installed method
        '''
        mock_wait = MagicMock(return_value=True)
        with patch.dict(netweavermod.__salt__, {'hana.wait_for_connection': mock_wait}):
            assert netweavermod.is_db_installed('192.168.10.15', 30015, 'SYSTEM', 'pass')
            mock_wait.assert_called_once_with(
                host='192.168.10.15',
                port=30015,
                user='SYSTEM',
                password='pass',
                timeout=0,
                interval=0
            )

    def test_is_db_installed_return_false(self):
        '''
        Test is_db_installed method
        '''
        mock_wait = MagicMock(side_effect=exceptions.CommandExecutionError)
        with patch.dict(netweavermod.__salt__, {'hana.wait_for_connection': mock_wait}):
            assert not netweavermod.is_db_installed('192.168.10.15', 30015, 'SYSTEM', 'pass')
            mock_wait.assert_called_once_with(
                host='192.168.10.15',
                port=30015,
                user='SYSTEM',
                password='pass',
                timeout=0,
                interval=0
            )

    def test_is_db_installed_raise_error(self):
        '''
        Test is_db_installed method
        '''
        with pytest.raises(exceptions.CommandExecutionError) as err:
            netweavermod.is_db_installed('192.168.10.15', 30015, 'SYSTEM', 'pass')
        assert 'hana.wait_for_connection not available. hanamod must be installed' in str(err.value)

    @patch('salt.modules.netweavermod.netweaver.shell.find_pattern')
    @patch('salt.modules.netweavermod.netweaver.NetweaverInstance')
    def test_is_instance_installed(self, mock_netweaver, mock_find_pattern):
        '''
        Test is_instance_installed method
        '''
        mock_netweaver_inst = MagicMock()
        mock_netweaver.return_value = mock_netweaver_inst
        instances_data = MagicMock(output='output')
        mock_netweaver_inst.get_system_instances.return_value = instances_data
        found = MagicMock()
        found.group.return_value = 'sapha1er, 10, 51013, 51014, 3, ENQREP, GREEN'
        mock_find_pattern.return_value = found

        data = netweavermod.is_instance_installed(
            'MESSAGESERVER', 'GREEN', 'virtual', 'prd', '00', 'pass')

        mock_netweaver.assert_called_once_with('prd', '00', 'pass')
        mock_netweaver_inst.get_system_instances.assert_called_once_with()
        mock_find_pattern.assert_called_once_with('virtual.*MESSAGESERVER.*GREEN.*', 'output')
        found.group.assert_called_once_with(0)
        assert data['hostname'] == 'sapha1er'
        assert data['instance'] == '10'
        assert data['http_port'] == '51013'
        assert data['https_port'] == '51014'
        assert data['start_priority'] == '3'
        assert data['features'] == 'ENQREP'
        assert data['dispstatus'] == 'GREEN'

    @patch('salt.modules.netweavermod.netweaver.shell.find_pattern')
    @patch('salt.modules.netweavermod.netweaver.NetweaverInstance')
    def test_is_instance_installed_not_found(self, mock_netweaver, mock_find_pattern):
        '''
        Test is_instance_installed method
        '''
        mock_netweaver_inst = MagicMock()
        mock_netweaver.return_value = mock_netweaver_inst
        instances_data = MagicMock(output='output')
        mock_netweaver_inst.get_system_instances.return_value = instances_data
        mock_find_pattern.return_value = None

        data = netweavermod.is_instance_installed(
            'MESSAGESERVER', sid='prd', inst='00', password='pass')

        mock_netweaver.assert_called_once_with('prd', '00', 'pass')
        mock_netweaver_inst.get_system_instances.assert_called_once_with()
        mock_find_pattern.assert_called_once_with('.*MESSAGESERVER.*.*', 'output')
        assert data == False

    @patch('salt.modules.netweavermod.netweaver.NetweaverInstance')
    def test_is_instance_installed_error(self, mock_netweaver):
        '''
        Test is_instance_installed method
        '''
        mock_netweaver_inst = MagicMock()
        mock_netweaver.return_value = mock_netweaver_inst
        instances_data = MagicMock(output='output')
        mock_netweaver_inst.get_system_instances.side_effect = \
            netweavermod.netweaver.NetweaverError('errpr')

        data = netweavermod.is_instance_installed(
            'MESSAGESERVER', sid='prd', inst='00', password='pass')

        mock_netweaver.assert_called_once_with('prd', '00', 'pass')
        mock_netweaver_inst.get_system_instances.assert_called_once_with()
        assert data == False

    def test_attach_virtual_host(self):

        mock_get_ip = MagicMock()
        mock_get_ip.return_value = '192.168.15.1'

        mock_retcode = MagicMock()
        mock_retcode.return_value = 1

        mock_run = MagicMock()
        mock_run.return_value = 0

        with patch.dict(netweavermod.__salt__, {'hosts.get_ip': mock_get_ip,
                                                'cmd.retcode': mock_retcode,
                                                'cmd.run': mock_run}):
            ip_address = netweavermod.attach_virtual_host('vhost', 'eth1', 32)

        mock_get_ip.assert_called_once_with('vhost')
        mock_retcode.assert_called_once_with('ip a | grep 192.168.15.1/32', python_shell=True)
        mock_run.assert_called_once_with('ip address add 192.168.15.1/32 dev eth1')
        assert ip_address == '192.168.15.1'

    def test_attach_virtual_host_not_ip(self):

        mock_get_ip = MagicMock()
        mock_get_ip.return_value = None

        with pytest.raises(exceptions.CommandExecutionError) as err:
            with patch.dict(netweavermod.__salt__, {'hosts.get_ip': mock_get_ip}):
                netweavermod.attach_virtual_host('vhost')

        mock_get_ip.assert_called_once_with('vhost')
        assert 'virtual host vhost not available' in str(err.value)

    def test_attach_virtual_host_ip_found(self):

        mock_get_ip = MagicMock()
        mock_get_ip.return_value = '192.168.15.1'

        mock_retcode = MagicMock()
        mock_retcode.return_value = 0

        with patch.dict(netweavermod.__salt__, {'hosts.get_ip': mock_get_ip,
                                                'cmd.retcode': mock_retcode}):
            ip_address = netweavermod.attach_virtual_host('vhost')

        mock_get_ip.assert_called_once_with('vhost')
        mock_retcode.assert_called_once_with('ip a | grep 192.168.15.1/24', python_shell=True)
        assert ip_address == '192.168.15.1'

    def test_attach_virtual_host_ip_not_found(self):

        mock_get_ip = MagicMock()
        mock_get_ip.return_value = '192.168.15.1'

        mock_retcode = MagicMock()
        mock_retcode.return_value = 1

        mock_run = MagicMock()
        mock_run.return_value = 1

        with pytest.raises(exceptions.CommandExecutionError) as err:
            with patch.dict(netweavermod.__salt__, {'hosts.get_ip': mock_get_ip,
                                                    'cmd.retcode': mock_retcode,
                                                    'cmd.run': mock_run}):
                netweavermod.attach_virtual_host('vhost')

        mock_get_ip.assert_called_once_with('vhost')
        mock_retcode.assert_called_once_with('ip a | grep 192.168.15.1/24', python_shell=True)
        mock_run.assert_called_once_with('ip address add 192.168.15.1/24 dev eth0')
        assert 'error running "ip address" command' in str(err.value)

    @patch('salt.modules.netweavermod.netweaver.NetweaverInstance')
    def test_update_conf_file(self, mock_netweaver):
        '''
        Test update_conf_file method - return
        '''
        mock_netweaver.update_conf_file.return_value = 'nw.inifile.params'
        conf_file = netweavermod.update_conf_file(
            'nw.inifile.params', sid='HA1', masterPwd='Suse1234')
        assert u'nw.inifile.params' == conf_file
        mock_netweaver.update_conf_file.assert_called_once_with(
            'nw.inifile.params', sid='HA1', masterPwd='Suse1234')

    @patch('salt.modules.netweavermod.netweaver.NetweaverInstance')
    def test_update_conf_file_raise(self, mock_netweaver):
        '''
        Test update_conf_file method - raise
        '''
        mock_netweaver.update_conf_file.side_effect = IOError('netweaver error')
        with pytest.raises(exceptions.CommandExecutionError) as err:
            netweavermod.update_conf_file('nw.inifile.params', sid='HA1', masterPwd='Suse1234')
        mock_netweaver.update_conf_file.assert_called_once_with(
            'nw.inifile.params', sid='HA1', masterPwd='Suse1234')
        assert 'netweaver error' in str(err.value)

    @patch('salt.modules.netweavermod.netweaver.NetweaverInstance')
    def test_install(self, mock_netweaver):
        '''
        Test install method - return
        '''
        netweavermod.install(
            'software_path', 'vhost', 'productID', 'netweaver.conf', 'root', 'root', cwd='/tmp')
        mock_netweaver.install.assert_called_once_with(
            'software_path', 'vhost', 'productID', 'netweaver.conf', 'root', 'root', cwd='/tmp')

    @patch('salt.modules.netweavermod.netweaver.NetweaverInstance')
    def test_install_raise(self, mock_netweaver):
        '''
        Test install method - raise
        '''
        mock_netweaver.install.side_effect = netweavermod.netweaver.NetweaverError(
            'netweaver error'
        )
        with pytest.raises(exceptions.CommandExecutionError) as err:
            netweavermod.install('software_path', 'vhost', 'productID', 'netweaver.conf', 'root', 'root')
        mock_netweaver.install.assert_called_once_with(
            'software_path', 'vhost', 'productID', 'netweaver.conf', 'root', 'root', cwd=None)
        assert 'netweaver error' in str(err.value)

    @patch('salt.modules.netweavermod.netweaver.NetweaverInstance')
    def test_install_ers(self, mock_netweaver):
        '''
        Test install method - return
        '''
        netweavermod.install_ers(
            'software_path', 'vhost', 'productID', 'netweaver.conf', 'root', 'root',
            cwd='/tmp', ascs_password='ascs', timeout=15, interval=2)
        mock_netweaver.install_ers.assert_called_once_with(
            'software_path', 'vhost', 'productID', 'netweaver.conf',
            'root', 'root', cwd='/tmp', ascs_password='ascs', timeout=15, interval=2)

    @patch('salt.modules.netweavermod.netweaver.NetweaverInstance')
    def test_install_ers_raise(self, mock_netweaver):
        '''
        Test install method - raise
        '''
        mock_netweaver.install_ers.side_effect = netweavermod.netweaver.NetweaverError(
            'netweaver error'
        )
        with pytest.raises(exceptions.CommandExecutionError) as err:
            netweavermod.install_ers('software_path', 'vhost', 'productID', 'netweaver.conf', 'root', 'root')
        mock_netweaver.install_ers.assert_called_once_with(
            'software_path', 'vhost', 'productID', 'netweaver.conf',
            'root', 'root', ascs_password=None, timeout=0, interval=5, cwd=None)
        assert 'netweaver error' in str(err.value)

    @patch('salt.modules.netweavermod.netweaver.NetweaverInstance')
    def test_get_ensa_version(self, mock_netweaver):
        '''
        Test install method - raise
        '''
        mock_netweaver_instance = mock.Mock()
        mock_netweaver_instance.get_ensa_version.return_value = 1
        mock_netweaver.return_value = mock_netweaver_instance
        with patch.object(netweavermod, '_init', mock_netweaver):
            version = netweavermod.get_ensa_version('ascs', 'prd', '00', 'pass')
            assert version == 1
        mock_netweaver.assert_called_once_with('prd', '00', 'pass')
        mock_netweaver_instance.get_ensa_version.assert_called_once_with('ascs')

    @patch('salt.modules.netweavermod.netweaver.NetweaverInstance')
    def test_get_ensa_version_error(self, mock_netweaver):
        '''
        Test install method - raise
        '''
        mock_netweaver_instance = mock.Mock()
        mock_netweaver_instance.get_ensa_version.side_effect = ValueError('invalid instance')
        mock_netweaver.return_value = mock_netweaver_instance
        with patch.object(netweavermod, '_init', mock_netweaver):
            with pytest.raises(exceptions.CommandExecutionError) as err:
                netweavermod.get_ensa_version('other', 'prd', '00', 'pass')
            assert'invalid instance' in str(err.value)
        mock_netweaver.assert_called_once_with('prd', '00', 'pass')
        mock_netweaver_instance.get_ensa_version.assert_called_once_with('other')

        mock_netweaver.reset_mock()
        mock_netweaver_instance.reset_mock()
        mock_netweaver_instance.get_ensa_version.side_effect = \
            netweavermod.netweaver.NetweaverError('Netweaver error')
        mock_netweaver.return_value = mock_netweaver_instance
        with patch.object(netweavermod, '_init', mock_netweaver):
            with pytest.raises(exceptions.CommandExecutionError) as err:
                netweavermod.get_ensa_version('ascs', 'prd', '00', 'pass')
            assert'Netweaver error' in str(err.value)
        mock_netweaver.assert_called_once_with('prd', '00', 'pass')
        mock_netweaver_instance.get_ensa_version.assert_called_once_with('ascs')

    def test_setup_cwd(self):

        mock_remove = mock.MagicMock()
        mock_mkdir = mock.MagicMock()
        mock_touch = mock.MagicMock()
        mock_chown = mock.MagicMock()
        mock_set_mode = mock.MagicMock()
        mock_append = mock.MagicMock()

        with patch.dict(netweavermod.__salt__, {'file.remove': mock_remove,
                                                'file.mkdir': mock_mkdir,
                                                'file.touch': mock_touch,
                                                'file.chown': mock_chown,
                                                'file.set_mode': mock_set_mode,
                                                'file.append': mock_append}):
            netweavermod.setup_cwd('/software', '/tmp', ['/path/dvd1', '/path/dvd2'])

            mock_remove.assert_called_once_with('/tmp')
            mock_mkdir.assert_called_once_with('/tmp', user='root', group='sapinst', mode=775)
            mock_touch.assert_called_once_with('/tmp/start_dir.cd')
            mock_chown.assert_called_once_with('/tmp/start_dir.cd', 'root', 'sapinst')
            mock_set_mode.assert_called_once_with('/tmp/start_dir.cd', 775)
            mock_append.assert_has_calls([
                mock.call('/tmp/start_dir.cd', args='/software'),
                mock.call('/tmp/start_dir.cd', args=['/path/dvd1', '/path/dvd2'])
            ])
