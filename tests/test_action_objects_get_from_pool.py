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
import unittest.mock as mock
import pytest
from unittest import mock
from objects_get_from_pool import ObjectsGetFromPool
import json
import xmltojson

__all__ = [
    'ObjectsGetFromPoolTestCase'
]


class ObjectsGetFromPoolTestCase(OneBaseActionTestCase):
    __test__ = True
    action_cls = ObjectsGetFromPool

    @mock.patch('objects_get_from_pool.xmltojson.parse')
    def test_run_success_multiple_objects(self, mock_parse):
        api_endpoint = "some_endpoint"
        object_ids = None
        object_options = ["option1", "option2"]
        object_type = "VM"
        open_nebula = "open_nebula"
        response = (True, "<xml></xml>")
        objects = [{"ID": "1"}, {"ID": "2"}]
        object_pool = {f"{object_type}_POOL": {object_type: objects}}

        self.action.xmlrpc_session_create = mock.Mock(return_value=self.action)
        self.action.some_endpoint = mock.Mock(return_value=response)
        mock_parse.return_value = json.dumps(object_pool)

        result = self.action.run(api_endpoint, object_ids, object_options, object_type, open_nebula)

        assert result == objects
        self.action.xmlrpc_session_create.assert_called_once_with(open_nebula)
        self.action.some_endpoint.assert_called_once_with(self.action.auth_string, *tuple(object_options))
        mock_parse.assert_called_once_with(response[1])

    @mock.patch('objects_get_from_pool.xmltojson.parse')
    def test_run_success_single_object(self, mock_parse):
        api_endpoint = "some_endpoint"
        object_ids = None
        object_options = ["option1", "option2"]
        object_type = "VM"
        open_nebula = "open_nebula"
        response = (True, "<xml></xml>")
        objects = {"ID": "1"}
        object_pool = {f"{object_type}_POOL": {object_type: objects}}

        self.action.xmlrpc_session_create = mock.Mock(return_value=self.action)
        self.action.some_endpoint = mock.Mock(return_value=response)
        mock_parse.return_value = json.dumps(object_pool)

        result = self.action.run(api_endpoint, object_ids, object_options, object_type, open_nebula)

        assert result == [objects]
        self.action.xmlrpc_session_create.assert_called_once_with(open_nebula)
        self.action.some_endpoint.assert_called_once_with(self.action.auth_string, *tuple(object_options))
        mock_parse.assert_called_once_with(response[1])

    @mock.patch('objects_get_from_pool.xmltojson.parse')
    def test_run_with_object_ids(self, mock_parse):
        api_endpoint = "some_endpoint"
        object_ids = [1, 2]
        object_options = ["option1", "option2"]
        object_type = "VM"
        open_nebula = "open_nebula"
        response = (True, "<xml></xml>")
        objects = [{"ID": "1"}, {"ID": "2"}, {"ID": "3"}]
        object_pool = {f"{object_type}_POOL": {object_type: objects}}

        self.action.xmlrpc_session_create = mock.Mock(return_value=self.action)
        self.action.some_endpoint = mock.Mock(return_value=response)
        mock_parse.return_value = json.dumps(object_pool)

        result = self.action.run(api_endpoint, object_ids, object_options, object_type, open_nebula)

        assert result == [{"ID": "1"}, {"ID": "2"}]
        self.action.xmlrpc_session_create.assert_called_once_with(open_nebula)
        self.action.some_endpoint.assert_called_once_with(self.action.auth_string, *tuple(object_options))
        mock_parse.assert_called_once_with(response[1])

    @mock.patch('objects_get_from_pool.xmltojson.parse')
    def test_run_with_missing_object_ids(self, mock_parse):
        api_endpoint = "some_endpoint"
        object_ids = [1, 4]
        object_options = ["option1", "option2"]
        object_type = "VM"
        open_nebula = "open_nebula"
        response = (True, "<xml></xml>")
        objects = [{"ID": "1"}, {"ID": "2"}, {"ID": "3"}]
        object_pool = {f"{object_type}_POOL": {object_type: objects}}

        self.action.xmlrpc_session_create = mock.Mock(return_value=self.action)
        self.action.some_endpoint = mock.Mock(return_value=response)
        mock_parse.return_value = json.dumps(object_pool)

        with pytest.raises(Exception) as excinfo:
            self.action.run(api_endpoint, object_ids, object_options, object_type, open_nebula)

        assert str(excinfo.value) == 'No objects found with the given ID: 4'
        self.action.xmlrpc_session_create.assert_called_once_with(open_nebula)
        self.action.some_endpoint.assert_called_once_with(self.action.auth_string, *tuple(object_options))
        mock_parse.assert_called_once_with(response[1])

    def test_run_error_response(self):
        api_endpoint = "some_endpoint"
        object_ids = None
        object_options = ["option1", "option2"]
        object_type = "VM"
        open_nebula = "open_nebula"
        response = (False, "Error message")

        self.action.xmlrpc_session_create = mock.Mock(return_value=self.action)
        self.action.some_endpoint = mock.Mock(return_value=response)

        with pytest.raises(Exception) as excinfo:
            self.action.run(api_endpoint, object_ids, object_options, object_type, open_nebula)

        assert str(excinfo.value) == "Error message"
        self.action.xmlrpc_session_create.assert_called_once_with(open_nebula)
        self.action.some_endpoint.assert_called_once_with(self.action.auth_string, *tuple(object_options))
