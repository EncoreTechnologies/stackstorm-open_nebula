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

from template_get_by_name import TemplateGetByName
import unittest.mock as mock

__all__ = [
    'TemplateGetByNameTestCase'
]


class TemplateGetByNameTestCase(OneBaseActionTestCase):
    __test__ = True
    action_cls = TemplateGetByName

    @mock.patch("lib.action_base.BaseAction.pyone_session_create")
    def test_run(self, mock_session):
        action = self.get_action_instance(self._config_good)

        # Define test parameters
        template_name = "temp2"
        mock_temp1 = mock.Mock()
        mock_temp2 = mock.Mock()
        mock_temp1.NAME = "temp1"
        mock_temp1.ID = 78
        mock_temp1.TEMPLATE = {"KEY": "VALUE"}
        mock_temp2.NAME = "temp2"
        mock_temp2.ID = 79
        mock_temp2.TEMPLATE = {"KEY": "VALUE"}

        test_temps = [mock_temp1, mock_temp2]
        open_nebula = "default"
        expected_result = {
            "KEY": "VALUE",
            "ID": 79,
            "NAME": "temp2"
        }

        # Mock one object and run action
        mock_info = mock.Mock()
        mock_info.VMTEMPLATE = test_temps
        mock_one = mock.Mock()
        mock_one.templatepool.info.return_value = mock_info
        mock_session.return_value = mock_one
        result = action.run(template_name, open_nebula)

        # Verify result and calls
        self.assertEqual(expected_result, result)
        mock_session.assert_called_with(open_nebula)
        mock_one.templatepool.info.assert_called_with(-2, -1, -1, -1)

    @mock.patch("lib.action_base.BaseAction.pyone_session_create")
    def test_run_not_found(self, mock_session):
        action = self.get_action_instance(self._config_good)

        # Define test parameters
        template_name = "temp3"
        mock_temp1 = mock.Mock()
        mock_temp2 = mock.Mock()
        mock_temp1.NAME = "temp1"
        mock_temp1.ID = 78
        mock_temp1.TEMPLATE = {"KEY": "VALUE"}
        mock_temp2.NAME = "temp2"
        mock_temp2.ID = 79
        mock_temp2.TEMPLATE = {"KEY": "VALUE"}

        test_temps = [mock_temp1, mock_temp2]
        open_nebula = "default"

        # Mock one object and run action
        mock_info = mock.Mock()
        mock_info.VMTEMPLATE = test_temps
        mock_one = mock.Mock()
        mock_one.templatepool.info.return_value = mock_info
        mock_session.return_value = mock_one
        with self.assertRaises(Exception):
            action.run(template_name, open_nebula)
