
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

    @mock.patch('logging.Logger.info')
    @mock.patch('salt.utils.path.which')
    def test_virtual_crm(self, mock_which, logger):
        mock_pkg_version = MagicMock(return_value='1.0.0')
        mock_pkg_version_cmp = MagicMock(return_value=1)

        mock_which.side_effect = [True, True]
        with patch.dict(crmshmod.__salt__, {
                'pkg.version': mock_pkg_version,
                'pkg.version_cmp': mock_pkg_version_cmp}):
            assert crmshmod.__virtual__() == 'crm'
            mock_which.assert_called_once_with(crmshmod.CRM_COMMAND)
            logger.assert_has_calls([
                mock.call('crmsh version: %s', '1.0.0'),
                mock.call('%s will be used', 'crm')
            ])

    @mock.patch('salt.utils.path.which')
    def test_virtual_crm_error(self, mock_which):

        mock_which.side_effect = [False, True]
        response = crmshmod.__virtual__()
        assert response == (
            False, 'The crmsh execution module failed to load: the crm package'
            ' is not available.')
        mock_which.assert_called_once_with(crmshmod.CRM_COMMAND)

    @mock.patch('logging.Logger.info')
    @mock.patch('salt.utils.path.which')
    def test_virtual_ha(self, mock_which, logger):
        mock_pkg_version = MagicMock(return_value='1.0.0')
        mock_pkg_version_cmp = MagicMock(return_value=-1)

        mock_which.side_effect = [True, True]
        with patch.dict(crmshmod.__salt__, {
                'pkg.version': mock_pkg_version,
                'pkg.version_cmp': mock_pkg_version_cmp}):
            assert crmshmod.__virtual__() == 'crm'
            logger.assert_has_calls([
                mock.call('crmsh version: %s', '1.0.0'),
                mock.call('%s will be used', 'ha-cluster')
            ])
            mock_which.assert_has_calls([
                mock.call(crmshmod.CRM_COMMAND),
                mock.call(crmshmod.HA_INIT_COMMAND)
            ])

    @mock.patch('logging.Logger.info')
    @mock.patch('salt.utils.path.which')
    def test_virtual_ha_error(self, mock_which, logger):
        mock_pkg_version = MagicMock(return_value='1.0.0')
        mock_pkg_version_cmp = MagicMock(return_value=-1)

        mock_which.side_effect = [True, False]
        with patch.dict(crmshmod.__salt__, {
                'pkg.version': mock_pkg_version,
                'pkg.version_cmp': mock_pkg_version_cmp}):
            response = crmshmod.__virtual__()
            logger.assert_has_calls([
                mock.call('crmsh version: %s', '1.0.0'),
                mock.call('%s will be used', 'ha-cluster')
            ])
            mock_which.assert_has_calls([
                mock.call(crmshmod.CRM_COMMAND),
                mock.call(crmshmod.HA_INIT_COMMAND)
            ])
            assert response == (
                False,
                'The crmsh execution module failed to load: the ha-cluster-init'
                ' package is not available.')

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

    def test_crm_init_basic(self):
        '''
        Test _crm_init method
        '''
        mock_cmd_run = MagicMock(return_value=True)

        with patch.dict(crmshmod.__salt__, {'cmd.retcode': mock_cmd_run}):
            result = crmshmod._crm_init('hacluster')
            assert result
            mock_cmd_run.assert_called_once_with(
                '{crm_command} cluster init -y -n {name}'.format(
                    crm_command=crmshmod.CRM_COMMAND, name='hacluster'))

    def test_crm_init_complete(self):
        '''
        Test _crm_init method
        '''
        mock_cmd_run = MagicMock(return_value=True)

        with patch.dict(crmshmod.__salt__, {'cmd.retcode': mock_cmd_run}):
            result = crmshmod._crm_init(
                'hacluster', 'dog', 'eth1', True, '192.168.1.50', True, 'sbd_dev', True)
            assert result
            mock_cmd_run.assert_called_once_with(
                '{} cluster init -y -n {} -w {} -i {} -u -A {} --enable-sbd -s {} -q'.format(
                    crmshmod.CRM_COMMAND, 'hacluster', 'dog', 'eth1', '192.168.1.50', 'sbd_dev'))

    def test_ha_cluster_init_basic(self):
        '''
        Test _ha_cluster_init method
        '''
        mock_cmd_run = MagicMock(return_value=True)

        with patch.dict(crmshmod.__salt__, {'cmd.retcode': mock_cmd_run}):
            result = crmshmod._ha_cluster_init()
            assert result
            mock_cmd_run.assert_called_once_with(
                '{command} -y'.format(command=crmshmod.HA_INIT_COMMAND))

    def test_ha_cluster_init_complete(self):
        '''
        Test _ha_cluster_init method
        '''
        mock_cmd_run = MagicMock(return_value=True)

        with patch.dict(crmshmod.__salt__, {'cmd.retcode': mock_cmd_run}):
            result = crmshmod._ha_cluster_init(
                'eth1', True, '192.168.1.50', True, 'sbd_dev', True)
            assert result
            mock_cmd_run.assert_called_once_with(
                '{} -y -i {} -u -A {} -S -s {} -q'.format(
                    crmshmod.HA_INIT_COMMAND, 'eth1', '192.168.1.50', 'sbd_dev'))

    @mock.patch('salt.modules.crmshmod._crm_init')
    def test_cluster_init_crm(self, crm_init):
        '''
        Test cluster_init with crm option
        '''
        crmshmod.__crmnewversion__ = True
        crm_init.return_value = 0
        value = crmshmod.cluster_init('hacluster', 'dog', 'eth1')
        assert value == 0
        crm_init.assert_called_once_with(
            'hacluster', 'dog', 'eth1', None, None, None, None, None)

    @mock.patch('logging.Logger.warn')
    @mock.patch('salt.modules.crmshmod._ha_cluster_init')
    def test_cluster_init_ha(self, ha_cluster_init, logger):
        '''
        Test cluster_init with ha_cluster_init option
        '''
        crmshmod.__crmnewversion__ = False
        ha_cluster_init.return_value = 0
        value = crmshmod.cluster_init('hacluster', 'dog', 'eth1')
        assert value == 0
        logger.assert_called_once_with(
            'The parameters name and watchdog are not considered!')
        ha_cluster_init.assert_called_once_with(
            'eth1', None, None, None, None, None)

    def test_crm_join_basic(self):
        '''
        Test _crm_join method
        '''
        mock_cmd_run = MagicMock(return_value=True)

        with patch.dict(crmshmod.__salt__, {'cmd.retcode': mock_cmd_run}):
            result = crmshmod._crm_join('192.168.1.50')
            assert result
            mock_cmd_run.assert_called_once_with(
                '{crm_command} cluster join -y -c {host}'.format(
                    crm_command=crmshmod.CRM_COMMAND, host='192.168.1.50'))

    def test_crm_join_complete(self):
        '''
        Test cluster_join method
        '''
        mock_cmd_run = MagicMock(return_value=True)

        with patch.dict(crmshmod.__salt__, {'cmd.retcode': mock_cmd_run}):
            result = crmshmod._crm_join(
                '192.168.1.50', 'dog', 'eth1', True)
            assert result
            mock_cmd_run.assert_called_once_with(
                '{} cluster join -y -c {} -w {} -i {} -q'.format(
                    crmshmod.CRM_COMMAND, '192.168.1.50', 'dog', 'eth1'))

    def test_ha_cluster_join_basic(self):
        '''
        Test _ha_cluster_join method
        '''
        mock_cmd_run = MagicMock(return_value=True)

        with patch.dict(crmshmod.__salt__, {'cmd.retcode': mock_cmd_run}):
            result = crmshmod._ha_cluster_join('192.168.1.50')
            assert result
            mock_cmd_run.assert_called_once_with(
                '{command} -y -c {host}'.format(
                    command=crmshmod.HA_JOIN_COMMAND, host='192.168.1.50'))

    def test_ha_cluster_join_complete(self):
        '''
        Test _ha_cluster_join method
        '''
        mock_cmd_run = MagicMock(return_value=True)

        with patch.dict(crmshmod.__salt__, {'cmd.retcode': mock_cmd_run}):
            result = crmshmod._ha_cluster_join('192.168.1.50', 'eth1', True)
            assert result
            mock_cmd_run.assert_called_once_with(
                '{} -y -c {} -i {} -q'.format(
                    crmshmod.HA_JOIN_COMMAND, '192.168.1.50', 'eth1'))

    @mock.patch('salt.modules.crmshmod._crm_join')
    def test_cluster_join_crm(self, crm_join):
        '''
        Test cluster_join with crm option
        '''
        crmshmod.__crmnewversion__ = True
        crm_join.return_value = 0
        value = crmshmod.cluster_join('host', 'dog', 'eth1')
        assert value == 0
        crm_join.assert_called_once_with(
            'host', 'dog', 'eth1', None)

    @mock.patch('logging.Logger.warn')
    @mock.patch('salt.modules.crmshmod._ha_cluster_join')
    def test_cluster_join_ha(self, ha_cluster_join, logger):
        '''
        Test cluster_join with ha_cluster_join option
        '''
        crmshmod.__crmnewversion__ = False
        ha_cluster_join.return_value = 0
        value = crmshmod.cluster_join('host', 'dog', 'eth1')
        assert value == 0
        logger.assert_called_once_with(
            'The parameter watchdog is not considered!')
        ha_cluster_join.assert_called_once_with('host', 'eth1', None)

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
