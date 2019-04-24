# -*- coding: utf-8 -*-
'''
    :codeauthor: Jayesh Kariya <jayeshk@saltstack.com>
'''

# Import Python libs
from __future__ import absolute_import, print_function, unicode_literals

# Import Salt Testing Libs
from tests.support.mixins import LoaderModuleMockMixin
from tests.support.unit import TestCase, skipIf
from tests.support.mock import (
    MagicMock,
    patch,
    NO_MOCK,
    NO_MOCK_REASON
)

# Import Salt Libs
import salt.modules.drbd as drbd


@skipIf(NO_MOCK, NO_MOCK_REASON)
class DrbdTestCase(TestCase, LoaderModuleMockMixin):
    '''
    Test cases for salt.modules.drbd
    '''
    def setup_loader_modules(self):
        return {drbd: {}}

    # 'overview' function tests: 1

    def test_overview(self):
        '''
        Test if it shows status of the DRBD devices
        '''
        ret = {'connection state': 'True',
               'device': 'Stack',
               'fs': 'None',
               'local disk state': 'UpToDate',
               'local role': 'master',
               'minor number': 'Salt',
               'mountpoint': 'True',
               'partner disk state': 'UpToDate',
               'partner role': 'minion',
               'percent': '888',
               'remains': '666',
               'total size': '50',
               'used': '50'}
        mock = MagicMock(return_value='Salt:Stack True master/minion \
        UpToDate/UpToDate True None 50 50 666 888')
        with patch.dict(drbd.__salt__, {'cmd.run': mock}):
            self.assertDictEqual(drbd.overview(), ret)

        ret = {'connection state': 'True',
               'device': 'Stack',
               'local disk state': 'UpToDate',
               'local role': 'master',
               'minor number': 'Salt',
               'partner disk state': 'partner',
               'partner role': 'minion',
               'synched': '5050',
               'synchronisation: ': 'syncbar'}
        mock = MagicMock(return_value='Salt:Stack True master/minion \
        UpToDate/partner syncbar None 50 50')
        with patch.dict(drbd.__salt__, {'cmd.run': mock}):
            self.assertDictEqual(drbd.overview(), ret)

    def test_status(self):
        '''
        Test if it shows status of the DRBD resources via drbdadm
        '''
        ret = [{'local role': 'Primary',
                'local volumes': [{'disk': 'UpToDate'}],
                'peer nodes': [{'peer volumes': [{'done': '96.47',
                    'peer-disk': 'Inconsistent', 'replication': 'SyncSource'}],
                'peernode name': 'opensuse-node2',
                'role': 'Secondary'}],
                'resource name': 'single'}]

        fake = {}
        fake['stdout'] = '''
single role:Primary
  disk:UpToDate
  opensuse-node2 role:Secondary
    replication:SyncSource peer-disk:Inconsistent done:96.47
'''
        fake['stderr'] = ""
        fake['retcode'] = 0

        mock = MagicMock(return_value=fake)

        with patch.dict(drbd.__salt__, {'cmd.run_all': mock}):
            try:  # python2
                self.assertItemsEqual(drbd.status(), ret)
            except AttributeError:  # python3
                self.assertCountEqual(drbd.status(), ret)

        ret = [{'local role': 'Primary',
                'local volumes': [{'disk': 'UpToDate', 'volume': '0'},
                                  {'disk': 'UpToDate', 'volume': '1'}
                                 ],
                'peer nodes': [{'peer volumes': [{'peer-disk': 'UpToDate', 'volume': '0'},
                                                 {'peer-disk': 'UpToDate', 'volume': '1'}
                                                ],
                                'peernode name': 'node2',
                                'role': 'Secondary'},
                               {'peer volumes': [{'peer-disk': 'UpToDate', 'volume': '0'},
                                                 {'peer-disk': 'UpToDate', 'volume': '1'}
                                                ],
                                'peernode name': 'node3',
                                'role': 'Secondary'}
                              ],
                'resource name': 'test'},
               {'local role': 'Primary',
                'local volumes': [{'disk': 'UpToDate', 'volume': '0'},
                                  {'disk': 'UpToDate', 'volume': '1'}
                                 ],
                'peer nodes': [{'peer volumes': [{'peer-disk': 'UpToDate', 'volume': '0'},
                                                 {'peer-disk': 'UpToDate', 'volume': '1'}
                                                ],
                                'peernode name': 'node2',
                                'role': 'Secondary'},
                               {'peer volumes': [{'peer-disk': 'UpToDate', 'volume': '0'},
                                                 {'peer-disk': 'UpToDate', 'volume': '1'}
                                                ],
                                'peernode name': 'node3',
                                'role': 'Secondary'}
                              ],
                'resource name': 'res'}
              ]

        fake = {}
        fake['stdout'] = '''
res role:Primary
  volume:0 disk:UpToDate
  volume:1 disk:UpToDate
  node2 role:Secondary
    volume:0 peer-disk:UpToDate
    volume:1 peer-disk:UpToDate
  node3 role:Secondary
    volume:0 peer-disk:UpToDate
    volume:1 peer-disk:UpToDate

test role:Primary
  volume:0 disk:UpToDate
  volume:1 disk:UpToDate
  node2 role:Secondary
    volume:0 peer-disk:UpToDate
    volume:1 peer-disk:UpToDate
  node3 role:Secondary
    volume:0 peer-disk:UpToDate
    volume:1 peer-disk:UpToDate

'''
        fake['stderr'] = ""
        fake['retcode'] = 0

        mock = MagicMock(return_value=fake)

        with patch.dict(drbd.__salt__, {'cmd.run_all': mock}):
            try:  # python2
                self.assertItemsEqual(drbd.status(), ret)
            except AttributeError:  # python3
                self.assertCountEqual(drbd.status(), ret)

    def test_createmd(self):
        '''
        Test if createmd function work well
        '''
        mock = MagicMock(return_value=True)

        with patch.dict(drbd.__salt__, {'cmd.retcode': mock}):
            self.assertEqual(drbd.createmd(), True)
            mock.assert_called_once_with(['drbdadm', 'create-md', 'all', '--force'])

    def test_up(self):
        '''
        Test if up function work well
        '''
        mock = MagicMock(return_value=True)

        with patch.dict(drbd.__salt__, {'cmd.retcode': mock}):
            self.assertEqual(drbd.up(), True)
            mock.assert_called_once_with(['drbdadm', 'up', 'all'])

    def test_down(self):
        '''
        Test if down function work well
        '''
        mock = MagicMock(return_value=True)

        with patch.dict(drbd.__salt__, {'cmd.retcode': mock}):
            self.assertEqual(drbd.down(), True)
            mock.assert_called_once_with(['drbdadm', 'down', 'all'])

    def test_primary(self):
        '''
        Test if primary function work well
        '''
        # SubTest1:
        mock = MagicMock(return_value=True)

        with patch.dict(drbd.__salt__, {'cmd.retcode': mock}):
            self.assertEqual(drbd.primary(), True)
            mock.assert_called_once_with(['drbdadm', 'primary', 'all'])

        # SubTest2:
        mock = MagicMock(return_value=True)

        with patch.dict(drbd.__salt__, {'cmd.retcode': mock}):
            self.assertEqual(drbd.primary(force=True), True)
            mock.assert_called_once_with(['drbdadm', 'primary', 'all', '--force'])

    def test_secondary(self):
        '''
        Test if secondary function work well
        '''
        mock = MagicMock(return_value=True)

        with patch.dict(drbd.__salt__, {'cmd.retcode': mock}):
            self.assertEqual(drbd.secondary(), True)
            mock.assert_called_once_with(['drbdadm', 'secondary', 'all'])

    def test_adjust(self):
        '''
        Test if adjust function work well
        '''
        mock = MagicMock(return_value=True)

        with patch.dict(drbd.__salt__, {'cmd.retcode': mock}):
            self.assertEqual(drbd.adjust(), True)
            mock.assert_called_once_with(['drbdadm', 'adjust', 'all'])

    def test_setup_show(self):
        '''
        Test if setup_show function work well
        Test data is get from drbd-9.0.16/drbd-utils-9.6.0
        '''
        ret = [{'_this_host': {'node-id': 1,
                               'volumes': [{'device_minor': 5,
                                            'disk': {'on-io-error': 'pass_on'},
                                            'meta-disk': 'internal',
                                            'volume_nr': 0}]},
                'connections': [{'_peer_node_id': 2,
                                 'net': {'_name': 'salt-node3', 'ping-timeout': '10'},
                                 'path': {'_remote_host': 'ipv4 192.168.10.103:7990',
                                          '_this_host': 'ipv4 192.168.10.102:7990'},
                                 'volumes': [{'disk': {'c-fill-target': '20480s'},
                                              'volume_nr': 0}]}],
                'resource': 'beijing'}]

        fake = {}
        fake['stdout'] = '''
[
    {
        "resource": "beijing",
        "_this_host": {
            "node-id": 1,
            "volumes": [
                {
                    "volume_nr": 0,
                    "device_minor": 5,
                    "disk": "/dev/vdb1",
                    "meta-disk": "internal",
                    "disk": {
                        "on-io-error": "pass_on"
                    }
                }
            ]
        },
        "connections": [
            {
                "_peer_node_id": 2,
                "path": {
                    "_this_host": "ipv4 192.168.10.102:7990",
                    "_remote_host": "ipv4 192.168.10.103:7990"
                },
                "net": {
                    "ping-timeout": "10",
                    "_name": "salt-node3"
                },
                "volumes": [
                    {
                        "volume_nr": 0,
                        "disk": {
                            "c-fill-target": "20480s"
                        }
                    }
                ]
            }
        ]
    }
]
'''
        fake['stderr'] = ""
        fake['retcode'] = 0

        mock = MagicMock(return_value=fake)

        with patch.dict(drbd.__salt__, {'cmd.run_all': mock}):
            try:  # python2
                self.assertItemsEqual(drbd.setup_show(), ret)
            except AttributeError:  # python3
                self.assertCountEqual(drbd.setup_show(), ret)
            mock.assert_called_once_with(['drbdsetup', 'show', 'all', '--json'])

    def test_setup_status(self):
        '''
        Test if setup_status function work well
        Test data is get from drbd-9.0.16/drbd-utils-9.6.0
        '''
        ret = [{'connections': [{'ap-in-flight': 0,
                                 'congested': False,
                                 'connection-state': 'Connected',
                                 'name': 'salt-node3',
                                 'peer-node-id': 2,
                                 'peer-role': 'Secondary',
                                 'peer_devices': [{'has-online-verify-details': False,
                                                   'has-sync-details': False,
                                                   'out-of-sync': 0,
                                                   'peer-client': False,
                                                   'peer-disk-state': 'UpToDate',
                                                   'pending': 0,
                                                   'percent-in-sync': 100.0,
                                                   'received': 0,
                                                   'replication-state': 'Established',
                                                   'resync-suspended': 'no',
                                                   'sent': 0,
                                                   'unacked': 0,
                                                   'volume': 0}],
                                 'rs-in-flight': 0}],
                'devices': [{'al-writes': 0,
                             'bm-writes': 0,
                             'client': False,
                             'disk-state': 'UpToDate',
                             'lower-pending': 0,
                             'minor': 5,
                             'quorum': True,
                             'read': 0,
                             'size': 307152,
                             'upper-pending': 0,
                             'volume': 0,
                             'written': 0}],
                'name': 'beijing',
                'node-id': 1,
                'role': 'Primary',
                'suspended': False,
                'write-ordering': 'flush'}]

        fake = {}
        fake['stdout'] = '''
[
{
  "name": "beijing",
  "node-id": 1,
  "role": "Primary",
  "suspended": false,
  "write-ordering": "flush",
  "devices": [
    {
      "volume": 0,
      "minor": 5,
      "disk-state": "UpToDate",
      "client": false,
      "quorum": true,
      "size": 307152,
      "read": 0,
      "written": 0,
      "al-writes": 0,
      "bm-writes": 0,
      "upper-pending": 0,
      "lower-pending": 0
    } ],
  "connections": [
    {
      "peer-node-id": 2,
      "name": "salt-node3",
      "connection-state": "Connected",
      "congested": false,
      "peer-role": "Secondary",
      "ap-in-flight": 0,
      "rs-in-flight": 0,
      "peer_devices": [
        {
          "volume": 0,
          "replication-state": "Established",
          "peer-disk-state": "UpToDate",
          "peer-client": false,
          "resync-suspended": "no",
          "received": 0,
          "sent": 0,
          "out-of-sync": 0,
          "pending": 0,
          "unacked": 0,
          "has-sync-details": false,
          "has-online-verify-details": false,
          "percent-in-sync": 100.00
        } ]
    } ]
}
]

'''
        fake['stderr'] = ""
        fake['retcode'] = 0

        mock = MagicMock(return_value=fake)

        with patch.dict(drbd.__salt__, {'cmd.run_all': mock}):
            try:  # python2
                self.assertItemsEqual(drbd.setup_status(), ret)
            except AttributeError:  # python3
                self.assertCountEqual(drbd.setup_status(), ret)
            mock.assert_called_once_with(['drbdsetup', 'status', 'all', '--json'])

    def test_check_sync_status(self):
        '''
        Test if check_sync_status function work well
        Test data is get from drbd-9.0.16/drbd-utils-9.6.0
        '''

        # Test 1: Test all UpToDate
        fake = {}
        fake['stdout'] = '''
beijing role:Primary
  volume:0 disk:UpToDate
  volume:1 disk:UpToDate
  node2 role:Secondary
    volume:0 peer-disk:UpToDate
    volume:1 peer-disk:UpToDate
  node3 role:Secondary
    volume:0 peer-disk:UpToDate
    volume:1 peer-disk:UpToDate

'''
        fake['stderr'] = ""
        fake['retcode'] = 0

        mock = MagicMock(return_value=fake)

        with patch.dict(drbd.__salt__, {'cmd.run_all': mock}):
            self.assertEqual(drbd.check_sync_status('beijing'), True)
            mock.assert_called_with(['drbdadm', 'status', 'beijing'])

        # Test 2: Test local is not UpToDate
        fake = {}
        fake['stdout'] = '''
beijing role:Primary
  volume:0 disk:UpToDate
  volume:1 disk:Inconsistent
  node2 role:Secondary
    volume:0 peer-disk:UpToDate
    volume:1 peer-disk:UpToDate
  node3 role:Secondary
    volume:0 peer-disk:UpToDate
    volume:1 peer-disk:UpToDate

'''
        fake['stderr'] = ""
        fake['retcode'] = 0

        mock = MagicMock(return_value=fake)

        with patch.dict(drbd.__salt__, {'cmd.run_all': mock}):
            self.assertEqual(drbd.check_sync_status('beijing'), False)
            mock.assert_called_with(['drbdadm', 'status', 'beijing'])

        # Test 3: Test peer is not UpToDate
        fake = {}
        fake['stdout'] = '''
beijing role:Primary
  volume:0 disk:UpToDate
  volume:1 disk:UpToDate
  node2 role:Secondary
    volume:0 peer-disk:Inconsistent
    volume:1 peer-disk:UpToDate
  node3 role:Secondary
    volume:0 peer-disk:UpToDate
    volume:1 peer-disk:UpToDate

'''
        fake['stderr'] = ""
        fake['retcode'] = 0

        mock = MagicMock(return_value=fake)

        with patch.dict(drbd.__salt__, {'cmd.run_all': mock}):
            self.assertEqual(drbd.check_sync_status('beijing'), False)
            mock.assert_called_with(['drbdadm', 'status', 'beijing'])
