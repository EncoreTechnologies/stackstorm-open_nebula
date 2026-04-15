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
from vm_get_by_name import VmGetByName
import unittest.mock as mock

__all__ = [
    'VmGetByNameTestCase'
]


class VmGetByNameTestCase(OneBaseActionTestCase):
    __test__ = True
    action_cls = VmGetByName

    @mock.patch("lib.action_base.BaseAction.pyone_session_create")
    def test_run(self, mock_session):
        action = self.get_action_instance(self._config_good)

        # Define test parameters
        vm_name = 'test-vm.com'
        filter = 'VM.NAME=' + vm_name
        open_nebula = 'default'
        expected_result = ['VM1', 'VM2']

        # Mock one object and run action
        mock_vm1 = mock.Mock()
        mock_vm1.TEMPLATE = 'VM1'
        mock_vm2 = mock.Mock()
        mock_vm2.TEMPLATE = 'VM2'
        mock_vmpool = mock.Mock()
        mock_vmpool.VM = [mock_vm1, mock_vm2]
        mock_one = mock.Mock()
        mock_one.vmpool.infoextended.return_value = mock_vmpool
        mock_session.return_value = mock_one
        result = action.run(vm_name, open_nebula)

        # Verify result and calls
        self.assertEqual(expected_result, result)
        mock_session.assert_called_with(open_nebula)
        mock_one.vmpool.infoextended.assert_called_with(-2, -1, -1, -1, filter)

    @mock.patch("lib.action_base.BaseAction.pyone_session_create")
    def test_run_whitespace_fallback(self, mock_session):
        action = self.get_action_instance(self._config_good)

        # Define test parameters - VM has trailing whitespace in Open Nebula
        vm_name = 'test-vm.com'
        filter = 'VM.NAME=' + vm_name
        open_nebula = 'default'
        expected_result = ['VM1']

        # Mock filtered call returning empty, unfiltered call returning match
        mock_vm1 = mock.Mock()
        mock_vm1.NAME = 'test-vm.com '
        mock_vm1.TEMPLATE = 'VM1'

        mock_vmpool_empty = mock.Mock()
        mock_vmpool_empty.VM = []
        mock_vmpool_all = mock.Mock()
        mock_vmpool_all.VM = [mock_vm1]

        mock_one = mock.Mock()
        mock_one.vmpool.infoextended.side_effect = [mock_vmpool_empty, mock_vmpool_all]
        mock_session.return_value = mock_one
        result = action.run(vm_name, open_nebula)

        # Verify result and calls
        self.assertEqual(expected_result, result)
        mock_session.assert_called_with(open_nebula)
        mock_one.vmpool.infoextended.assert_any_call(-2, -1, -1, -1, filter)
        mock_one.vmpool.infoextended.assert_any_call(-2, -1, -1, -1)

    @mock.patch("lib.action_base.BaseAction.pyone_session_create")
    def test_run_whitespace_fallback_multiple_matches(self, mock_session):
        action = self.get_action_instance(self._config_good)

        # Define test parameters - multiple VMs match after stripping
        vm_name = 'test-vm.com'
        filter = 'VM.NAME=' + vm_name
        open_nebula = 'default'

        # Mock filtered call returning empty, unfiltered call returning multiple matches
        mock_vm1 = mock.Mock()
        mock_vm1.NAME = 'test-vm.com '
        mock_vm1.TEMPLATE = 'VM1'
        mock_vm2 = mock.Mock()
        mock_vm2.NAME = ' test-vm.com'
        mock_vm2.TEMPLATE = 'VM2'

        mock_vmpool_empty = mock.Mock()
        mock_vmpool_empty.VM = []
        mock_vmpool_all = mock.Mock()
        mock_vmpool_all.VM = [mock_vm1, mock_vm2]

        mock_one = mock.Mock()
        mock_one.vmpool.infoextended.side_effect = [mock_vmpool_empty, mock_vmpool_all]
        mock_session.return_value = mock_one
        with self.assertRaises(Exception):
            action.run(vm_name, open_nebula)

    @mock.patch("lib.action_base.BaseAction.pyone_session_create")
    def test_run_not_found(self, mock_session):
        action = self.get_action_instance(self._config_good)

        # Define test parameters - no VMs found by filter or fallback
        vm_name = 'nonexistent-vm.com'
        filter = 'VM.NAME=' + vm_name
        open_nebula = 'default'
        expected_result = []

        # Mock both calls returning empty
        mock_vmpool_empty = mock.Mock()
        mock_vmpool_empty.VM = []

        mock_one = mock.Mock()
        mock_one.vmpool.infoextended.return_value = mock_vmpool_empty
        mock_session.return_value = mock_one
        result = action.run(vm_name, open_nebula)

        # Verify result and calls
        self.assertEqual(expected_result, result)
        mock_session.assert_called_with(open_nebula)
