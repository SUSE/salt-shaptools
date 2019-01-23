
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
import salt.modules.crmshmod as crmshmod


@skipIf(NO_MOCK, NO_MOCK_REASON)
class CrmshModuleTest(TestCase, LoaderModuleMockMixin):
    '''
    This class contains a set of functions that test salt.modules.crm.
    '''

    def setup_loader_modules(self):
        return {crmshmod: {}}

    def test_status(self):
        '''
        Test status method
        '''
        mock_cmd_run = MagicMock(return_value=True)

        with patch.dict(crmshmod.__salt__, {'cmd.retcode': mock_cmd_run}):
            result = crmshmod.status()
            assert result
            mock_cmd_run.assert_called_once_with('{crm_command} status'.format(
                crm_command=crmshmod.CRM_COMMAND))

    def test_cluster_status(self):
        '''
        Test cluster_status method
        '''
        mock_cmd_run = MagicMock(return_value=True)

        with patch.dict(crmshmod.__salt__, {'cmd.retcode': mock_cmd_run}):
            result = crmshmod.cluster_status()
            assert result
            mock_cmd_run.assert_called_once_with('{crm_command} cluster status'.format(
                crm_command=crmshmod.CRM_COMMAND))

    def test_cluster_start(self):
        '''
        Test cluster_start method
        '''
        mock_cmd_run = MagicMock(return_value=True)

        with patch.dict(crmshmod.__salt__, {'cmd.retcode': mock_cmd_run}):
            result = crmshmod.cluster_start()
            assert result
            mock_cmd_run.assert_called_once_with('{crm_command} cluster start'.format(
                crm_command=crmshmod.CRM_COMMAND))

    def test_cluster_stop(self):
        '''
        Test cluster_stop method
        '''
        mock_cmd_run = MagicMock(return_value=True)

        with patch.dict(crmshmod.__salt__, {'cmd.retcode': mock_cmd_run}):
            result = crmshmod.cluster_stop()
            assert result
            mock_cmd_run.assert_called_once_with('{crm_command} cluster stop'.format(
                crm_command=crmshmod.CRM_COMMAND))

    def test_cluster_run(self):
        '''
        Test cluster_run method
        '''
        mock_cmd_run = MagicMock(return_value=True)

        with patch.dict(crmshmod.__salt__, {'cmd.retcode': mock_cmd_run}):
            result = crmshmod.cluster_run('ls -la')
            assert result
            mock_cmd_run.assert_called_once_with(
                '{crm_command} cluster run "{cmd}"'.format(
                    crm_command=crmshmod.CRM_COMMAND, cmd='ls -la'))

    def test_cluster_health(self):
        '''
        Test cluster_health method
        '''
        mock_cmd_run = MagicMock(return_value=True)

        with patch.dict(crmshmod.__salt__, {'cmd.retcode': mock_cmd_run}):
            result = crmshmod.cluster_health()
            assert result
            mock_cmd_run.assert_called_once_with('{crm_command} cluster health'.format(
                crm_command=crmshmod.CRM_COMMAND))

    def test_wait_for_startup(self):
        '''
        Test wait_for_startup method
        '''
        mock_cmd_run = MagicMock(return_value=True)

        with patch.dict(crmshmod.__salt__, {'cmd.retcode': mock_cmd_run}):
            result = crmshmod.wait_for_startup()
            assert result
            mock_cmd_run.assert_called_once_with(
                '{crm_command} cluster wait_for_startup'.format(
                    crm_command=crmshmod.CRM_COMMAND))

    def test_wait_for_startup_timeout(self):
        '''
        Test wait_for_startup method
        '''
        mock_cmd_run = MagicMock(return_value=True)

        with patch.dict(crmshmod.__salt__, {'cmd.retcode': mock_cmd_run}):
            result = crmshmod.wait_for_startup(5)
            assert result
            mock_cmd_run.assert_called_once_with(
                '{crm_command} cluster wait_for_startup {timeout}'.format(
                    crm_command=crmshmod.CRM_COMMAND, timeout=5))

    def test_wait_for_startup_error(self):
        '''
        Test wait_for_startup method
        '''
        mock_cmd_run = MagicMock(return_value=True)

        with patch.dict(crmshmod.__salt__, {'cmd.retcode': mock_cmd_run}):
            with pytest.raises(exceptions.SaltInvocationError) as err:
                crmshmod.wait_for_startup(5.0)
            assert 'timeout must be integer type' in str(err)

    def test_cluster_init_basic(self):
        '''
        Test cluster_init method
        '''
        mock_cmd_run = MagicMock(return_value=True)

        with patch.dict(crmshmod.__salt__, {'cmd.retcode': mock_cmd_run}):
            result = crmshmod.cluster_init('hacluster')
            assert result
            mock_cmd_run.assert_called_once_with(
                '{crm_command} cluster init -y -n {name}'.format(
                    crm_command=crmshmod.CRM_COMMAND, name='hacluster'))

    def test_cluster_init_complete(self):
        '''
        Test cluster_init method
        '''
        mock_cmd_run = MagicMock(return_value=True)

        with patch.dict(crmshmod.__salt__, {'cmd.retcode': mock_cmd_run}):
            result = crmshmod.cluster_init(
                'hacluster', 'dog', 'eth1', True, '192.168.1.50', True, 'sbd_dev', True)
            assert result
            mock_cmd_run.assert_called_once_with(
                '{} cluster init -y -n {} -w {} -i {} -u -A {} --enable-sbd -s {} -q'.format(
                    crmshmod.CRM_COMMAND, 'hacluster', 'dog', 'eth1', '192.168.1.50', 'sbd_dev'))

    def test_cluster_join_basic(self):
        '''
        Test cluster_join method
        '''
        mock_cmd_run = MagicMock(return_value=True)

        with patch.dict(crmshmod.__salt__, {'cmd.retcode': mock_cmd_run}):
            result = crmshmod.cluster_join('192.168.1.50')
            assert result
            mock_cmd_run.assert_called_once_with(
                '{crm_command} cluster join -y -c {host}'.format(
                    crm_command=crmshmod.CRM_COMMAND, host='192.168.1.50'))

    def test_cluster_join_complete(self):
        '''
        Test cluster_join method
        '''
        mock_cmd_run = MagicMock(return_value=True)

        with patch.dict(crmshmod.__salt__, {'cmd.retcode': mock_cmd_run}):
            result = crmshmod.cluster_join(
                '192.168.1.50', 'dog', 'eth1', True)
            assert result
            mock_cmd_run.assert_called_once_with(
                '{} cluster join -y -c {} -w {} -i {} -q'.format(
                    crmshmod.CRM_COMMAND, '192.168.1.50', 'dog', 'eth1'))

    def test_cluster_remove_basic(self):
        '''
        Test cluster_remove method
        '''
        mock_cmd_run = MagicMock(return_value=True)

        with patch.dict(crmshmod.__salt__, {'cmd.retcode': mock_cmd_run}):
            result = crmshmod.cluster_remove('192.168.1.50')
            assert result
            mock_cmd_run.assert_called_once_with(
                '{crm_command} cluster remove -y -c {host}'.format(
                    crm_command=crmshmod.CRM_COMMAND, host='192.168.1.50'))

    def test_cluster_remove_complete(self):
        '''
        Test cluster_remove method
        '''
        mock_cmd_run = MagicMock(return_value=True)

        with patch.dict(crmshmod.__salt__, {'cmd.retcode': mock_cmd_run}):
            result = crmshmod.cluster_remove(
                '192.168.1.50', True, True)
            assert result
            mock_cmd_run.assert_called_once_with(
                '{} cluster remove -y -c {} --force -q'.format(
                    crmshmod.CRM_COMMAND, '192.168.1.50'))

    def test_configure_load_basic(self):
        '''
        Test configure_load method
        '''
        mock_cmd_run = MagicMock(return_value=True)

        with patch.dict(crmshmod.__salt__, {'cmd.retcode': mock_cmd_run}):
            result = crmshmod.configure_load('update', 'file.conf')
            assert result
            mock_cmd_run.assert_called_once_with(
                '{crm_command} configure load {method} {url}'.format(
                    crm_command=crmshmod.CRM_COMMAND,
                    method='update',
                    url='file.conf'))

    def test_configure_load_complete(self):
        '''
        Test cluster_remove method
        '''
        mock_cmd_run = MagicMock(return_value=True)

        with patch.dict(crmshmod.__salt__, {'cmd.retcode': mock_cmd_run}):
            result = crmshmod.configure_load('update', 'file.conf', True)
            assert result
            mock_cmd_run.assert_called_once_with(
                '{crm_command} configure load xml {method} {url}'.format(
                    crm_command=crmshmod.CRM_COMMAND,
                    method='update',
                    url='file.conf'))
