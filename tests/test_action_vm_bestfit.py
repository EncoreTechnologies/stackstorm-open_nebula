#!/usr/bin/env python
# Copyright 2024 Encore Technologies
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from one_base_action_test_case import OneBaseActionTestCase
import unittest
from unittest.mock import MagicMock, patch
from vm_bestfit import BestFit

__all__ = [
    'BestFitTestCase'
]


class BestFitTestCase(OneBaseActionTestCase):
    __test__ = True
    action_cls = BestFit

    @patch('vm_bestfit.BestFit.pyone_session_create')
    @patch('vm_bestfit.BestFit.get_host')
    @patch('vm_bestfit.BestFit.get_storage')
    def test_run(self, mock_get_storage, mock_get_host, mock_pyone_session_create):
        # Arrange
        cluster_name = 'test_cluster'
        datastore_filter_strategy = 'strategy'
        datastore_filter_regex_list = ['regex']
        disks = ['disk1']
        open_nebula = 'open_nebula'

        mock_get_host.return_value = MagicMock(NAME='host1', ID=1)
        mock_get_storage.return_value = MagicMock(NAME='datastore1', ID=1)

        # Mock the clusterpool and cluster objects
        cluster_mock = MagicMock()
        cluster_mock.CLUSTER = [MagicMock(NAME='test_cluster')]
        clusterpool_mock = MagicMock()
        clusterpool_mock.clusterpool.info.return_value = cluster_mock
        mock_pyone_session_create.return_value = clusterpool_mock

        # Act
        result = self.action.run(cluster_name, datastore_filter_strategy,
                                 datastore_filter_regex_list, disks, open_nebula)

        # Assert
        self.assertEqual(result, {
            'clusterName': 'test_cluster',
            'hostName': 'host1',
            'hostID': 1,
            'datastoreName': 'datastore1',
            'datastoreID': 1
        })

    @patch('vm_bestfit.BestFit.pyone_session_create')
    def test_run_no_cluster_found(self, mock_pyone_session_create):
        # Arrange
        cluster_name = 'non_existent_cluster'
        datastore_filter_strategy = 'strategy'
        datastore_filter_regex_list = ['regex']
        disks = ['disk1']
        open_nebula = 'open_nebula'

        # Mock the clusterpool and cluster objects
        cluster_mock = MagicMock()
        cluster_mock.CLUSTER = [MagicMock(NAME='test_cluster')]
        clusterpool_mock = MagicMock()
        clusterpool_mock.clusterpool.info.return_value = cluster_mock
        mock_pyone_session_create.return_value = clusterpool_mock

        # Act & Assert
        with self.assertRaises(Exception) as context:
            self.action.run(cluster_name, datastore_filter_strategy,
                            datastore_filter_regex_list, disks, open_nebula)

        self.assertTrue('No cluster found with the given name' in str(context.exception))

    def test_get_host(self):
        # Arrange
        cluster = MagicMock()
        cluster.HOSTS.ID = [1, 2, 3]

        host1 = MagicMock(STATE=2, VMS=MagicMock(ID=[1, 2]))
        host2 = MagicMock(STATE=2, VMS=MagicMock(ID=[1]))
        host3 = MagicMock(STATE=1, VMS=MagicMock(ID=[1, 2, 3]))

        self.action.one = MagicMock()
        self.action.one.host.info.side_effect = [host1, host2, host3]

        # Act
        result = self.action.get_host(cluster)

        # Assert
        self.assertEqual(result, host2)

    def test_get_host_no_available_hosts(self):
        # Arrange
        cluster = MagicMock()
        cluster.HOSTS.ID = [1, 2, 3]

        host1 = MagicMock(STATE=1, VMS=MagicMock(ID=[1, 2]))
        host2 = MagicMock(STATE=1, VMS=MagicMock(ID=[1]))
        host3 = MagicMock(STATE=1, VMS=MagicMock(ID=[1, 2, 3]))

        self.action.one = MagicMock()
        self.action.one.host.info.side_effect = [host1, host2, host3]

        # Act & Assert
        with self.assertRaises(Exception) as context:
            self.action.get_host(cluster)

        self.assertTrue('No available hosts found for cluster' in str(context.exception))

    def test_get_storage_from_disks(self):
        # Arrange
        cluster = MagicMock()
        cluster.DATASTORES.ID = [1, 2, 3]
        disks = [{'datastore': 'datastore2'}]

        datastore1 = MagicMock(NAME='datastore1', STATE=0)
        datastore2 = MagicMock(NAME='datastore2', STATE=0)
        datastore3 = MagicMock(NAME='datastore3', STATE=0)

        self.action.one = MagicMock()
        self.action.one.datastore.info.side_effect = [datastore1, datastore2, datastore3]

        # Act
        result = self.action.get_storage(cluster, 'strategy', ['regex'], disks)

        # Assert
        self.assertEqual(result, datastore2)

    def test_get_storage_most_free_space(self):
        # Arrange
        cluster = MagicMock()
        cluster.DATASTORES.ID = [1, 2, 3]
        disks = [{'datastore': 'automatic'}]

        datastore1 = MagicMock(NAME='datastore1', FREE_MB=1000, STATE=0)
        datastore2 = MagicMock(NAME='datastore2', FREE_MB=2000, STATE=0)
        datastore3 = MagicMock(NAME='datastore3', FREE_MB=500, STATE=0)

        self.action.one = MagicMock()
        self.action.one.datastore.info.side_effect = [datastore1, datastore2, datastore3]

        # Act
        result = self.action.get_storage(cluster, 'strategy', ['regex'], disks)

        # Assert
        self.assertEqual(result, datastore2)

    def test_get_storage_filtered_out(self):
        # Arrange
        cluster = MagicMock()
        cluster.DATASTORES.ID = [1, 2, 3]
        disks = [{'datastore': 'automatic'}]

        datastore1 = MagicMock(NAME='datastore1', FREE_MB=1000, STATE=0)
        datastore2 = MagicMock(NAME='datastore2', FREE_MB=2000, STATE=0)
        datastore3 = MagicMock(NAME='datastore3', FREE_MB=500, STATE=0)

        self.action.one = MagicMock()
        self.action.one.datastore.info.side_effect = [datastore1, datastore2, datastore3]

        # Mock filter_datastores to filter out datastore2
        self.action.filter_datastores = MagicMock(side_effect=lambda name, strategy,
                                                  regex: name != 'datastore2')

        # Act
        result = self.action.get_storage(cluster, 'strategy', ['regex'], disks)

        # Assert
        self.assertEqual(result, datastore1)

    def test_get_storage_no_available_datastores(self):
        # Arrange
        cluster = MagicMock()
        cluster.DATASTORES.ID = [1, 2, 3]
        disks = [{'datastore': 'automatic'}]

        datastore1 = MagicMock(NAME='datastore1', FREE_MB=1000, STATE=1)
        datastore2 = MagicMock(NAME='datastore2', FREE_MB=2000, STATE=1)
        datastore3 = MagicMock(NAME='datastore3', FREE_MB=500, STATE=1)

        self.action.one = MagicMock()
        self.action.one.datastore.info.side_effect = [datastore1, datastore2, datastore3]

        # Act
        result = self.action.get_storage(cluster, 'strategy', ['regex'], disks)

        # Assert
        self.assertIsNone(result)

    def test_filter_datastores_no_regex(self):
        # Arrange
        ds_name = 'datastore1'
        datastore_filter_strategy = 'exclude_matches'
        datastore_filter_regex_list = None

        # Act
        result = self.action.filter_datastores(ds_name, datastore_filter_strategy,
                                               datastore_filter_regex_list)

        # Assert
        self.assertTrue(result)

    def test_filter_datastores_exclude_matches(self):
        # Arrange
        ds_name = 'datastore1'
        datastore_filter_strategy = 'exclude_matches'
        datastore_filter_regex_list = ['datastore1', 'datastore2']

        # Act
        result = self.action.filter_datastores(ds_name, datastore_filter_strategy,
                                               datastore_filter_regex_list)

        # Assert
        self.assertFalse(result)

    def test_filter_datastores_include_matches(self):
        # Arrange
        ds_name = 'datastore1'
        datastore_filter_strategy = 'include_matches'
        datastore_filter_regex_list = ['datastore1', 'datastore2']

        # Act
        result = self.action.filter_datastores(ds_name, datastore_filter_strategy,
                                               datastore_filter_regex_list)

        # Assert
        self.assertTrue(result)

    def test_filter_datastores_no_match(self):
        # Arrange
        ds_name = 'datastore3'
        datastore_filter_strategy = 'exclude_matches'
        datastore_filter_regex_list = ['datastore1', 'datastore2']

        # Act
        result = self.action.filter_datastores(ds_name, datastore_filter_strategy,
                                               datastore_filter_regex_list)

        # Assert
        self.assertTrue(result)

    def test_filter_datastores_include_no_match(self):
        # Arrange
        ds_name = 'datastore3'
        datastore_filter_strategy = 'include_matches'
        datastore_filter_regex_list = ['datastore1', 'datastore2']

        # Act
        result = self.action.filter_datastores(ds_name, datastore_filter_strategy,
                                               datastore_filter_regex_list)

        # Assert
        self.assertFalse(result)

    def test_get_host_with_exclude_vm(self):
        # Arrange
        cluster = MagicMock()
        cluster.HOSTS.ID = [1, 2, 3]

        # Host1 has VM 100 (will be excluded), Host2 is the expected pick
        host1 = MagicMock(STATE=2, VMS=MagicMock(ID=['100', '101']))
        host2 = MagicMock(STATE=2, VMS=MagicMock(ID=['200', '201', '202']))
        host3 = MagicMock(STATE=2, VMS=MagicMock(ID=['300']))

        self.action.one = MagicMock()
        self.action.one.host.info.side_effect = [host1, host2, host3]

        # Act - exclude VM 100, so host1 is skipped. host3 has fewer VMs than host2
        result = self.action.get_host(cluster, exclude_vm_ids=[100])

        # Assert
        self.assertEqual(result, host3)

    def test_get_host_exclude_vm_single_vm_on_host(self):
        # Arrange - host with a single VM returns a string, not a list
        cluster = MagicMock()
        cluster.HOSTS.ID = [1, 2]

        host1 = MagicMock(STATE=2, VMS=MagicMock(ID='100'))
        host2 = MagicMock(STATE=2, VMS=MagicMock(ID=['200', '201']))

        self.action.one = MagicMock()
        self.action.one.host.info.side_effect = [host1, host2]

        # Act - exclude VM 100, host1 has single VM as string
        result = self.action.get_host(cluster, exclude_vm_ids=[100])

        # Assert
        self.assertEqual(result, host2)

    def test_get_host_all_excluded(self):
        # Arrange
        cluster = MagicMock()
        cluster.NAME = 'test_cluster'
        cluster.HOSTS.ID = [1, 2]

        host1 = MagicMock(STATE=2, VMS=MagicMock(ID=['100']))
        host2 = MagicMock(STATE=2, VMS=MagicMock(ID=['200']))

        self.action.one = MagicMock()
        self.action.one.host.info.side_effect = [host1, host2]

        # Act & Assert - both hosts are excluded
        with self.assertRaises(Exception) as context:
            self.action.get_host(cluster, exclude_vm_ids=[100, 200])

        self.assertTrue('No available hosts found for cluster' in str(context.exception))

    def test_get_host_cpu_strategy(self):
        # Arrange
        cluster = MagicMock()
        cluster.HOSTS.ID = [1, 2, 3]

        host1 = MagicMock(STATE=2, VMS=MagicMock(ID=['100', '101']),
                          HOST_SHARE=MagicMock(CPU_USAGE='2400', MAX_CPU='4800'))
        host2 = MagicMock(STATE=2, VMS=MagicMock(ID=['200']),
                          HOST_SHARE=MagicMock(CPU_USAGE='480', MAX_CPU='4800'))
        host3 = MagicMock(STATE=2, VMS=MagicMock(ID=['300', '301', '302']),
                          HOST_SHARE=MagicMock(CPU_USAGE='3600', MAX_CPU='4800'))

        self.action.one = MagicMock()
        self.action.one.host.info.side_effect = [host1, host2, host3]

        # Act - host2 has lowest CPU usage ratio (480/4800 = 10%)
        result = self.action.get_host(cluster, host_strategy='cpu')

        # Assert
        self.assertEqual(result, host2)

    def test_get_host_memory_strategy(self):
        # Arrange
        cluster = MagicMock()
        cluster.HOSTS.ID = [1, 2, 3]

        host1 = MagicMock(STATE=2, VMS=MagicMock(ID=['100']),
                          HOST_SHARE=MagicMock(MEM_USAGE='190000000', MAX_MEM='256000000'))
        host2 = MagicMock(STATE=2, VMS=MagicMock(ID=['200', '201']),
                          HOST_SHARE=MagicMock(MEM_USAGE='50000000', MAX_MEM='256000000'))
        host3 = MagicMock(STATE=2, VMS=MagicMock(ID=['300']),
                          HOST_SHARE=MagicMock(MEM_USAGE='200000000', MAX_MEM='256000000'))

        self.action.one = MagicMock()
        self.action.one.host.info.side_effect = [host1, host2, host3]

        # Act - host2 has lowest memory usage ratio
        result = self.action.get_host(cluster, host_strategy='memory')

        # Assert
        self.assertEqual(result, host2)

    def test_get_host_exclude_with_strategy(self):
        # Arrange
        cluster = MagicMock()
        cluster.HOSTS.ID = [1, 2, 3]

        # Host2 has lowest CPU but contains excluded VM
        host1 = MagicMock(STATE=2, VMS=MagicMock(ID=['100']),
                          HOST_SHARE=MagicMock(CPU_USAGE='2400', MAX_CPU='4800'))
        host2 = MagicMock(STATE=2, VMS=MagicMock(ID=['200']),
                          HOST_SHARE=MagicMock(CPU_USAGE='480', MAX_CPU='4800'))
        host3 = MagicMock(STATE=2, VMS=MagicMock(ID=['300']),
                          HOST_SHARE=MagicMock(CPU_USAGE='1200', MAX_CPU='4800'))

        self.action.one = MagicMock()
        self.action.one.host.info.side_effect = [host1, host2, host3]

        # Act - exclude VM 200, so host2 is skipped. host3 is next best CPU
        result = self.action.get_host(cluster, exclude_vm_ids=[200], host_strategy='cpu')

        # Assert
        self.assertEqual(result, host3)

    @patch('vm_bestfit.BestFit.pyone_session_create')
    @patch('vm_bestfit.BestFit.get_host')
    @patch('vm_bestfit.BestFit.get_storage')
    def test_run_with_new_params(self, mock_get_storage, mock_get_host,
                                  mock_pyone_session_create):
        # Arrange
        cluster_name = 'test_cluster'
        datastore_filter_strategy = 'strategy'
        datastore_filter_regex_list = ['regex']
        disks = ['disk1']
        exclude_vm_ids = [100]
        host_strategy = 'cpu'
        open_nebula = 'open_nebula'

        mock_get_host.return_value = MagicMock(NAME='host1', ID=1)
        mock_get_storage.return_value = MagicMock(NAME='datastore1', ID=1)

        cluster_mock = MagicMock()
        cluster_mock.CLUSTER = [MagicMock(NAME='test_cluster')]
        clusterpool_mock = MagicMock()
        clusterpool_mock.clusterpool.info.return_value = cluster_mock
        mock_pyone_session_create.return_value = clusterpool_mock

        # Act
        result = self.action.run(cluster_name, datastore_filter_strategy,
                                 datastore_filter_regex_list, disks,
                                 exclude_vm_ids, host_strategy, open_nebula)

        # Assert - verify new params are passed through to get_host
        mock_get_host.assert_called_once()
        call_args = mock_get_host.call_args
        self.assertEqual(call_args[0][1], exclude_vm_ids)
        self.assertEqual(call_args[0][2], host_strategy)

    @patch('vm_bestfit.BestFit.pyone_session_create')
    @patch('vm_bestfit.BestFit.get_host')
    @patch('vm_bestfit.BestFit.get_storage')
    def test_run_without_new_params(self, mock_get_storage, mock_get_host,
                                     mock_pyone_session_create):
        # Arrange - call with only original params to verify backward compatibility
        cluster_name = 'test_cluster'
        datastore_filter_strategy = 'strategy'
        datastore_filter_regex_list = ['regex']
        disks = ['disk1']
        open_nebula = 'open_nebula'

        mock_get_host.return_value = MagicMock(NAME='host1', ID=1)
        mock_get_storage.return_value = MagicMock(NAME='datastore1', ID=1)

        cluster_mock = MagicMock()
        cluster_mock.CLUSTER = [MagicMock(NAME='test_cluster')]
        clusterpool_mock = MagicMock()
        clusterpool_mock.clusterpool.info.return_value = cluster_mock
        mock_pyone_session_create.return_value = clusterpool_mock

        # Act - no exclude_vm_ids or host_strategy passed
        result = self.action.run(cluster_name, datastore_filter_strategy,
                                 datastore_filter_regex_list, disks,
                                 open_nebula=open_nebula)

        # Assert
        self.assertEqual(result['hostName'], 'host1')
        mock_get_host.assert_called_once()
        call_args = mock_get_host.call_args
        self.assertIsNone(call_args[0][1])  # exclude_vm_ids defaults to None
        self.assertEqual(call_args[0][2], 'vm_count')  # host_strategy defaults to vm_count


if __name__ == '__main__':
    unittest.main()
