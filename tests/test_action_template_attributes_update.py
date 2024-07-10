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

from template_attributes_update import TemplateAttributeUpdate
import unittest.mock as mock

__all__ = [
    'TemplateAttributeUpdateTestCase'
]


class TemplateAttributeUpdateTestCase(OneBaseActionTestCase):
    __test__ = True
    action_cls = TemplateAttributeUpdate

    @mock.patch("lib.action_base.BaseAction.pyone_session_create")
    def test_run(self, mock_session):
        action = self.get_action_instance(self._config_good)

        # Define test parameters
        attributes = {'ATTR': 'VALUE'}
        template_id = 0
        open_nebula = 'default'
        expected_result = 'result'

        # Mock one object and run action
        mock_one = mock.Mock()
        mock_one.template.update.return_value = expected_result
        mock_session.return_value = mock_one
        result = action.run(attributes, template_id, open_nebula)

        # Verify result and calls
        self.assertEqual(expected_result, result)
        mock_session.assert_called_with(open_nebula)
        mock_one.template.update.assert_called_with(template_id, attributes, 1)
