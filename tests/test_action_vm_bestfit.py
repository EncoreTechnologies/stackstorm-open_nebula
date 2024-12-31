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
import unittest.mock as mock
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
        result = self.action.run(cluster_name, datastore_filter_strategy, datastore_filter_regex_list, disks, open_nebula)

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
            self.action.run(cluster_name, datastore_filter_strategy, datastore_filter_regex_list, disks, open_nebula)
        
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
        self.action.filter_datastores = MagicMock(side_effect=lambda name, strategy, regex: name != 'datastore2')

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
        result = self.action.filter_datastores(ds_name, datastore_filter_strategy, datastore_filter_regex_list)

        # Assert
        self.assertTrue(result)

    def test_filter_datastores_exclude_matches(self):
        # Arrange
        ds_name = 'datastore1'
        datastore_filter_strategy = 'exclude_matches'
        datastore_filter_regex_list = ['datastore1', 'datastore2']

        # Act
        result = self.action.filter_datastores(ds_name, datastore_filter_strategy, datastore_filter_regex_list)

        # Assert
        self.assertFalse(result)

    def test_filter_datastores_include_matches(self):
        # Arrange
        ds_name = 'datastore1'
        datastore_filter_strategy = 'include_matches'
        datastore_filter_regex_list = ['datastore1', 'datastore2']

        # Act
        result = self.action.filter_datastores(ds_name, datastore_filter_strategy, datastore_filter_regex_list)

        # Assert
        self.assertTrue(result)

    def test_filter_datastores_no_match(self):
        # Arrange
        ds_name = 'datastore3'
        datastore_filter_strategy = 'exclude_matches'
        datastore_filter_regex_list = ['datastore1', 'datastore2']

        # Act
        result = self.action.filter_datastores(ds_name, datastore_filter_strategy, datastore_filter_regex_list)

        # Assert
        self.assertTrue(result)

    def test_filter_datastores_include_no_match(self):
        # Arrange
        ds_name = 'datastore3'
        datastore_filter_strategy = 'include_matches'
        datastore_filter_regex_list = ['datastore1', 'datastore2']

        # Act
        result = self.action.filter_datastores(ds_name, datastore_filter_strategy, datastore_filter_regex_list)

        # Assert
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()