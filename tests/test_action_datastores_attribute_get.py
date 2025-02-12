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

from datastores_attribute_get import DatastoresAttributeGet
import unittest.mock as mock

__all__ = [
    'DatastoresAttributeGetTestCase'
]


class DatastoresAttributeGetTestCase(OneBaseActionTestCase):
    __test__ = True
    action_cls = DatastoresAttributeGet

    @mock.patch("lib.action_base.BaseAction.pyone_session_create")
    def test_run_attribute_found(self, mock_session):
        action = self.get_action_instance(self._config_good)

        # Define test parameters
        mock_ds1 = mock.Mock()
        mock_ds2 = mock.Mock()
        mock_ds1.NAME = "ds1"
        mock_ds2.NAME = "ds2"
        mock_ds1.USER_TEMPLATE = {"BACKUPS": "true"}
        mock_ds2.USER_TEMPLATE = {"BACKUPS": "false"}

        test_dss = [mock_ds1, mock_ds2]
        ds_ids = [1, 2]
        attribute_name = ["USER_TEMPLATE", "BACKUPS"]
        open_nebula = "default"
        expected_result = {
            'ds_with_attribute': [
                {'ds_id': 1, 'ds_name': "ds1", 'BACKUPS': "true"},
                {'ds_id': 2, 'ds_name': "ds2", 'BACKUPS': "false"}
            ],
            'attribute_not_set': []
        }

        # Mock one object and run action
        mock_one = mock.Mock()
        mock_one.datastore.info.side_effect = test_dss
        mock_session.return_value = mock_one
        result = action.run(attribute_name, ds_ids, open_nebula)

        # Verify result and calls
        self.assertEqual(expected_result, result)
        mock_session.assert_called_with(open_nebula)
        mock_one.datastore.info.assert_any_call(1)
        mock_one.datastore.info.assert_any_call(2)

    @mock.patch("lib.action_base.BaseAction.pyone_session_create")
    def test_run_attribute_not_found(self, mock_session):
        action = self.get_action_instance(self._config_good)

        # Define test parameters
        mock_ds1 = mock.Mock()
        mock_ds2 = mock.Mock()
        mock_ds1.NAME = "ds1"
        mock_ds2.NAME = "ds2"
        mock_ds1.USER_TEMPLATE = {"DESCRIPTION": "desc"}
        mock_ds2.USER_TEMPLATE = {"DESCRIPTION": "desc"}

        test_dss = [mock_ds1, mock_ds2]
        ds_ids = [1, 2]
        attribute_name = ["USER_TEMPLATE", "BACKUPS"]
        open_nebula = "default"
        expected_result = {
            'ds_with_attribute': [],
            'attribute_not_set': [
                {'ds_id': 1, 'ds_name': "ds1"},
                {'ds_id': 2, 'ds_name': "ds2"}
            ]
        }

        # Mock one object and run action
        mock_one = mock.Mock()
        mock_one.datastore.info.side_effect = test_dss
        mock_session.return_value = mock_one
        result = action.run(attribute_name, ds_ids, open_nebula)

        # Verify result and calls
        self.assertEqual(expected_result, result)
        mock_session.assert_called_with(open_nebula)
        mock_one.datastore.info.assert_any_call(1)
        mock_one.datastore.info.assert_any_call(2)

    @mock.patch("lib.action_base.BaseAction.pyone_session_create")
    def test_run_mixed_attributes(self, mock_session):
        action = self.get_action_instance(self._config_good)

        # Define test parameters
        mock_ds1 = mock.Mock()
        mock_ds2 = mock.Mock()
        mock_ds3 = mock.Mock()
        mock_ds1.NAME = "ds1"
        mock_ds2.NAME = "ds2"
        mock_ds3.NAME = "ds3"
        mock_ds1.USER_TEMPLATE = {"BACKUPS": "true"}
        mock_ds2.USER_TEMPLATE = {"DESCRIPTION": "desc"}
        mock_ds3.USER_TEMPLATE = {"BACKUPS": "false"}

        test_dss = [mock_ds1, mock_ds2, mock_ds3]
        ds_ids = [1, 2, 3]
        attribute_name = ["USER_TEMPLATE", "BACKUPS"]
        open_nebula = "default"
        expected_result = {
            'ds_with_attribute': [
                {'ds_id': 1, 'ds_name': "ds1", 'BACKUPS': "true"},
                {'ds_id': 3, 'ds_name': "ds3", 'BACKUPS': "false"}
            ],
            'attribute_not_set': [
                {'ds_id': 2, 'ds_name': "ds2"}
            ]
        }

        # Mock one object and run action
        mock_one = mock.Mock()
        mock_one.datastore.info.side_effect = test_dss
        mock_session.return_value = mock_one
        result = action.run(attribute_name, ds_ids, open_nebula)

        # Verify result and calls
        self.assertEqual(expected_result, result)
        mock_session.assert_called_with(open_nebula)
        mock_one.datastore.info.assert_any_call(1)
        mock_one.datastore.info.assert_any_call(2)
        mock_one.datastore.info.assert_any_call(3)
