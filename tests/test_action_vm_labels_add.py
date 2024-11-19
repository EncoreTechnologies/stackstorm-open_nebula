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
from vm_labels_add import VmLabelsAdd
import unittest.mock as mock

__all__ = [
    'VmLabelsAddTestCase'
]


class VmLabelsAddTestCase(OneBaseActionTestCase):
    __test__ = True
    action_cls = VmLabelsAdd

    @mock.patch("lib.action_base.BaseAction.vm_labels_get")
    @mock.patch("lib.action_base.BaseAction.pyone_session_create")
    def test_run(self, mock_session, mock_labels_get):
        action = self.get_action_instance(self._config_good)

        # Define test parameters
        new_labels = ['LABEL1', 'LABEL2']
        vm_id = 0
        open_nebula = 'default'
        vm_labels = ['VMLABEL']
        test_attrs = {'LABELS': ','.join(vm_labels + new_labels)}
        expected_result = 'result'

        # Mock one object and run action
        mock_vm = mock.Mock()
        mock_one = mock.Mock()
        mock_one.vm.info.return_value = mock_vm
        mock_session.return_value = mock_one
        mock_labels_get.return_value = vm_labels
        mock_one.vm.update.return_value = expected_result
        result = action.run(new_labels, vm_id, open_nebula)

        # Verify result and calls
        self.assertEqual(expected_result, result)
        mock_session.assert_called_with(open_nebula)
        mock_one.vm.info.assert_called_with(vm_id)
        mock_labels_get.assert_called_with(mock_vm)
        mock_one.vm.update.assert_called_with(vm_id, test_attrs, 1)
