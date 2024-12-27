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
from templates_get_with_label import TemplatesGetWithLabel
import unittest.mock as mock
import xmltodict


__all__ = [
    'TemplatesGetWithLabelTestCase'
]


class TemplatesGetWithLabelTestCase(OneBaseActionTestCase):
    __test__ = True
    action_cls = TemplatesGetWithLabel

    @mock.patch("lib.action_base.BaseAction.xmlrpc_session_create")
    def test_run(self, mock_session):
        action = self.get_action_instance(self._config_good)

        # Define test parameters
        label_name = 'LABEL'
        open_nebula = 'default'
        auth_string = 'user:pass'
        action.auth_string = auth_string
        expected_result = 'test-server.com'

        # Mock one object and run action
        temp1 = {
            'NAME': 'temp1',
            'TEMPLATE': {
                'LABELS': 'LABEL'
            }
        }
        temp2 = {
            'NAME': 'temp2',
            'TEMPLATE': {
                'LABELS': 'NOTFOUND'
            }
        }
        temp3 = {
            'NAME': 'temp3',
            'TEMPLATE': {
                'LABELS': 'TEST,LABEL'
            }
        }
        temp4 = {
            'NAME': 'temp3',
            'TEMPLATE': {'DONT': 'INCLUDE'}
        }
        test_templates = {
            'VMTEMPLATE_POOL': {
                'VMTEMPLATE': [temp1, temp2, temp3, temp4]
            }
        }
        expected_result = [temp1, temp3]

        mock_one = mock.Mock()
        # Convert the templates dict to xml for the xmltojson.parse function in the action
        mock_one.one.templatepool.info.return_value = [
            True,
            xmltodict.unparse(test_templates, pretty=True)
        ]
        mock_session.return_value = mock_one
        result = action.run(label_name, open_nebula)

        # Verify result and calls
        self.assertEqual(expected_result, result)
        mock_session.assert_called_with(open_nebula)
        mock_one.one.templatepool.info.assert_called_with(auth_string, *tuple([-2, -1, -1, -1]))

    @mock.patch("lib.action_base.BaseAction.xmlrpc_session_create")
    def test_run_single(self, mock_session):
        action = self.get_action_instance(self._config_good)

        # Define test parameters
        label_name = 'LABEL'
        open_nebula = 'default'
        auth_string = 'user:pass'
        action.auth_string = auth_string
        expected_result = 'test-server.com'

        # Mock one object and run action
        temp1 = {
            'NAME': 'temp1',
            'TEMPLATE': {
                'LABELS': 'LABEL'
            }
        }
        test_templates = {
            'VMTEMPLATE_POOL': {
                'VMTEMPLATE': temp1
            }
        }
        expected_result = [temp1]

        mock_one = mock.Mock()
        # Convert the templates dict to xml for the xmltojson.parse function in the action
        mock_one.one.templatepool.info.return_value = [
            True,
            xmltodict.unparse(test_templates, pretty=True)
        ]
        mock_session.return_value = mock_one
        result = action.run(label_name, open_nebula)

        # Verify result and calls
        self.assertEqual(expected_result, result)
        mock_session.assert_called_with(open_nebula)
        mock_one.one.templatepool.info.assert_called_with(auth_string, *tuple([-2, -1, -1, -1]))

    @mock.patch("lib.action_base.BaseAction.xmlrpc_session_create")
    def test_run_error(self, mock_session):
        action = self.get_action_instance(self._config_good)

        # Define test parameters
        label_name = 'LABEL'
        open_nebula = 'default'
        auth_string = 'user:pass'
        action.auth_string = auth_string

        # Mock one object and run action
        mock_one = mock.Mock()
        mock_one.one.templatepool.info.return_value = [False, 'error']
        mock_session.return_value = mock_one

        with self.assertRaises(Exception):
            action.run(label_name, open_nebula)
