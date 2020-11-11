
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
import salt.modules.crmshmod as crmshmod


class CrmshModuleTest(TestCase, LoaderModuleMockMixin):
    '''
    This class contains a set of functions that test salt.modules.crm.
    '''

    def setup_loader_modules(self):
        return {crmshmod: {}}

    @mock.patch('salt.utils.path.which')
    def test_virtual_crm(self, mock_which):
        mock_pkg_version = MagicMock(return_value='1.0.0')
        mock_pkg_version_cmp = MagicMock(return_value=1)

        mock_which.side_effect = [True, True]
        with patch.dict(crmshmod.__salt__, {
                'pkg.version': mock_pkg_version,
                'pkg.version_cmp': mock_pkg_version_cmp}):
            assert crmshmod.__virtual__() == 'crm'
            mock_which.assert_called_once_with(crmshmod.CRM_COMMAND)

    @mock.patch('salt.utils.path.which')
    def test_virtual_crm_error(self, mock_which):

        mock_which.side_effect = [False, True]
        response = crmshmod.__virtual__()
        assert response == (
            False, 'The crmsh execution module failed to load: the crm package'
            ' is not available.')
        mock_which.assert_called_once_with(crmshmod.CRM_COMMAND)

    @mock.patch('salt.utils.path.which')
    def test_virtual_ha(self, mock_which):
        mock_pkg_version = MagicMock(return_value='1.0.0')
        mock_pkg_version_cmp = MagicMock(return_value=-1)

        mock_which.side_effect = [True, True]
        with patch.dict(crmshmod.__salt__, {
                'pkg.version': mock_pkg_version,
                'pkg.version_cmp': mock_pkg_version_cmp}):
            assert crmshmod.__virtual__() == 'crm'
            mock_which.assert_has_calls([
                mock.call(crmshmod.CRM_COMMAND),
                mock.call(crmshmod.HA_INIT_COMMAND)
            ])

    @mock.patch('salt.utils.path.which')
    def test_virtual_ha_error(self, mock_which):
        mock_pkg_version = MagicMock(return_value='1.0.0')
        mock_pkg_version_cmp = MagicMock(return_value=-1)

        mock_which.side_effect = [True, False]
        with patch.dict(crmshmod.__salt__, {
                'pkg.version': mock_pkg_version,
                'pkg.version_cmp': mock_pkg_version_cmp}):
            response = crmshmod.__virtual__()
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
            assert 'timeout must be integer type' in str(err.value)

    def test_add_watchdog_sbd(self):
        '''
        Test _add_watchdog_sbd
        '''
        mock_file_replace = MagicMock()

        with patch.dict(crmshmod.__salt__, {'file.replace': mock_file_replace}):
            crmshmod._add_watchdog_sbd('dog')
            mock_file_replace.assert_called_once_with(
                path='/etc/sysconfig/sbd',
                pattern='^SBD_WATCHDOG_DEV=.*',
                repl='SBD_WATCHDOG_DEV={}'.format('dog'),
                append_if_not_found=True
            )

    def test_add_node_corosync(self):
        '''
        Test _add_node_corosync
        '''
        mock_cmd_run = MagicMock()
        mock_contains_regex = MagicMock(return_value=0)
        mock_file_append = MagicMock()

        with patch.dict(crmshmod.__salt__, {
                'cmd.run': mock_cmd_run,
                'file.contains_regex': mock_contains_regex,
                'file.append': mock_file_append}):
            crmshmod._add_node_corosync('1.0.1.0', 'node')
            mock_contains_regex.assert_called_once_with(
                path='/etc/corosync/corosync.conf', regex='^nodelist.*')
            mock_file_append.assert_called_once_with(
                path='/etc/corosync/corosync.conf', args='nodelist {}')
            mock_cmd_run.assert_called_once_with(
                '{crm_command} corosync add-node {addr} {name}'.format(
                    crm_command=crmshmod.CRM_COMMAND,
                    addr='1.0.1.0', name='node'), raise_err=True)

    def test_set_corosync_value(self):
        '''
        Test _set_corosync_value
        '''
        mock_cmd_run = MagicMock()

        with patch.dict(crmshmod.__salt__, {'cmd.run': mock_cmd_run}):
            crmshmod._set_corosync_value('path', 'value')
            mock_cmd_run.assert_called_once_with(
                '{crm_command} corosync set {path} {value}'.format(
                    crm_command=crmshmod.CRM_COMMAND,
                    path='path', value='value'), raise_err=True)

    def test_create_corosync_authkey(self):
        '''
        Test _create_corosync_authkey
        '''
        mock_cmd_run = MagicMock()

        with patch.dict(crmshmod.__salt__, {'cmd.run': mock_cmd_run}):
            crmshmod._create_corosync_authkey()
            mock_cmd_run.assert_called_once_with('corosync-keygen', raise_err=True)

    @mock.patch('salt.modules.crmshmod._set_corosync_value')
    @mock.patch('salt.modules.crmshmod._add_node_corosync')
    @mock.patch('salt.modules.crmshmod._create_corosync_authkey')
    def test_set_corosync_unicast(self, mock_authkey, mock_add, mock_set):
        '''
        Test _set_corosync_unicast
        '''
        mock_cmd_run = MagicMock()
        mock_file_line = MagicMock()

        with patch.dict(crmshmod.__salt__, {
                'cmd.run': mock_cmd_run,
                'file.line': mock_file_line}):
            crmshmod._set_corosync_unicast('1.0.1.0', 'node')
            mock_file_line.assert_called_once_with(
                path='/etc/corosync/corosync.conf',
                match='.*mcastaddr:.*',
                mode='delete')
            mock_cmd_run.assert_has_calls([
                mock.call('{crm_command} cluster stop'.format(
                    crm_command=crmshmod.CRM_COMMAND), raise_err=True),
                mock.call('{crm_command} cluster start'.format(
                    crm_command=crmshmod.CRM_COMMAND), raise_err=True)
            ])
            mock_set.assert_called_once_with('totem.transport', 'udpu')
            mock_add.assert_called_once_with('1.0.1.0', 'node')
            mock_authkey.assert_called_once_with()

    def test_join_corosync_unicast(self):
        '''
        Test _join_corosync_unicast
        '''
        mock_cmd_retcode = MagicMock(return_value=0)
        mock_cmd_run = MagicMock()
        mock_get_hostname = MagicMock(return_value='node')
        mock_interface_ip = MagicMock(return_value='1.0.1.0')

        with patch.dict(crmshmod.__salt__, {
                'cmd.retcode': mock_cmd_retcode,
                'cmd.run': mock_cmd_run,
                'network.get_hostname': mock_get_hostname,
                'network.interface_ip': mock_interface_ip}):
            crmshmod._join_corosync_unicast('main_node', 'eth1')
            mock_cmd_retcode.assert_called_once_with(
                'ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -t '
                'root@{host} "grep \'transport: udpu\' {conf}"'.format(
                    host='main_node', conf='/etc/corosync/corosync.conf')
            )
            mock_interface_ip.assert_called_once_with('eth1')
            mock_cmd_run.assert_called_once_with(
                'ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -t '
                'root@{host} "sudo {crm_command} corosync add-node {addr} {name}"'.format(
                    host='main_node', crm_command=crmshmod.CRM_COMMAND,
                    addr='1.0.1.0', name='node'), raise_err=True
            )

    @mock.patch('logging.Logger.info')
    def test_join_corosync_not_unicast(self, logger):
        '''
        Test _join_corosync_unicast
        '''
        mock_cmd_retcode = MagicMock(return_value=1)

        with patch.dict(crmshmod.__salt__, {'cmd.retcode': mock_cmd_retcode}):
            crmshmod._join_corosync_unicast('main_node', 'eth1')
            mock_cmd_retcode.assert_called_once_with((
                    'ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -t '
                    'root@{host} "grep \'transport: udpu\' {conf}"'.format(
                        host='main_node', conf='/etc/corosync/corosync.conf')))
            logger.assert_called_once_with('cluster not set as unicast')

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
                'hacluster', 'dog', 'eth1', True, '192.168.1.50', True, ['dev1', 'dev2'], True, 'alice', True)
            assert result
            mock_cmd_run.assert_called_once_with(
                '{} cluster init -y -n {} -w {} -i {} -u -A {} '
                '-s {} -s {} --no-overwrite-sshkey --qnetd-hostname {} -q'.format(
                    crmshmod.CRM_COMMAND, 'hacluster', 'dog', 'eth1', '192.168.1.50', 'dev1', 'dev2', 'alice'))

        # SBD diskless
        mock_cmd_run.reset_mock()
        with patch.dict(crmshmod.__salt__, {'cmd.retcode': mock_cmd_run}):
            result = crmshmod._crm_init(
                'hacluster', 'dog', 'eth1', True, '192.168.1.50', True, None, True, 'alice', True)
            assert result
            mock_cmd_run.assert_called_once_with(
                '{} cluster init -y -n {} -w {} -i {} -u -A {} '
                '-S --no-overwrite-sshkey --qnetd-hostname {} -q'.format(
                    crmshmod.CRM_COMMAND, 'hacluster', 'dog', 'eth1', '192.168.1.50', 'alice'))

    def test_ha_cluster_init_basic(self):
        '''
        Test _ha_cluster_init method
        '''
        mock_cmd_run = MagicMock(return_value=0)

        with patch.dict(crmshmod.__salt__, {'cmd.retcode': mock_cmd_run}):
            result = crmshmod._ha_cluster_init()
            assert result == 0
            mock_cmd_run.assert_called_once_with(
                '{command} -y'.format(command=crmshmod.HA_INIT_COMMAND))

    @mock.patch('salt.modules.crmshmod._add_watchdog_sbd')
    @mock.patch('salt.modules.crmshmod._set_corosync_unicast')
    def test_ha_cluster_init_complete(self, mock_corosync, mock_watchdog):
        '''
        Test _ha_cluster_init method
        '''
        mock_cmd_run = MagicMock(return_value=0)
        mock_get_hostname = MagicMock(return_value='node')
        mock_interface_ip = MagicMock(return_value='1.0.1.0')

        with patch.dict(crmshmod.__salt__, {
                'cmd.retcode': mock_cmd_run,
                'network.get_hostname': mock_get_hostname,
                'network.interface_ip': mock_interface_ip}):
            result = crmshmod._ha_cluster_init(
                'dog', 'eth1', True, '192.168.1.50', True, ['dev1', 'dev2'], 'alice', True)
            assert result == 0
            mock_watchdog.assert_called_once_with('dog')
            mock_corosync.assert_called_once_with('1.0.1.0', 'node')
            mock_interface_ip.assert_called_once_with('eth1')
            mock_cmd_run.assert_called_once_with(
                '{} -y -i {} -A {} -s {} -s {} --qnetd-hostname {} -q'.format(
                    crmshmod.HA_INIT_COMMAND, 'eth1', '192.168.1.50', 'dev1', 'dev2', 'alice'))

        # SBD diskless
        mock_cmd_run.reset_mock()
        with patch.dict(crmshmod.__salt__, {
                'cmd.retcode': mock_cmd_run,
                'network.get_hostname': mock_get_hostname,
                'network.interface_ip': mock_interface_ip}):
            result = crmshmod._ha_cluster_init(
                'dog', 'eth1', True, '192.168.1.50', True, None, 'alice', True)
            assert result == 0
            mock_cmd_run.assert_called_once_with(
                '{} -y -i {} -A {} -S --qnetd-hostname {} -q'.format(
                    crmshmod.HA_INIT_COMMAND, 'eth1', '192.168.1.50', 'alice'))

    @mock.patch('salt.modules.crmshmod._crm_init')
    def test_cluster_init_crm(self, crm_init):
        '''
        Test cluster_init with crm option
        '''

        with patch.dict(crmshmod.__salt__, {'crm.use_crm': True}):
            crm_init.return_value = 0
            value = crmshmod.cluster_init('hacluster', 'dog', 'eth1', sbd=True, sbd_dev='dev1')
            assert value == 0
            crm_init.assert_called_once_with(
                'hacluster', 'dog', 'eth1', None, None, True, ['dev1'], False, None, None)

        crm_init.reset_mock()
        with patch.dict(crmshmod.__salt__, {'crm.use_crm': True}):
            crm_init.return_value = 0
            value = crmshmod.cluster_init('hacluster', 'dog', 'eth1', sbd=False, sbd_dev=['disk1', 'disk2'])
            assert value == 0
            crm_init.assert_called_once_with(
                'hacluster', 'dog', 'eth1', None, None, False, ['disk1', 'disk2'], False, None, None)

    @mock.patch('logging.Logger.warning')
    @mock.patch('salt.modules.crmshmod._ha_cluster_init')
    def test_cluster_init_ha(self, ha_cluster_init, logger):
        '''
        Test cluster_init with ha_cluster_init option
        '''

        with patch.dict(crmshmod.__salt__, {'crm.use_crm': False}):
            ha_cluster_init.return_value = 0
            value = crmshmod.cluster_init(
                'hacluster', 'dog', 'eth1', sbd_dev='dev1', no_overwrite_sshkey=True)
            assert value == 0
            logger.assert_has_calls([
                mock.call('The parameter name is not considered!'),
                mock.call('--no_overwrite_sshkey option not available')
            ])
            ha_cluster_init.assert_called_once_with(
                'dog', 'eth1', None, None, None, ['dev1'], None, None)

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

    @mock.patch('salt.modules.crmshmod._join_corosync_unicast')
    def test_ha_cluster_join_basic(self, mock_corosync):
        '''
        Test _ha_cluster_join method
        '''
        mock_cmd_run = MagicMock(return_value=True)

        with patch.dict(crmshmod.__salt__, {'cmd.retcode': mock_cmd_run}):
            result = crmshmod._ha_cluster_join('192.168.1.50')
            assert result
            mock_corosync.assert_called_once_with('192.168.1.50', None)
            mock_cmd_run.assert_called_once_with(
                '{command} -y -c {host}'.format(
                    command=crmshmod.HA_JOIN_COMMAND, host='192.168.1.50'))

    @mock.patch('salt.modules.crmshmod._add_watchdog_sbd')
    @mock.patch('salt.modules.crmshmod._join_corosync_unicast')
    def test_ha_cluster_join_complete(self, mock_corosync, mock_watchdog):
        '''
        Test _ha_cluster_join method
        '''
        mock_cmd_run = MagicMock(side_effect=[0, 0])

        with patch.dict(crmshmod.__salt__, {'cmd.retcode': mock_cmd_run}):
            result = crmshmod._ha_cluster_join(
                '192.168.1.50', 'dog', 'eth1', True)
            assert result == 0
            mock_corosync.assert_called_once_with('192.168.1.50', 'eth1')
            mock_watchdog.assert_called_once_with('dog')
            mock_cmd_run.assert_has_calls([
                mock.call('{} -y -c {} -i {} -q'.format(
                    crmshmod.HA_JOIN_COMMAND, '192.168.1.50', 'eth1')),
                mock.call('{} resource refresh'.format(
                    crmshmod.CRM_COMMAND))
            ])

    @mock.patch('salt.modules.crmshmod._add_watchdog_sbd')
    @mock.patch('salt.modules.crmshmod._join_corosync_unicast')
    def test_ha_cluster_join_complete_error(self, mock_corosync, mock_watchdog):
        '''
        Test _ha_cluster_join method
        '''
        mock_cmd_run = MagicMock(side_effect=[1, 0])

        with patch.dict(crmshmod.__salt__, {'cmd.retcode': mock_cmd_run}):
            result = crmshmod._ha_cluster_join(
                '192.168.1.50', 'dog', 'eth1', True)
            assert result == 1
            mock_corosync.assert_called_once_with('192.168.1.50', 'eth1')
            mock_watchdog.assert_called_once_with('dog')
            mock_cmd_run.assert_called_once_with('{} -y -c {} -i {} -q'.format(
                    crmshmod.HA_JOIN_COMMAND, '192.168.1.50', 'eth1'))

    @mock.patch('salt.modules.crmshmod._crm_join')
    def test_cluster_join_crm(self, crm_join):
        '''
        Test cluster_join with crm option
        '''
        with patch.dict(crmshmod.__salt__, {'crm.use_crm': True}):
            crm_join.return_value = 0
            value = crmshmod.cluster_join('host', 'dog', 'eth1')
            assert value == 0
            crm_join.assert_called_once_with(
                'host', 'dog', 'eth1', None)

    @mock.patch('salt.modules.crmshmod._ha_cluster_join')
    def test_cluster_join_ha(self, ha_cluster_join):
        '''
        Test cluster_join with ha_cluster_join option
        '''
        with patch.dict(crmshmod.__salt__, {'crm.use_crm': False}):
            ha_cluster_join.return_value = 0
            value = crmshmod.cluster_join('host', 'dog', 'eth1')
            assert value == 0
            ha_cluster_join.assert_called_once_with('host', 'dog', 'eth1', None)

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
                '{crm_command} -n configure load {method} {url}'.format(
                    crm_command=crmshmod.CRM_COMMAND,
                    method='update',
                    url='file.conf'))

    def test_configure_load_complete(self):
        '''
        Test cluster_remove method
        '''
        mock_cmd_run = MagicMock(return_value=True)

        with patch.dict(crmshmod.__salt__, {'cmd.retcode': mock_cmd_run}):
            result = crmshmod.configure_load('update', 'file.conf', True, True)
            assert result
            mock_cmd_run.assert_called_once_with(
                '{crm_command} -F configure load xml {method} {url}'.format(
                    crm_command=crmshmod.CRM_COMMAND,
                    method='update',
                    url='file.conf'))

    def test_configure_get_property(self):
        '''
        Test configure_get_property
        '''

        mock_cmd_run = MagicMock(return_value=' value ')

        with patch.dict(crmshmod.__salt__, {'cmd.run': mock_cmd_run}):
            result = crmshmod.configure_get_property('item')
            assert result == 'value'
            mock_cmd_run.assert_called_once_with(
                '{crm_command} configure get_property {property}'.format(
                    crm_command=crmshmod.CRM_COMMAND,
                    property='item'))

    def test_configure_get_property_error(self):
        '''
        Test configure_get_property when it raises an error
        '''

        mock_cmd_run = MagicMock(return_value='ERROR: configure.get_property: item')

        with patch.dict(crmshmod.__salt__, {'cmd.run': mock_cmd_run}):
            with pytest.raises(exceptions.CommandExecutionError) as err:
                crmshmod.configure_get_property('item')
            mock_cmd_run.assert_called_once_with(
                '{crm_command} configure get_property {property}'.format(
                    crm_command=crmshmod.CRM_COMMAND,
                    property='item'))

        assert 'ERROR: configure.get_property: item' in str(err.value)

    def test_configure_property(self):
        '''
        Test configure_property method
        '''
        mock_cmd_run = MagicMock(return_value=True)

        with patch.dict(crmshmod.__salt__, {'cmd.retcode': mock_cmd_run}):
            result = crmshmod.configure_property('item', 'value')
            assert result
            mock_cmd_run.assert_called_once_with(
                '{crm_command} configure property {item}="{value}"'.format(
                    crm_command=crmshmod.CRM_COMMAND,
                    item='item',
                    value='value'))

        mock_cmd_run.reset_mock()

        with patch.dict(crmshmod.__salt__, {'cmd.retcode': mock_cmd_run}):
            result = crmshmod.configure_property('item', False)
            assert result
            mock_cmd_run.assert_called_once_with(
                '{crm_command} configure property {item}={value}'.format(
                    crm_command=crmshmod.CRM_COMMAND,
                    item='item',
                    value='false'))

    def test_configure_rsc_defaults(self):
        '''
        Test configure_rsc_defaults method
        '''
        mock_cmd_run = MagicMock(return_value=True)

        with patch.dict(crmshmod.__salt__, {'cmd.retcode': mock_cmd_run}):
            result = crmshmod.configure_rsc_defaults('item', 'value')
            assert result
            mock_cmd_run.assert_called_once_with(
                '{crm_command} configure rsc_defaults {item}="{value}"'.format(
                    crm_command=crmshmod.CRM_COMMAND,
                    item='item',
                    value='value'))

        mock_cmd_run.reset_mock()

        with patch.dict(crmshmod.__salt__, {'cmd.retcode': mock_cmd_run}):
            result = crmshmod.configure_rsc_defaults('item', False)
            assert result
            mock_cmd_run.assert_called_once_with(
                '{crm_command} configure rsc_defaults {item}={value}'.format(
                    crm_command=crmshmod.CRM_COMMAND,
                    item='item',
                    value='false'))

    def test_configure_op_defaults(self):
        '''
        Test configure_op_defaults method
        '''
        mock_cmd_run = MagicMock(return_value=True)

        with patch.dict(crmshmod.__salt__, {'cmd.retcode': mock_cmd_run}):
            result = crmshmod.configure_op_defaults('item', 'value')
            assert result
            mock_cmd_run.assert_called_once_with(
                '{crm_command} configure op_defaults {item}="{value}"'.format(
                    crm_command=crmshmod.CRM_COMMAND,
                    item='item',
                    value='value'))

        mock_cmd_run.reset_mock()

        with patch.dict(crmshmod.__salt__, {'cmd.retcode': mock_cmd_run}):
            result = crmshmod.configure_op_defaults('item', False)
            assert result
            mock_cmd_run.assert_called_once_with(
                '{crm_command} configure op_defaults {item}={value}'.format(
                    crm_command=crmshmod.CRM_COMMAND,
                    item='item',
                    value='false'))

    def test_detect_cloud_py2(self):
        '''
        Test detect_cloud
        '''
        mock_versin = '3.0.0'
        mock_cmd_run = MagicMock(return_value='my-cloud ')

        with patch.dict(crmshmod.__salt__, {
                'crm.version': mock_versin,
                'cmd.run': mock_cmd_run}):
            result = crmshmod.detect_cloud()
            assert result == 'my-cloud'

        mock_cmd_run.assert_called_once_with(
            'python -c "from crmsh import utils; print(utils.detect_cloud());"')

    def test_detect_cloud_py3(self):
        '''
        Test detect_cloud
        '''
        mock_versin = '4.0.0'
        mock_cmd_run = MagicMock(return_value='my-cloud ')

        with patch.dict(crmshmod.__salt__, {
                'crm.version': mock_versin,
                'cmd.run': mock_cmd_run}):
            result = crmshmod.detect_cloud()
            assert result == 'my-cloud'

        mock_cmd_run.assert_called_once_with(
            'python3 -c "from crmsh import utils; print(utils.detect_cloud());"')
