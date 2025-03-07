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
from data_get_all import DataGetAll
import unittest.mock as mock
import json


__all__ = [
    'DataGetAllTestCase'
]


class DataGetAllTestCase(OneBaseActionTestCase):
    __test__ = True
    action_cls = DataGetAll

    def test_get_vm_snapshot_count(self):
        # Run the action 3 times checking for 0, 1, and 2 snapshots
        vm = {'snapshots': {'snapshot': [{'id': 1}, {'id': 2}]}}
        result = self.action.get_vm_snapshot_count(vm)
        assert result == 2

        vm = {'snapshots': {'snapshot': {'id': 1}}}
        result = self.action.get_vm_snapshot_count(vm)
        assert result == 1

        vm = {}
        result = self.action.get_vm_snapshot_count(vm)
        assert result == 0

    def test_update_vm_list(self):
        obj = {'template': {'disk': [{'size': '2048'}, {'size': '1024'}]}}
        result = self.action.update_vm(obj)
        assert result['template']['disk_space'] == '3.0'
        assert result['snapshot_count'] == 0

    def test_update_vm(self):
        obj = {'template': {'disk': {'size': '2048'}}}
        result = self.action.update_vm(obj)
        assert result['template']['disk_space'] == '2.0'
        assert result['snapshot_count'] == 0

    def test_update_datastore(self):
        obj = {'total_mb': '2048'}
        result = self.action.update_datastore(obj)
        assert result['capacity_gb'] == '2.0'

    def test_update_host(self):
        obj = {'host_share': {'total_cpu': '2000', 'total_mem': '2097152', 'numa_nodes': {}}}
        result = self.action.update_host(obj)
        assert result['host_share']['cpu_ghz'] == '2.0'
        assert result['host_share']['mem_gb'] == '2.0'
        assert 'numa_nodes' not in result['host_share']

    def test_update_network(self):
        obj = {}
        result = self.action.update_network(obj)
        assert result == obj

    def test_zones_to_csv(self):
        obj = {'template': {'zone': 'test1 test2'}}
        result = self.action.zones_to_csv(obj, 'VNET')
        assert result == {'template': {'zone': 'test1,test2'}}

    def test_zones_to_csv_no_zone(self):
        obj = {'template': {'no_zone': 'no_zone'}}
        result = self.action.zones_to_csv(obj, 'VNET')
        assert result == obj

    def test_zones_to_csv_no_template(self):
        obj = {'no_template': 'no_template'}
        result = self.action.zones_to_csv(obj, 'VM')
        assert result == obj

    def test_update_objects(self):
        objects = [{'template': {'disk': [{'size': '2048'}, {'size': '1024'}]}}]
        result = self.action.update_objects(objects, 'VM')
        assert result[0]['template']['disk_space'] == '3.0'
        assert result[0]['snapshot_count'] == 0

    def test_update_objects_zones(self):
        objects = [{'template': {'zone': 'test1 test2'}}]
        result = self.action.update_objects(objects, 'VNET')
        assert result[0]['template']['zone'] == 'test1,test2'

    def test_update_objects_not_found(self):
        objects = [{'template': {'disk': [{'size': '2048'}, {'size': '1024'}]}}]
        result = self.action.update_objects(objects, 'NOT_FOUNT')
        self.assertEqual(result, objects)

    def test_filter_templates(self):
        self.action.template_label_filters = ['label1']
        templates = [{'template': {'labels': 'label1,label2'}},
                     {'template': {'labels': 'label3'}},
                     {'template': {'no_labels': 'test'}}]
        result = self.action.filter_templates(templates)
        assert len(result) == 1
        expected_result = [{'template': {'labels': 'label1,label2'}}]
        self.assertEqual(expected_result, result)

        self.action.template_label_filters = []
        result = self.action.filter_templates(templates)
        assert len(result) == 3
        self.assertEqual(result, templates)

    def test_filter_objects(self):
        self.action.template_label_filters = ['label1']
        objects = [{'template': {'labels': 'label1,label2'}}, {'template': {'labels': 'label3'}}]
        result = self.action.filter_objects(objects, 'VMTEMPLATE')
        assert len(result) == 1
        assert result[0]['template']['labels'] == 'label1,label2'

        result = self.action.filter_objects(objects, 'VM')
        assert len(result) == 2

    @mock.patch('data_get_all.xmltojson.parse')
    def test_get_objects_success_multiple_objects(self, mock_parse):
        endpoint = "some_endpoint"
        object_options = ["option1", "option2"]
        object_type = "VM"
        response = (True, "<xml></xml>")
        objects = [{"id": 1}, {"id": 2}]
        object_pool = {f"{object_type}_POOL": {object_type: objects}}

        self.action.session.some_endpoint.return_value = response
        mock_parse.return_value = json.dumps(object_pool)
        self.action.lowercase_keys = mock.Mock(return_value=objects)
        self.action.filter_objects = mock.Mock(return_value=objects)
        self.action.update_objects = mock.Mock(return_value=objects)

        result = self.action.get_objects(endpoint, object_options, object_type)

        assert result == objects
        self.action.session.some_endpoint.assert_called_once_with(self.action.auth_string,
                                                                  *tuple(object_options))
        mock_parse.assert_called_once_with(response[1])
        self.action.lowercase_keys.assert_called_once_with(objects)
        self.action.filter_objects.assert_called_once_with(objects, object_type)
        self.action.update_objects.assert_called_once_with(objects, object_type)

    @mock.patch('data_get_all.xmltojson.parse')
    def test_get_objects_success_single_object(self, mock_parse):
        endpoint = "some_endpoint"
        object_options = ["option1", "option2"]
        object_type = "VM"
        response = (True, "<xml></xml>")
        objects = {"id": 1}
        object_pool = {f"{object_type}_POOL": {object_type: objects}}

        self.action.session.some_endpoint.return_value = response
        mock_parse.return_value = json.dumps(object_pool)
        self.action.lowercase_keys = mock.Mock(return_value=[objects])
        self.action.filter_objects = mock.Mock(return_value=[objects])
        self.action.update_objects = mock.Mock(return_value=[objects])

        result = self.action.get_objects(endpoint, object_options, object_type)

        assert result == [objects]
        self.action.session.some_endpoint.assert_called_once_with(self.action.auth_string,
                                                                  *tuple(object_options))
        mock_parse.assert_called_once_with(response[1])
        self.action.lowercase_keys.assert_called_once_with([objects])
        self.action.filter_objects.assert_called_once_with([objects], object_type)
        self.action.update_objects.assert_called_once_with([objects], object_type)

    def test_get_objects_error_response(self):
        endpoint = "some_endpoint"
        object_options = ["option1", "option2"]
        object_type = "VM"
        response = (False, "Error message")

        self.action.session.some_endpoint.return_value = response

        with self.assertRaises(Exception):
            excinfo = self.action.get_objects(endpoint, object_options, object_type)
            assert str(excinfo.value) == "Error message"
            self.action.session.some_endpoint.assert_called_once_with(self.action.auth_string,
                                                                      *tuple(object_options))

    def test_lowercase_keys(self):
        obj = [{'KEY': 'value', 'NESTED': {'NESTED_KEY': 'nested_value'}}]
        result = self.action.lowercase_keys(obj)
        assert result == [{'key': 'value', 'nested': {'nested_key': 'nested_value'}}]

    @mock.patch("data_get_all.DataGetAll.add_wilds")
    @mock.patch("data_get_all.DataGetAll.get_objects")
    @mock.patch("lib.action_base.BaseAction.xmlrpc_session_create")
    def test_run(self, mock_session, mock_get_objects, mock_add_wilds):
        action = self.get_action_instance(self._config_good)
        api_config = [
            {
                'name': 'vms',
                'endpoint': 'one.test.endpoint',
                'options': [-2, -1, -1, -1],
                'type': 'TEST'
            },
            {
                'name': 'networks',
                'endpoint': 'one.test.endpoint',
                'options': [-2, -1, -1],
                'type': 'TEST'
            },
            {
                'name': 'hosts',
                'endpoint': 'one.test.endpoint',
                'options': [-2, -1, -1],
                'type': 'TEST'
            }
        ]
        template_label_filters = ['filter', 'list']
        open_nebula = 'default'
        test_session = 'session'
        mock_session.return_value = test_session
        mock_get_objects.side_effect = ['obj1', 'obj2', 'obj3']
        mock_add_wilds.return_value = ['wild1', 'wild2']

        expected_result = {
            'vms': 'obj1',
            'networks': 'obj2',
            'hosts': 'obj3',
            'wilds': ['wild1', 'wild2'],
            'hostname': 'test.com',
            'hypervisor_type': 'open_nebula'
        }

        result = action.run(api_config, template_label_filters, open_nebula)

        # Verify result and calls
        self.assertEqual(expected_result, result)
        mock_session.assert_called_with(open_nebula)
        self.assertEqual(mock_get_objects.call_count, len(api_config))
        mock_get_objects.assert_has_calls = [
            mock.call('one.vmpool.infoextended', [-2, -1, -1, -1], 'VM'),
            mock.call('one.vnpool.info', [-2, -1, -1], 'VNET')
        ]

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
