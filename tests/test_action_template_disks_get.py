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
from template_disks_get import TemplateDisksGet
import unittest.mock as mock

__all__ = [
    'TemplateDisksGetTestCase'
]


class TemplateDisksGetTestCase(OneBaseActionTestCase):
    __test__ = True
    action_cls = TemplateDisksGet

    @mock.patch("lib.action_base.BaseAction.template_disks_get")
    @mock.patch("lib.action_base.BaseAction.pyone_session_create")
    def test_run(self, mock_session, mock_disks_get):
        action = self.get_action_instance(self._config_good)

        # Define test parameters
        template_id = 0
        open_nebula = 'default'
        temp_info = 'temp'
        expected_result = 'result'

        # Mock one object and run action
        mock_one = mock.Mock()
        mock_one.template.info.return_value = temp_info
        mock_session.return_value = mock_one
        mock_disks_get.return_value = expected_result
        result = action.run(template_id, open_nebula)

        # Verify result and calls
        self.assertEqual(expected_result, result)
        mock_session.assert_called_with(open_nebula)
        mock_one.template.info.assert_called_with(template_id)
        mock_disks_get.assert_called_with(temp_info)
