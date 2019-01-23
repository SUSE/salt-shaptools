
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
import salt.states.crmshmod as crmshmod


@skipIf(NO_MOCK, NO_MOCK_REASON)
class CrmshmodTestCase(TestCase, LoaderModuleMockMixin):
    '''
    Test cases for salt.states.crm
    '''
    def setup_loader_modules(self):
        return {crmshmod: {'__opts__': {'test': False}}}

    # 'absent' function tests

    def test_absent_absent(self):
        '''
        Test to check absent when cluster is already absent
        '''

        ret = {'name': 'localhost',
               'changes': {},
               'result': True,
               'comment': 'Cluster is not running already'}

        mock_status = MagicMock(return_value=1)
        with patch.dict(crmshmod.__salt__, {'crm.status': mock_status}):
            assert crmshmod.cluster_absent('localhost') == ret
            mock_status.assert_called_once_with()

    def test_absent_test(self):
        '''
        Test to check absent in test mode
        '''

        ret = {'name': 'localhost',
               'changes': {'name': 'localhost'},
               'result': None,
               'comment': 'Cluster in {} would be removed'.format('localhost')}

        mock_status = MagicMock(return_value=0)
        with patch.dict(crmshmod.__salt__, {'crm.status': mock_status}):
            with patch.dict(crmshmod.__opts__, {'test': True}):
                assert crmshmod.cluster_absent('localhost') == ret
            mock_status.assert_called_once_with()

    def test_absent(self):
        '''
        Test to check absent when cluster is running
        '''

        ret = {'name': 'localhost',
               'changes': {'name': 'localhost'},
               'result': True,
               'comment': 'Cluster removed'}

        mock_status = MagicMock(return_value=0)
        mock_remove = MagicMock(return_value=0)
        with patch.dict(crmshmod.__salt__, {'crm.status': mock_status,
                                            'crm.cluster_remove': mock_remove}):
            assert crmshmod.cluster_absent('localhost') == ret
            mock_status.assert_called_once_with()
            mock_remove.assert_called_once_with(
                host='localhost', force=True, quiet=None)

    def test_absent_error(self):
        '''
        Test to check absent when removal fails
        '''

        ret = {'name': 'localhost',
               'changes': {'name': 'localhost'},
               'result': False,
               'comment': 'Error removing cluster'}

        mock_status = MagicMock(return_value=0)
        mock_remove = MagicMock(return_value=1)
        with patch.dict(crmshmod.__salt__, {'crm.status': mock_status,
                                            'crm.cluster_remove': mock_remove}):
            assert crmshmod.cluster_absent('localhost') == ret
            mock_status.assert_called_once_with()
            mock_remove.assert_called_once_with(
                host='localhost', force=True, quiet=None)

    def test_absent_command_error(self):
        '''
        Test to check absent when command execution error is raised
        '''

        ret = {'name': 'localhost',
               'changes': {},
               'result': False,
               'comment': 'cluster command error'}

        mock_status = MagicMock(return_value=0)
        mock_remove = MagicMock(
            side_effect=exceptions.CommandExecutionError('cluster command error'))
        with patch.dict(crmshmod.__salt__, {'crm.status': mock_status,
                                            'crm.cluster_remove': mock_remove}):
            assert crmshmod.cluster_absent('localhost') == ret
            mock_status.assert_called_once_with()
            mock_remove.assert_called_once_with(
                host='localhost', force=True, quiet=None)

    # 'initialized' function tests

    def test_initialized_initialized(self):
        '''
        Test to check initialized when cluster is already initialized
        '''

        ret = {'name': 'hacluster',
               'changes': {},
               'result': True,
               'comment': 'Cluster is already initialized'}

        mock_status = MagicMock(return_value=0)
        with patch.dict(crmshmod.__salt__, {'crm.status': mock_status}):
            assert crmshmod.cluster_initialized('hacluster') == ret
            mock_status.assert_called_once_with()

    def test_initialized_test(self):
        '''
        Test to check initialized in test mode
        '''

        ret = {'name': 'hacluster',
               'changes': {'name': 'hacluster'},
               'result': None,
               'comment': '{} would be initialized'.format('hacluster')}

        mock_status = MagicMock(return_value=1)
        with patch.dict(crmshmod.__salt__, {'crm.status': mock_status}):
            with patch.dict(crmshmod.__opts__, {'test': True}):
                assert crmshmod.cluster_initialized('hacluster') == ret
            mock_status.assert_called_once_with()

    def test_initialized(self):
        '''
        Test to check initialized when cluster is not created yet
        '''

        ret = {'name': 'hacluster',
               'changes': {'name': 'hacluster'},
               'result': True,
               'comment': 'Cluster initialized'}

        mock_status = MagicMock(return_value=1)
        mock_init = MagicMock(return_value=0)
        with patch.dict(crmshmod.__salt__, {'crm.status': mock_status,
                                            'crm.cluster_init': mock_init}):
            assert crmshmod.cluster_initialized(
                name='hacluster',
                watchdog='/dev/watchdog',
                interface='eth0',
                unicast=False,
                admin_ip='192.168.1.50',
                sbd=True,
                sbd_dev='/dev/sbd',
                quiet=False) == ret
            mock_status.assert_called_once_with()
            mock_init.assert_called_once_with(
                name='hacluster',
                watchdog='/dev/watchdog',
                interface='eth0',
                unicast=False,
                admin_ip='192.168.1.50',
                sbd=True,
                sbd_dev='/dev/sbd',
                quiet=False)

    def test_initialized_error(self):
        '''
        Test to check initialized when initialization fails
        '''

        ret = {'name': 'hacluster',
               'changes': {'name': 'hacluster'},
               'result': False,
               'comment': 'Error initialazing cluster'}

        mock_status = MagicMock(return_value=1)
        mock_init = MagicMock(return_value=1)
        with patch.dict(crmshmod.__salt__, {'crm.status': mock_status,
                                            'crm.cluster_init': mock_init}):
            assert crmshmod.cluster_initialized(
                name='hacluster',
                watchdog='/dev/watchdog',
                interface='eth0',
                unicast=False,
                admin_ip='192.168.1.50',
                sbd=True,
                sbd_dev='/dev/sbd',
                quiet=False) == ret
            mock_status.assert_called_once_with()
            mock_init.assert_called_once_with(
                name='hacluster',
                watchdog='/dev/watchdog',
                interface='eth0',
                unicast=False,
                admin_ip='192.168.1.50',
                sbd=True,
                sbd_dev='/dev/sbd',
                quiet=False)

    def test_initialized_command_error(self):
        '''
        Test to check initialized when command execution error is raised
        '''

        ret = {'name': 'hacluster',
               'changes': {},
               'result': False,
               'comment': 'cluster command error'}

        mock_status = MagicMock(return_value=1)
        mock_init = MagicMock(
            side_effect=exceptions.CommandExecutionError('cluster command error'))
        with patch.dict(crmshmod.__salt__, {'crm.status': mock_status,
                                            'crm.cluster_init': mock_init}):
            assert crmshmod.cluster_initialized(
                name='hacluster',
                watchdog='/dev/watchdog',
                interface='eth0',
                unicast=False,
                admin_ip='192.168.1.50',
                sbd=True,
                sbd_dev='/dev/sbd',
                quiet=False) == ret
            mock_status.assert_called_once_with()
            mock_init.assert_called_once_with(
                name='hacluster',
                watchdog='/dev/watchdog',
                interface='eth0',
                unicast=False,
                admin_ip='192.168.1.50',
                sbd=True,
                sbd_dev='/dev/sbd',
                quiet=False)

    # 'joined' function tests

    def test_joined_joined(self):
        '''
        Test to check joined when node is already joined to cluster
        '''

        ret = {'name': 'master',
               'changes': {},
               'result': True,
               'comment': 'Node is already joined to a cluster'}

        mock_status = MagicMock(return_value=0)
        with patch.dict(crmshmod.__salt__, {'crm.status': mock_status}):
            assert crmshmod.cluster_joined('master') == ret
            mock_status.assert_called_once_with()

    def test_joined_test(self):
        '''
        Test to check joined in test mode
        '''

        ret = {'name': 'master',
               'changes': {'name': 'master'},
               'result': None,
               'comment': 'Node would be joined to {}'.format('master')}

        mock_status = MagicMock(return_value=1)
        with patch.dict(crmshmod.__salt__, {'crm.status': mock_status}):
            with patch.dict(crmshmod.__opts__, {'test': True}):
                assert crmshmod.cluster_joined('master') == ret
            mock_status.assert_called_once_with()

    def test_joined(self):
        '''
        Test to check joined when cluster is not joined yet
        '''

        ret = {'name': 'master',
               'changes': {'name': 'master'},
               'result': True,
               'comment': 'Node joined to cluster'}

        mock_status = MagicMock(return_value=1)
        mock_join = MagicMock(return_value=0)
        with patch.dict(crmshmod.__salt__, {'crm.status': mock_status,
                                            'crm.cluster_join': mock_join}):
            assert crmshmod.cluster_joined(
                name='master',
                watchdog='/dev/watchdog',
                interface='eth0',
                quiet=False) == ret
            mock_status.assert_called_once_with()
            mock_join.assert_called_once_with(
                host='master',
                watchdog='/dev/watchdog',
                interface='eth0',
                quiet=False)

    def test_joined_error(self):
        '''
        Test to check joined when joining fails
        '''

        ret = {'name': 'master',
               'changes': {'name': 'master'},
               'result': False,
               'comment': 'Error joining to cluster'}

        mock_status = MagicMock(return_value=1)
        mock_join = MagicMock(return_value=1)
        with patch.dict(crmshmod.__salt__, {'crm.status': mock_status,
                                            'crm.cluster_join': mock_join}):
            assert crmshmod.cluster_joined(
                name='master',
                watchdog='/dev/watchdog',
                interface='eth0',
                quiet=False) == ret
            mock_status.assert_called_once_with()
            mock_join.assert_called_once_with(
                host='master',
                watchdog='/dev/watchdog',
                interface='eth0',
                quiet=False)

    def test_joined_command_error(self):
        '''
        Test to check joined when command execution error is raised
        '''

        ret = {'name': 'master',
               'changes': {},
               'result': False,
               'comment': 'cluster command error'}

        mock_status = MagicMock(return_value=1)
        mock_join = MagicMock(
            side_effect=exceptions.CommandExecutionError('cluster command error'))
        with patch.dict(crmshmod.__salt__, {'crm.status': mock_status,
                                            'crm.cluster_join': mock_join}):
            assert crmshmod.cluster_joined(
                name='master',
                watchdog='/dev/watchdog',
                interface='eth0',
                quiet=False) == ret
            mock_status.assert_called_once_with()
            mock_join.assert_called_once_with(
                host='master',
                watchdog='/dev/watchdog',
                interface='eth0',
                quiet=False)

    # 'configured' function tests

    def test_configured_test(self):
        '''
        Test to check configured in test mode
        '''

        ret = {'name': 'update',
               'changes': {'method': 'update', 'url': 'file.config'},
               'result': None,
               'comment': 'Cluster would be configured with method {} and file {}'.format(
                   'update', 'file.config')}

        with patch.dict(crmshmod.__opts__, {'test': True}):
            assert crmshmod.cluster_configured('update', 'file.config') == ret

    def test_configured_not_cluster(self):
        '''
        Test to check configured when the cluster is not initialized
        '''

        ret = {'name': 'update',
               'changes': {},
               'result': False,
               'comment': 'Cluster is not created yet. Run cluster_initialized before'}

        mock_status = MagicMock(return_value=1)
        with patch.dict(crmshmod.__salt__, {'crm.status': mock_status}):
            assert crmshmod.cluster_configured('update', 'file.config') == ret
            mock_status.assert_called_once_with()

    def test_configured(self):
        '''
        Test to check configured when configuration is applied properly
        '''

        ret = {'name': 'update',
               'changes': {'method': 'update', 'url': 'file.config'},
               'result': True,
               'comment': 'Cluster properly configured'}

        mock_status = MagicMock(return_value=0)
        mock_configured = MagicMock(return_value=0)
        with patch.dict(crmshmod.__salt__, {'crm.status': mock_status,
                                            'crm.configure_load': mock_configured}):
            assert crmshmod.cluster_configured(
                method='update',
                url='file.config',
                is_xml=False) == ret
            mock_status.assert_called_once_with()
            mock_configured.assert_called_once_with(
                method='update',
                url='file.config',
                is_xml=False)

    def test_configured_error(self):
        '''
        Test to check configured when configuration fails
        '''

        ret = {'name': 'update',
               'changes': {},
               'result': False,
               'comment': 'Error configuring the cluster with method {} and file {}'.format(
                   'update', 'file.config')}

        mock_status = MagicMock(return_value=0)
        mock_configured = MagicMock(return_value=1)
        with patch.dict(crmshmod.__salt__, {'crm.status': mock_status,
                                            'crm.configure_load': mock_configured}):
            assert crmshmod.cluster_configured(
                method='update',
                url='file.config',
                is_xml=False) == ret
            mock_status.assert_called_once_with()
            mock_configured.assert_called_once_with(
                method='update',
                url='file.config',
                is_xml=False)

    def test_configured_command_error(self):
        '''
        Test to check configured when command execution error is raised
        '''

        ret = {'name': 'update',
               'changes': {},
               'result': False,
               'comment': 'cluster command error'}

        mock_status = MagicMock(return_value=0)
        mock_configured = MagicMock(
            side_effect=exceptions.CommandExecutionError('cluster command error'))
        with patch.dict(crmshmod.__salt__, {'crm.status': mock_status,
                                            'crm.configure_load': mock_configured}):
            assert crmshmod.cluster_configured(
                method='update',
                url='file.config',
                is_xml=False) == ret
            mock_status.assert_called_once_with()
            mock_configured.assert_called_once_with(
                method='update',
                url='file.config',
                is_xml=False)
