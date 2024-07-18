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

from cluster_host_count import OpenNebulaHostCount
import unittest.mock as mock

__all__ = [
    'OpenNebulaHostCountTestCount'
]


class OpenNebulaHostCountTestCase(OneBaseActionTestCase):
    __test__ = True
    action_cls = OpenNebulaHostCount

    @mock.patch("lib.action_base.BaseAction.pyone_session_create")
    def test_run_list(self, mock_session):
        action = self.get_action_instance(self._config_good)

        # Define test parameters
        mock_cluster1 = mock.Mock()
        mock_cluster2 = mock.Mock()
        mock_cluster1.NAME = "mockcluster1"
        mock_cluster2.NAME = "mockcluster2"
        mock_host1 = mock.Mock()
        mock_host2 = mock.Mock()
        mock_host3 = mock.Mock()
        mock_host4 = mock.Mock()
        mock_cluster1.HOSTS.ID = [mock_host1, mock_host2]
        mock_cluster2.HOSTS.ID = [mock_host3, mock_host4]

        test_clusters = [mock_cluster1, mock_cluster2]
        open_nebula = "default"
        expected_result = {'mockcluster1':
                            {'host_count': 2,
                             'host_list': [mock_host1, mock_host2]}, 
                           'mockcluster2': 
                            {'host_count': 2,
                             'host_list': [mock_host3, mock_host4]}}

        # Mock one object and run action
        mock_one = mock.Mock()
        mock_info = mock.Mock()
        mock_info.CLUSTER = test_clusters
        mock_one.clusterpool.info.return_value = mock_info
        mock_session.return_value = mock_one
        result = action.run(open_nebula)

        # Verify result and calls
        self.assertEqual(expected_result, result)
        mock_session.assert_called_with(open_nebula)
        mock_one.clusterpool.info.assert_called_with()

    @mock.patch("lib.action_base.BaseAction.pyone_session_create")
    def test_run_single(self, mock_session):
        action = self.get_action_instance(self._config_good)

        # Define test parameters
        mock_cluster1 = mock.Mock()
        mock_cluster2 = mock.Mock()
        mock_cluster1.NAME = "mockcluster1"
        mock_cluster2.NAME = "mockcluster2"
        mock_host1 = mock.Mock()
        mock_host2 = mock.Mock()
        mock_cluster1.HOSTS.ID = mock_host1
        mock_cluster2.HOSTS.ID = mock_host2

        test_clusters = [mock_cluster1, mock_cluster2]
        open_nebula = "default"
        expected_result = {'mockcluster1':
                            {'host_count': 1,
                             'host_list': [mock_host1]}, 
                           'mockcluster2': 
                            {'host_count': 1,
                             'host_list': [mock_host2]}}

        # Mock one object and run action
        mock_one = mock.Mock()
        mock_info = mock.Mock()
        mock_info.CLUSTER = test_clusters
        mock_one.clusterpool.info.return_value = mock_info
        mock_session.return_value = mock_one
        result = action.run(open_nebula)

        # Verify result and calls
        self.assertEqual(expected_result, result)
        mock_session.assert_called_with(open_nebula)
        mock_one.clusterpool.info.assert_called_with()

    @mock.patch("lib.action_base.BaseAction.pyone_session_create")
    def test_run_no_clusters(self, mock_session):
        action = self.get_action_instance(self._config_good)

        # Define test parameters
        test_clusters = []
        open_nebula = "default"

        # Mock one object and run action
        mock_info = mock.Mock()
        mock_info.CLUSTER = test_clusters
        mock_one = mock.Mock()
        mock_one.clusterpool.info.return_value = mock_info
        mock_session.return_value = mock_one
        action.run(open_nebula)
        mock_session.assert_called_with(open_nebula)
        mock_one.clusterpool.info.assert_called_with()