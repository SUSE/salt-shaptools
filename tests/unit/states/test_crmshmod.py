
# -*- coding: utf-8 -*-
'''
    :codeauthor: Xabier Arbulu Insausti <xarbulu@suse.com>
'''
# Import Python libs
from __future__ import absolute_import, unicode_literals, print_function

import sys
import collections
from salt import exceptions

# Import Salt Testing Libs
from tests.support.mixins import LoaderModuleMockMixin
from tests.support.unit import skipIf, TestCase
from tests.support import mock
from tests.support.mock import (
    mock_open,
    MagicMock,
    patch
)

# Import Salt Libs
import salt.states.crmshmod as crmshmod


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
               'comment': 'Cluster is already not running'}

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
               'comment': 'Cluster node {} would be removed'.format('localhost')}

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
               'comment': 'Cluster node removed'}

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
               'comment': 'Error removing cluster node'}

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
                no_overwrite_sshkey=True,
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
                no_overwrite_sshkey=True,
                qnetd_hostname=None,
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
                no_overwrite_sshkey=True,
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
                no_overwrite_sshkey=True,
                qnetd_hostname=None,
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
                no_overwrite_sshkey=False,
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
                no_overwrite_sshkey=False,
                qnetd_hostname=None,
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
               'comment': 'Node joined to the cluster'}

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
               'comment': 'Error joining to the cluster'}

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
                name='update',
                url='file.config',
                is_xml=False) == ret
            mock_status.assert_called_once_with()
            mock_configured.assert_called_once_with(
                method='update',
                url='file.config',
                is_xml=False,
                force=False)

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
                name='update',
                url='file.config',
                is_xml=False,
                force=True) == ret
            mock_status.assert_called_once_with()
            mock_configured.assert_called_once_with(
                method='update',
                url='file.config',
                is_xml=False,
                force=True)

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
                name='update',
                url='file.config',
                is_xml=False) == ret
            mock_status.assert_called_once_with()
            mock_configured.assert_called_once_with(
                method='update',
                url='file.config',
                is_xml=False,
                force=False)

    def test_convert2dict(self):
        corofile = """
# Please read the corosync.conf.5 manual page
totem {
    version: 2
    max_messages: 20
    interface {
        ringnumber: 0

    }
    transport: udpu
}

logging {
    timestamp: on
    logger_subsys {
        debug: off
    }

}

quorum {
    expected_votes: 1
    two_node: 0
}"""

        corodict, _ = crmshmod._convert2dict(corofile.splitlines())

        assert corodict == {
            'totem': {
                'version': '2',
                'max_messages': '20',
                'interface': {
                    'ringnumber': '0'
                },
                'transport': 'udpu'
            },
            'logging': {
                'timestamp': 'on',
                'logger_subsys': {
                    'debug': 'off'
                }
            },
            'quorum': {
                'expected_votes': '1',
                'two_node': '0'
            }
        }

    def test_merge_dicts1(self):
        main_dict = {
            'a': {
                'b': 1,
                'c': 2
            },
            'd': 3
        }
        changed_dict = {
            'a': {
                'c': 4
            },
            'd': 5
        }
        merged_dict, applied_changes = crmshmod._mergedicts(
            main_dict, changed_dict, {}, '')

        assert merged_dict == {
            'a': {
                'b': 1,
                'c': 4
            },
            'd': 5
        }

        assert applied_changes == {
            '.a.c': 4,
            '.d': 5
        }

    def test_merge_dicts2(self):
        main_dict = {
            'a': {
                'b': {
                    'f': 7
                },
                'c': 2
            },
            'd': 3
        }
        changed_dict = {
            'a': {
                'b': {
                    'f': 8
                },
            },
            'd': 5
        }
        merged_dict, applied_changes = crmshmod._mergedicts(
            main_dict, changed_dict, {}, '')

        assert merged_dict == {
            'a': {
                'b': {
                    'f': 8
                },
                'c': 2
            },
            'd': 5
        }

        assert applied_changes == {
            '.d': 5,
            '.a.b.f': 8
        }

    def test_merge_dicts3(self):
        main_dict = {
            'a': {
                'b': 1,
                'c': 2
            },
            'd': 3
        }
        changed_dict = {
            'e': {
                'c': 4
            },
            'a': {
                'b': 3
            },
            'd': 5
        }
        merged_dict, applied_changes = crmshmod._mergedicts(
            main_dict, changed_dict, {}, '')

        assert merged_dict == {
            'a': {
                'b': 3,
                'c': 2
            },
            'e': {
                'c': 4
            },
            'd': 5
        }

        assert applied_changes == {
            '.d': 5,
            '.a.b': 3,
            '.e': {'c': 4}
        }

    def test_convert2corosync(self):
        main_dict = {
            'a': {
                'b': {
                    'f': 7
                },
                'c': 2
            },
            'd': 3
        }

        output = crmshmod._convert2corosync(main_dict, '')

        # Py2 and py3 have different way of ordering the `items` method
        # For the functionality this does not really affect
        if sys.version_info[0] == 2:
            assert output == "a {\n\tc: 2\n\tb {\n\t\tf: 7\n\t}\n}\nd: 3\n"
        else:
            assert output == "a {\n\tb {\n\t\tf: 7\n\t}\n\tc: 2\n}\nd: 3\n"

    @mock.patch('salt.states.crmshmod._convert2dict')
    @mock.patch('salt.states.crmshmod._mergedicts')
    def test_corosync_updated_already(self, mock_mergedicts, mock_convert2dict):
        '''
        Test to check corosync_updated when configuration is already applied
        '''

        ret = {'name': '/etc/corosync/corosync.conf',
               'changes': {},
               'result': True,
               'comment': 'Corosync already has the required configuration'}

        mock_convert2dict.return_value = ({'data': 1}, {})
        mock_mergedicts.return_value = ({}, {})

        file_content = "my corosync file content\nmy corosync file 2nd line content"
        with patch("salt.utils.files.fopen", mock_open(read_data=file_content)):
            assert crmshmod.corosync_updated(
                name='/etc/corosync/corosync.conf',
                data={'my_data': 1}) == ret

        mock_convert2dict.assert_called_once_with(
            ['my corosync file content', 'my corosync file 2nd line content']
        )
        mock_mergedicts.assert_called_once_with(
            {'data': 1}, {'my_data': 1}, {})

    @mock.patch('salt.states.crmshmod._convert2dict')
    @mock.patch('salt.states.crmshmod._mergedicts')
    def test_corosync_updated_test(self, mock_mergedicts, mock_convert2dict):
        '''
        Test to check corosync_updated in test mode
        '''

        ret = {'name': '/etc/corosync/corosync.conf',
               'changes': {'data': 1},
               'result': None,
               'comment': 'Corosync configuration would be update'}

        mock_convert2dict.return_value = ({}, {})
        mock_mergedicts.return_value = ({}, {'data': 1})

        file_content = "my corosync file content\nmy corosync file 2nd line content"
        with patch.dict(crmshmod.__opts__, {'test': True}):
            with patch("salt.utils.files.fopen", mock_open(read_data=file_content)):
                assert crmshmod.corosync_updated(
                    name='/etc/corosync/corosync.conf',
                    data={'my_data': 1}) == ret

        mock_convert2dict.assert_called_once_with(
            ['my corosync file content', 'my corosync file 2nd line content']
        )
        mock_mergedicts.assert_called_once_with(
            {}, {'my_data': 1}, {})

    @mock.patch('salt.states.crmshmod._convert2corosync')
    @mock.patch('salt.states.crmshmod._convert2dict')
    @mock.patch('salt.states.crmshmod._mergedicts')
    def test_corosync_updated(self, mock_mergedicts, mock_convert2dict, mock_convert2corosync):
        '''
        Test to check corosync_updated when configuration is applied
        '''

        ret = {'name': '/etc/corosync/corosync.conf',
               'changes': {'change1': 1, 'change2': 2},
               'result': True,
               'comment': 'Corosync configuration file updated'}

        mock_copy = MagicMock()
        mock_write = MagicMock()
        mock_convert2dict.return_value = ({'data': 1}, {})
        mock_mergedicts.return_value = ({'updated': 2}, {'change1': 1, 'change2': 2})
        mock_convert2corosync.return_value = 'new content'

        file_content = "my corosync file content\nmy corosync file 2nd line content"

        with patch.dict(crmshmod.__salt__, {'file.copy': mock_copy,
                                            'file.write': mock_write}):
            with patch("salt.utils.files.fopen", mock_open(read_data=file_content)):
                assert crmshmod.corosync_updated(
                    name='/etc/corosync/corosync.conf',
                    data={'my_data': 1}) == ret

        mock_convert2dict.assert_called_once_with(
            ['my corosync file content', 'my corosync file 2nd line content']
        )
        mock_mergedicts.assert_called_once_with(
            {'data': 1}, {'my_data': 1}, {})

        mock_convert2corosync.assert_called_once_with({'updated': 2})

        mock_copy.assert_called_once_with(
            '/etc/corosync/corosync.conf', '/etc/corosync/corosync.conf.backup')

        mock_write.assert_called_once_with(
            '/etc/corosync/corosync.conf', 'new content')

    # 'cluster_properties_present' function tests

    def test_properties_present_no_cluster(self):
        '''
        Test to check properties_present when the cluster is not created
        '''

        ret = {'name': 'name',
               'changes': {},
               'result': False,
               'comment': 'Cluster is not created yet. Run cluster_initialized before'}

        mock_status = MagicMock(return_value=1)
        with patch.dict(crmshmod.__salt__, {'crm.status': mock_status}):
            assert crmshmod.cluster_properties_present('name', {'data': 'value'}) == ret
            mock_status.assert_called_once_with()

    def test_properties_present_test(self):
        '''
        Test to check properties_present in test mode
        '''

        ret = {'name': 'name',
               'changes': {'data': 'value'},
               'result': None,
               'comment': 'Cluster properties would be configured'}

        mock_status = MagicMock(return_value=0)
        with patch.dict(crmshmod.__salt__, {'crm.status': mock_status}):
            with patch.dict(crmshmod.__opts__, {'test': True}):
                assert crmshmod.cluster_properties_present('name', {'data': 'value'}) == ret
            mock_status.assert_called_once_with()

    def test_properties_present(self):
        '''
        Test to check properties_present
        '''

        ret = {'name': 'name',
               'changes': {'data1': 'value1', 'data2': 'value2'},
               'result': True,
               'comment': 'Cluster properties configured'}

        mock_status = MagicMock(return_value=0)
        mock_configure_get_property = MagicMock()
        mock_configure_property = MagicMock()
        with patch.dict(crmshmod.__salt__, {'crm.status': mock_status,
                                            'crm.configure_get_property': mock_configure_get_property,
                                            'crm.configure_property': mock_configure_property}):
            assert crmshmod.cluster_properties_present(
                name='name',
                properties={'data1': 'value1', 'data2': 'value2'}) == ret
            mock_status.assert_called_once_with()
            mock_configure_get_property.assert_has_calls([
                mock.call(option='data1'),
                mock.call(option='data2')
            ])
            mock_configure_property.assert_has_calls([
                mock.call(option='data1', value='value1'),
                mock.call(option='data2', value='value2')
            ])

    def test_properties_present_error(self):
        '''
        Test to check properties_present with an error
        '''

        ret = {'name': 'name',
               'changes': {'data3': 'value3'},
               'result': False,
               'comment': 'Error configuring the properties data1, data2'}

        mock_status = MagicMock(return_value=0)
        mock_configure_get_property = MagicMock(side_effect=[
            exceptions.CommandExecutionError('err1'),
            exceptions.CommandExecutionError('err2'),
            "value3"
        ])
        mock_configure_property = MagicMock()
        # We need to create the dictionary this way, otherwise the items output is different in py2 and py3
        data = collections.OrderedDict()
        data['data1'] = 'value1'
        data['data2'] = 'value2'
        data['data3'] = 'value3'
        with patch.dict(crmshmod.__salt__, {'crm.status': mock_status,
                                            'crm.configure_get_property': mock_configure_get_property,
                                            'crm.configure_property': mock_configure_property}):
            assert crmshmod.cluster_properties_present(
                name='name',
                properties=data) == ret
            mock_status.assert_called_once_with()
            mock_configure_get_property.assert_has_calls([
                mock.call(option='data1'),
                mock.call(option='data2'),
                mock.call(option='data3')
            ])
            mock_configure_property.assert_has_calls([
                mock.call(option='data3', value='value3')
            ])

    # 'cluster_rsc_defaults_present' function tests

    def test_rsc_defaults_present_no_cluster(self):
        '''
        Test to check rsc_defaults_present when the cluster is not created
        '''

        ret = {'name': 'name',
               'changes': {},
               'result': False,
               'comment': 'Cluster is not created yet. Run cluster_initialized before'}

        mock_status = MagicMock(return_value=1)
        with patch.dict(crmshmod.__salt__, {'crm.status': mock_status}):
            assert crmshmod.cluster_rsc_defaults_present('name', {'data': 'value'}) == ret
            mock_status.assert_called_once_with()

    def test_rsc_defaults_present_test(self):
        '''
        Test to check rsc_defaults_present in test mode
        '''

        ret = {'name': 'name',
               'changes': {'data': 'value'},
               'result': None,
               'comment': 'Cluster rsc_defaults would be configured'}

        mock_status = MagicMock(return_value=0)
        with patch.dict(crmshmod.__salt__, {'crm.status': mock_status}):
            with patch.dict(crmshmod.__opts__, {'test': True}):
                assert crmshmod.cluster_rsc_defaults_present('name', {'data': 'value'}) == ret
            mock_status.assert_called_once_with()

    def test_rsc_defaults_present(self):
        '''
        Test to check rsc_defaults_present
        '''

        ret = {'name': 'name',
               'changes': {'data1': 'value1', 'data2': 'value2'},
               'result': True,
               'comment': 'Cluster rsc_defaults configured'}

        mock_status = MagicMock(return_value=0)
        mock_configure_rsc_defaults = MagicMock()
        with patch.dict(crmshmod.__salt__, {'crm.status': mock_status,
                                            'crm.configure_rsc_defaults': mock_configure_rsc_defaults}):
            assert crmshmod.cluster_rsc_defaults_present(
                name='name',
                rsc_defaults={'data1': 'value1', 'data2': 'value2'}) == ret
            mock_status.assert_called_once_with()
            mock_configure_rsc_defaults.assert_has_calls([
                mock.call(option='data1', value='value1'),
                mock.call(option='data2', value='value2')
            ])

    # 'cluster_op_defaults_present' function tests

    def test_op_defaults_present_no_cluster(self):
        '''
        Test to check op_defaults_present when the cluster is not created
        '''

        ret = {'name': 'name',
               'changes': {},
               'result': False,
               'comment': 'Cluster is not created yet. Run cluster_initialized before'}

        mock_status = MagicMock(return_value=1)
        with patch.dict(crmshmod.__salt__, {'crm.status': mock_status}):
            assert crmshmod.cluster_op_defaults_present('name', {'data': 'value'}) == ret
            mock_status.assert_called_once_with()

    def test_op_defaults_present_test(self):
        '''
        Test to check op_defaults_present in test mode
        '''

        ret = {'name': 'name',
               'changes': {'data': 'value'},
               'result': None,
               'comment': 'Cluster op_defaults would be configured'}

        mock_status = MagicMock(return_value=0)
        with patch.dict(crmshmod.__salt__, {'crm.status': mock_status}):
            with patch.dict(crmshmod.__opts__, {'test': True}):
                assert crmshmod.cluster_op_defaults_present('name', {'data': 'value'}) == ret
            mock_status.assert_called_once_with()

    def test_op_defaults_present(self):
        '''
        Test to check op_defaults_present
        '''

        ret = {'name': 'name',
               'changes': {'data1': 'value1', 'data2': 'value2'},
               'result': True,
               'comment': 'Cluster op_defaults configured'}

        mock_status = MagicMock(return_value=0)
        mock_configure_op_defaults = MagicMock()
        with patch.dict(crmshmod.__salt__, {'crm.status': mock_status,
                                            'crm.configure_op_defaults': mock_configure_op_defaults}):
            assert crmshmod.cluster_op_defaults_present(
                name='name',
                op_defaults={'data1': 'value1', 'data2': 'value2'}) == ret
            mock_status.assert_called_once_with()
            mock_configure_op_defaults.assert_has_calls([
                mock.call(option='data1', value='value1'),
                mock.call(option='data2', value='value2')
            ])

    def test_cloud_grains_present_test(self):
        '''
        Test to check cloud_grains_present in test mode
        '''

        ret = {'name': 'name',
               'changes': {},
               'result': None,
               'comment': 'Cloud grains would be set'}

        with patch.dict(crmshmod.__opts__, {'test': True}):
            assert crmshmod.cloud_grains_present('name') == ret

    def test_cloud_grains_present(self):
        '''
        Test to check cloud_grains_present
        '''

        ret = {'name': 'name',
               'changes': {'cloud_provider': 'mycloud'},
               'result': True,
               'comment': 'Cloud grains set'}

        mock_detect_cloud = MagicMock(return_value='mycloud')
        mock_set_grains = MagicMock()
        with patch.dict(crmshmod.__salt__, {'crm.detect_cloud': mock_detect_cloud,
                                            'grains.set': mock_set_grains}):
            assert crmshmod.cloud_grains_present(name='name') == ret
            mock_detect_cloud.assert_called_once_with()
            mock_set_grains.assert_called_once_with('cloud_provider', 'mycloud')

    def test_cloud_grains_present_gcp(self):
        '''
        Test to check cloud_grains_present for gcp
        '''

        ret = {'name': 'name',
               'changes': {'cloud_provider': 'google-cloud-platform',
                           'gcp_instance_id': 'm_id',
                           'gcp_instance_name': 'm_name'},
               'result': True,
               'comment': 'Cloud grains set'}

        mock_detect_cloud = MagicMock(return_value='google-cloud-platform')
        mock_set_grains = MagicMock()
        mock_http_query = MagicMock(side_effect=[{'body': 'm_id'}, {'body': 'm_name'}])
        with patch.dict(crmshmod.__salt__, {'crm.detect_cloud': mock_detect_cloud,
                                            'grains.set': mock_set_grains,
                                            'http.query': mock_http_query}):
            assert crmshmod.cloud_grains_present(name='name') == ret
            mock_detect_cloud.assert_called_once_with()
            mock_http_query.assert_has_calls([
                mock.call(
                    url='http://metadata.google.internal/computeMetadata/v1/instance/id',
                    header_dict={"Metadata-Flavor": "Google"}),
                mock.call(
                    url='http://metadata.google.internal/computeMetadata/v1/instance/name',
                    header_dict={"Metadata-Flavor": "Google"})
            ])
            mock_set_grains.assert_has_calls([
                mock.call('cloud_provider', 'google-cloud-platform'),
                mock.call('gcp_instance_id', 'm_id'),
                mock.call('gcp_instance_name', 'm_name')
            ])
