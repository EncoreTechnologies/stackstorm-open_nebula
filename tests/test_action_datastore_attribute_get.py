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
from datastore_attribute_get import DatastoreAttributeGet
import unittest.mock as mock

__all__ = [
    'DatastoreAttributeGetTestCase'
]


class DatastoreAttributeGetTestCase(OneBaseActionTestCase):
    __test__ = True
    action_cls = DatastoreAttributeGet

    @mock.patch("lib.action_base.BaseAction.pyone_session_create")
    def test_run_single_attr(self, mock_session):
        action = self.get_action_instance(self._config_good)

        # Define test parameters
        attribute_name = ['NAME']
        ds_id = 0
        open_nebula = 'default'
        expected_result = 'test-server.com'

        # Mock one object and run action
        mock_ds = mock.Mock()
        mock_ds.NAME = expected_result
        mock_one = mock.Mock()
        mock_one.datastore.info.return_value = mock_ds
        mock_session.return_value = mock_one
        result = action.run(attribute_name, ds_id, open_nebula)

        # Verify result and calls
        self.assertEqual(expected_result, result)
        mock_session.assert_called_with(open_nebula)
        mock_one.datastore.info.assert_called_with(ds_id)

    @mock.patch("lib.action_base.BaseAction.pyone_session_create")
    def test_run_multi_attr(self, mock_session):
        action = self.get_action_instance(self._config_good)

        # Define test parameters
        attribute_name = ['TEMPLATE', 'CPU']
        ds_id = 0
        open_nebula = 'default'
        expected_result = '2'

        # Mock one object and run action
        mock_ds = mock.Mock()
        mock_ds.TEMPLATE = {'CPU': '2'}
        mock_one = mock.Mock()
        mock_one.datastore.info.return_value = mock_ds
        mock_session.return_value = mock_one
        result = action.run(attribute_name, ds_id, open_nebula)

        # Verify result and calls
        self.assertEqual(expected_result, result)
        mock_session.assert_called_with(open_nebula)
        mock_one.datastore.info.assert_called_with(ds_id)

    @mock.patch("lib.action_base.BaseAction.pyone_session_create")
    def test_run_multi_error(self, mock_session):
        action = self.get_action_instance(self._config_good)

        # Define test parameters
        attribute_name = ['TEMPLATE', 'NOTFOUND']
        ds_id = 0
        open_nebula = 'default'

        # Mock one object and run action
        mock_ds = mock.Mock()
        mock_ds.TEMPLATE = {'CPU': '2'}
        mock_one = mock.Mock()
        mock_one.datastore.info.return_value = mock_ds
        mock_session.return_value = mock_one

        with self.assertRaises(ValueError):
            action.run(attribute_name, ds_id, open_nebula)
            mock_session.assert_called_with(open_nebula)
            mock_one.datastore.info.assert_called_with(ds_id)
