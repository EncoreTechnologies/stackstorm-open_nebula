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

from vms_attribute_get import VmsAttributeGet
import unittest.mock as mock

__all__ = [
    'VmsAttributeGetTestCase'
]


class VmsAttributeGetTestCase(OneBaseActionTestCase):
    __test__ = True
    action_cls = VmsAttributeGet

    @mock.patch("lib.action_base.BaseAction.pyone_session_create")
    def test_run_attribute_found(self, mock_session):
        action = self.get_action_instance(self._config_good)

        # Define test parameters
        mock_vm1 = mock.Mock()
        mock_vm2 = mock.Mock()
        mock_vm1.NAME = "vm1"
        mock_vm2.NAME = "vm2"
        mock_vm1.USER_TEMPLATE = {"BACKUPS": "true"}
        mock_vm2.USER_TEMPLATE = {"BACKUPS": "false"}

        test_vms = [mock_vm1, mock_vm2]
        vm_ids = [1, 2]
        attribute_name = ["USER_TEMPLATE", "BACKUPS"]
        open_nebula = "default"
        expected_result = {
            'vms_with_attribute': [
                {'vm_id': 1, 'vm_name': "vm1", 'BACKUPS': "true"},
                {'vm_id': 2, 'vm_name': "vm2", 'BACKUPS': "false"}
            ],
            'attribute_not_set': []
        }

        # Mock one object and run action
        mock_one = mock.Mock()
        mock_one.vm.info.side_effect = test_vms
        mock_session.return_value = mock_one
        result = action.run(attribute_name, vm_ids, open_nebula)

        # Verify result and calls
        self.assertEqual(expected_result, result)
        mock_session.assert_called_with(open_nebula)
        mock_one.vm.info.assert_any_call(1)
        mock_one.vm.info.assert_any_call(2)

    @mock.patch("lib.action_base.BaseAction.pyone_session_create")
    def test_run_attribute_not_found(self, mock_session):
        action = self.get_action_instance(self._config_good)

        # Define test parameters
        mock_vm1 = mock.Mock()
        mock_vm2 = mock.Mock()
        mock_vm1.NAME = "vm1"
        mock_vm2.NAME = "vm2"
        mock_vm1.USER_TEMPLATE = {"DESCRIPTION": "desc"}
        mock_vm2.USER_TEMPLATE = {"DESCRIPTION": "desc"}

        test_vms = [mock_vm1, mock_vm2]
        vm_ids = [1, 2]
        attribute_name = ["USER_TEMPLATE", "BACKUPS"]
        open_nebula = "default"
        expected_result = {
            'vms_with_attribute': [],
            'attribute_not_set': [
                {'vm_id': 1, 'vm_name': "vm1"},
                {'vm_id': 2, 'vm_name': "vm2"}
            ]
        }

        # Mock one object and run action
        mock_one = mock.Mock()
        mock_one.vm.info.side_effect = test_vms
        mock_session.return_value = mock_one
        result = action.run(attribute_name, vm_ids, open_nebula)

        # Verify result and calls
        self.assertEqual(expected_result, result)
        mock_session.assert_called_with(open_nebula)
        mock_one.vm.info.assert_any_call(1)
        mock_one.vm.info.assert_any_call(2)

    @mock.patch("lib.action_base.BaseAction.pyone_session_create")
    def test_run_mixed_attributes(self, mock_session):
        action = self.get_action_instance(self._config_good)

        # Define test parameters
        mock_vm1 = mock.Mock()
        mock_vm2 = mock.Mock()
        mock_vm3 = mock.Mock()
        mock_vm1.NAME = "vm1"
        mock_vm2.NAME = "vm2"
        mock_vm3.NAME = "vm3"
        mock_vm1.USER_TEMPLATE = {"BACKUPS": "true"}
        mock_vm2.USER_TEMPLATE = {"DESCRIPTION": "desc"}
        mock_vm3.USER_TEMPLATE = {"BACKUPS": "false"}

        test_vms = [mock_vm1, mock_vm2, mock_vm3]
        vm_ids = [1, 2, 3]
        attribute_name = ["USER_TEMPLATE", "BACKUPS"]
        open_nebula = "default"
        expected_result = {
            'vms_with_attribute': [
                {'vm_id': 1, 'vm_name': "vm1", 'BACKUPS': "true"},
                {'vm_id': 3, 'vm_name': "vm3", 'BACKUPS': "false"}
            ],
            'attribute_not_set': [
                {'vm_id': 2, 'vm_name': "vm2"}
            ]
        }

        # Mock one object and run action
        mock_one = mock.Mock()
        mock_one.vm.info.side_effect = test_vms
        mock_session.return_value = mock_one
        result = action.run(attribute_name, vm_ids, open_nebula)

        # Verify result and calls
        self.assertEqual(expected_result, result)
        mock_session.assert_called_with(open_nebula)
        mock_one.vm.info.assert_any_call(1)
        mock_one.vm.info.assert_any_call(2)
        mock_one.vm.info.assert_any_call(3)
