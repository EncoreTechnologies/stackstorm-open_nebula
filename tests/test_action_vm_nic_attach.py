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
from vm_nic_attach import VmNicAttach

__all__ = [
    'VmNicAttachTestCase'
]


class VmNicAttachTestCase(OneBaseActionTestCase):
    __test__ = True
    action_cls = VmNicAttach

    @patch('vm_nic_attach.VmNicAttach.pyone_session_create')
    @patch('vm_nic_attach.VmNicAttach.wait_for_vm')
    def test_run_success(self, mock_wait_for_vm, mock_pyone_session_create):
        # Arrange
        attach_timeout = 10
        gateway = '192.168.1.1'
        ip_addr = '192.168.1.100'
        method = 'static'
        network_id = 1
        vm_id = 1
        open_nebula = 'open_nebula'

        mock_pyone_session_create.return_value = MagicMock()
        mock_wait_for_vm.return_value = 3

        # Act
        result = self.action.run(attach_timeout, gateway, ip_addr, method, network_id, vm_id, open_nebula)

        # Assert
        self.assertEqual(result, (True, "Succesfully attached NIC to VM {}".format(vm_id)))
        mock_pyone_session_create.assert_called_once_with(open_nebula)
        mock_pyone_session_create.return_value.vm.attachnic.assert_called_once_with(
            vm_id, "NIC=[IP={}, NETWORK_ID={}, GATEWAY={}, METHOD={}]".format(ip_addr, network_id, gateway, method)
        )
        mock_wait_for_vm.assert_called_once_with(mock_pyone_session_create.return_value, vm_id, attach_timeout)

    @patch('vm_nic_attach.VmNicAttach.pyone_session_create')
    @patch('vm_nic_attach.VmNicAttach.wait_for_vm')
    def test_run_timeout(self, mock_wait_for_vm, mock_pyone_session_create):
        # Arrange
        attach_timeout = 10
        gateway = '192.168.1.1'
        ip_addr = '192.168.1.100'
        method = 'static'
        network_id = 1
        vm_id = 1
        open_nebula = 'open_nebula'

        mock_pyone_session_create.return_value = MagicMock()
        mock_wait_for_vm.return_value = 1

        # Act
        result = self.action.run(attach_timeout, gateway, ip_addr, method, network_id, vm_id, open_nebula)

        # Assert
        self.assertEqual(result, (False, "Timed out waiting for VM {} to enter running state after attaching NIC".format(vm_id)))
        mock_pyone_session_create.assert_called_once_with(open_nebula)
        mock_pyone_session_create.return_value.vm.attachnic.assert_called_once_with(
            vm_id, "NIC=[IP={}, NETWORK_ID={}, GATEWAY={}, METHOD={}]".format(ip_addr, network_id, gateway, method)
        )
        mock_wait_for_vm.assert_called_once_with(mock_pyone_session_create.return_value, vm_id, attach_timeout)

if __name__ == '__main__':
    unittest.main()