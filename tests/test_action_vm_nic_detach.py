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
from vm_nic_detach import VmNicDetach

__all__ = [
    'VmNicDetachTestCase'
]


class VmNicDetachTestCase(OneBaseActionTestCase):
    __test__ = True
    action_cls = VmNicDetach

    @patch('vm_nic_detach.VmNicDetach.pyone_session_create')
    @patch('vm_nic_detach.VmNicDetach.wait_for_vm')
    def test_run_success(self, mock_wait_for_vm, mock_pyone_session_create):
        # Arrange
        detach_timeout = 10
        nic_id = 1
        vm_id = 1
        open_nebula = 'open_nebula'

        mock_pyone_session_create.return_value = MagicMock()
        mock_wait_for_vm.return_value = 3

        # Act
        result = self.action.run(detach_timeout, nic_id, vm_id, open_nebula)

        # Assert
        self.assertEqual(result, (True, "Succesfully detached NIC from VM {}".format(vm_id)))
        mock_pyone_session_create.assert_called_once_with(open_nebula)
        mock_pyone_session_create.return_value.vm.detachnic.assert_called_once_with(vm_id, nic_id)
        mock_wait_for_vm.assert_called_once_with(mock_pyone_session_create.return_value, vm_id,
                                                 detach_timeout)

    @patch('vm_nic_detach.VmNicDetach.pyone_session_create')
    @patch('vm_nic_detach.VmNicDetach.wait_for_vm')
    def test_run_timeout(self, mock_wait_for_vm, mock_pyone_session_create):
        # Arrange
        detach_timeout = 10
        nic_id = 1
        vm_id = 1
        open_nebula = 'open_nebula'

        mock_pyone_session_create.return_value = MagicMock()
        mock_wait_for_vm.return_value = 1

        # Act
        result = self.action.run(detach_timeout, nic_id, vm_id, open_nebula)

        # Assert
        self.assertEqual(result, (False, "Timed out waiting for VM {} to enter running state "
                                  "after detaching NIC".format(vm_id)))
        mock_pyone_session_create.assert_called_once_with(open_nebula)
        mock_pyone_session_create.return_value.vm.detachnic.assert_called_once_with(vm_id, nic_id)
        mock_wait_for_vm.assert_called_once_with(mock_pyone_session_create.return_value, vm_id,
                                                 detach_timeout)


if __name__ == '__main__':
    unittest.main()
