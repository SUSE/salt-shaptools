
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
        with patch.dict(crmshmod.__salt__, {'crm.cluster_status': mock_status}):
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
        with patch.dict(crmshmod.__salt__, {'crm.cluster_status': mock_status}):
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
        with patch.dict(crmshmod.__salt__, {'crm.cluster_status': mock_status,
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
        with patch.dict(crmshmod.__salt__, {'crm.cluster_status': mock_status,
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
        with patch.dict(crmshmod.__salt__, {'crm.cluster_status': mock_status,
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
        with patch.dict(crmshmod.__salt__, {'crm.cluster_status': mock_status}):
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
        with patch.dict(crmshmod.__salt__, {'crm.cluster_status': mock_status}):
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
        with patch.dict(crmshmod.__salt__, {'crm.cluster_status': mock_status,
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
        with patch.dict(crmshmod.__salt__, {'crm.cluster_status': mock_status,
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
        with patch.dict(crmshmod.__salt__, {'crm.cluster_status': mock_status,
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
        with patch.dict(crmshmod.__salt__, {'crm.cluster_status': mock_status}):
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
        with patch.dict(crmshmod.__salt__, {'crm.cluster_status': mock_status}):
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
        with patch.dict(crmshmod.__salt__, {'crm.cluster_status': mock_status,
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
        with patch.dict(crmshmod.__salt__, {'crm.cluster_status': mock_status,
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
        with patch.dict(crmshmod.__salt__, {'crm.cluster_status': mock_status,
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
