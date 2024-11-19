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
from vm_resize import VmResize
import unittest.mock as mock

__all__ = [
    'VmResizeTestCase'
]


class VmResizeTestCase(OneBaseActionTestCase):
    __test__ = True
    action_cls = VmResize

    def test_check_template_sizes_cpu_error(self):
        action = self.get_action_instance(self._config_good)

        # Define test variables
        cpu_num = 2
        mem_mb = 4096
        vcpu_num = 4

        # Mock one object and run action
        mock_temp = mock.Mock()
        mock_temp.TEMPLATE = {'CPU': 4, 'MEMORY': 4096, 'VCPU': 4}

        # Verify result and calls
        with self.assertRaises(ValueError):
            action.check_template_sizes(cpu_num, mem_mb, vcpu_num, mock_temp)

    def test_check_template_sizes_mem_error(self):
        action = self.get_action_instance(self._config_good)

        # Define test variables
        cpu_num = 4
        mem_mb = 2048
        vcpu_num = 4

        # Mock one object and run action
        mock_temp = mock.Mock()
        mock_temp.TEMPLATE = {'CPU': 4, 'MEMORY': 4096, 'VCPU': 4}

        # Verify result and calls
        with self.assertRaises(ValueError):
            action.check_template_sizes(cpu_num, mem_mb, vcpu_num, mock_temp)

    def test_check_template_sizes_vcpu_error(self):
        action = self.get_action_instance(self._config_good)

        # Define test variables
        cpu_num = 4
        mem_mb = 4096
        vcpu_num = 2

        # Mock one object and run action
        mock_temp = mock.Mock()
        mock_temp.TEMPLATE = {'CPU': 4, 'MEMORY': 4096, 'VCPU': 4}

        # Verify result and calls
        with self.assertRaises(ValueError):
            action.check_template_sizes(cpu_num, mem_mb, vcpu_num, mock_temp)

    @mock.patch("vm_resize.VmResize.check_template_sizes")
    @mock.patch("lib.action_base.BaseAction.pyone_session_create")
    def test_run(self, mock_session, mock_check_sizes):
        action = self.get_action_instance(self._config_good)

        # Define test variables
        cpu_num = 4
        mem_mb = 4096
        vcpu_num = 4
        vm_id = 1
        temp_id = 6
        open_nebula = 'default'
        expected_result = 'result'

        template_string = """<TEMPLATE>
            <CPU>{}</CPU>
            <MEMORY>{}</MEMORY>
            <VCPU>{}</VCPU>
        </TEMPLATE>""".format(cpu_num, mem_mb, vcpu_num)

        # Mock one object and run action
        mock_vm = mock.Mock()
        mock_vm.TEMPLATE = {'TEMPLATE_ID': temp_id}
        mock_temp = mock.Mock()
        mock_one = mock.Mock()
        mock_one.vm.info.return_value = mock_vm
        mock_one.template.info.return_value = mock_temp
        mock_one.vm.resize.return_value = expected_result
        mock_session.return_value = mock_one
        result = action.run(cpu_num, mem_mb, vcpu_num, vm_id, open_nebula)

        # Verify result and calls
        self.assertEqual(expected_result, result)
        mock_session.assert_called_with(open_nebula)
        mock_one.vm.info.assert_called_with(vm_id)
        mock_one.template.info.assert_called_with(temp_id)
        mock_check_sizes.assert_called_with(cpu_num, mem_mb, vcpu_num, mock_temp)
        mock_one.vm.resize.assert_called_with(vm_id, template_string, True)
