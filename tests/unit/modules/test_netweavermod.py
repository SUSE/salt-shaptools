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
    patch,
    NO_MOCK,
    NO_MOCK_REASON
)

# Import Salt Libs
import salt.modules.netweavermod as netweavermod


@skipIf(NO_MOCK, NO_MOCK_REASON)
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
            ip_address = netweavermod.attach_virtual_host('vhost', 'eth1')

        mock_get_ip.assert_called_once_with('vhost')
        mock_retcode.assert_called_once_with('ip a | grep 192.168.15.1/24', python_shell=True)
        mock_run.assert_called_once_with('ip address add 192.168.15.1/24 dev eth1')
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
