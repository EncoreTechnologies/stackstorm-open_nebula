#!/usr/bin/env python
# Copyright 2026 Encore Technologies
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
from vm_host_get import VmHostGet

__all__ = [
    'VmHostGetTestCase'
]


class VmHostGetTestCase(OneBaseActionTestCase):
    __test__ = True
    action_cls = VmHostGet

    def _mock_host_pool(self, mock_pyone_session_create, hosts):
        host_pool = MagicMock()
        host_pool.HOST = hosts
        mock_one = MagicMock()
        mock_one.hostpool.info.return_value = host_pool
        mock_pyone_session_create.return_value = mock_one

    @patch('vm_host_get.VmHostGet.pyone_session_create')
    def test_run_found(self, mock_pyone_session_create):
        # Arrange
        host1 = MagicMock(NAME='host1.example.com', VMS=MagicMock(ID=['2100', '2101']))
        host2 = MagicMock(NAME='host2.example.com', VMS=MagicMock(ID=['2195', '2200']))
        host3 = MagicMock(NAME='host3.example.com', VMS=MagicMock(ID=['2300']))
        self._mock_host_pool(mock_pyone_session_create, [host1, host2, host3])

        # Act
        result = self.action.run(2195, 'open_nebula')

        # Assert
        self.assertEqual(result, 'host2.example.com')

    @patch('vm_host_get.VmHostGet.pyone_session_create')
    def test_run_not_found(self, mock_pyone_session_create):
        # Arrange
        host1 = MagicMock(NAME='host1.example.com', VMS=MagicMock(ID=['2100']))
        host2 = MagicMock(NAME='host2.example.com', VMS=MagicMock(ID=['2200']))
        self._mock_host_pool(mock_pyone_session_create, [host1, host2])

        # Act
        result = self.action.run(9999, 'open_nebula')

        # Assert
        self.assertIsNone(result)

    @patch('vm_host_get.VmHostGet.pyone_session_create')
    def test_run_single_vm_on_host(self, mock_pyone_session_create):
        # Arrange - host with a single VM returns a non-list value
        host1 = MagicMock(NAME='host1.example.com', VMS=MagicMock(ID=2195))
        self._mock_host_pool(mock_pyone_session_create, [host1])

        # Act
        result = self.action.run(2195, 'open_nebula')

        # Assert
        self.assertEqual(result, 'host1.example.com')

    @patch('vm_host_get.VmHostGet.pyone_session_create')
    def test_run_host_no_vms(self, mock_pyone_session_create):
        # Arrange - host with no VMs (VMS is None, so .ID raises AttributeError)
        host_no_vms = MagicMock(NAME='empty.example.com')
        host_no_vms.VMS = None
        host_with_vm = MagicMock(NAME='host1.example.com', VMS=MagicMock(ID=['2195']))
        self._mock_host_pool(mock_pyone_session_create, [host_no_vms, host_with_vm])

        # Act
        result = self.action.run(2195, 'open_nebula')

        # Assert
        self.assertEqual(result, 'host1.example.com')

    @patch('vm_host_get.VmHostGet.pyone_session_create')
    def test_run_integer_vm_ids(self, mock_pyone_session_create):
        # Arrange - pyone may return VM IDs as integers instead of strings
        host1 = MagicMock(NAME='host1.example.com', VMS=MagicMock(ID=[2195, 2200]))
        self._mock_host_pool(mock_pyone_session_create, [host1])

        # Act
        result = self.action.run(2195, 'open_nebula')

        # Assert
        self.assertEqual(result, 'host1.example.com')

    @patch('vm_host_get.VmHostGet.pyone_session_create')
    def test_run_empty_host_pool(self, mock_pyone_session_create):
        # Arrange
        self._mock_host_pool(mock_pyone_session_create, [])

        # Act
        result = self.action.run(2195, 'open_nebula')

        # Assert
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
