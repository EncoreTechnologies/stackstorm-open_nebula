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
from vm_snapshots_get import VmSnapshotGet
import unittest.mock as mock

__all__ = [
    'VmSnapshotGetTestCase'
]


class VmSnapshotGetTestCase(OneBaseActionTestCase):
    __test__ = True
    action_cls = VmSnapshotGet

    @mock.patch("lib.action_base.BaseAction.pyone_session_create")
    def test_run(self, mock_session):
        action = self.get_action_instance(self._config_good)

        # Define test variables
        vm_id = 1
        open_nebula = 'default'
        expected_result = ['snap1', 'snap2']

        # Mock one object and run action
        mock_vm = mock.Mock()
        mock_vm.TEMPLATE = {'SNAPSHOT': expected_result}
        mock_one = mock.Mock()
        mock_one.vm.info.return_value = mock_vm
        mock_session.return_value = mock_one
        result = action.run(vm_id, open_nebula)

        # Verify result and calls
        self.assertEqual(expected_result, result)
        mock_session.assert_called_with(open_nebula)
        mock_one.vm.info.assert_called_with(vm_id)
