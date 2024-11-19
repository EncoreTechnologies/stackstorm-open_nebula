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
from lib.action_base import BaseAction
import unittest.mock as mock
from collections import OrderedDict

__all__ = [
    'BaseActionTestCase'
]


class BaseActionTestCase(OneBaseActionTestCase):
    __test__ = True
    action_cls = BaseAction

    def test_init(self):
        action = self.get_action_instance(self._config_good)
        self.assertIsInstance(action, BaseAction)

    def test_init_blank_config(self):
        with self.assertRaises(ValueError):
            self.get_action_instance(self._config_blank)

    def test_init_one_blank_config(self):
        with self.assertRaises(ValueError):
            self.get_action_instance(self._config_one_blank)

    def test_init_no_one_config(self):
        with self.assertRaises(ValueError):
            self.get_action_instance(self._config_no_one)

    def raise_error(self):
        raise AttributeError()
        # raise Exception(AttributeError)

    # @mock.patch("lib.action_base.ssl._create_unverified_context",
    # side_effect=Exception(AttributeError))
    def test_init_ssl_error(self):
        # mock_ssl._create_unverified_context = self.raise_error()
        # mock_ssl.side_effect = AttributeError()
        # mockedObj = mock_ssl.return_value
        # mockedObj._create_unverified_context.side_effect = self.raise_error
        # mockedObj._create_unverified_context.side_effect =
        # mock.Mock(side_effect=AttributeError('Test'))

        with mock.patch('lib.action_base.ssl._create_unverified_context',
                        side_effect=AttributeError('mocked error')):
            action = self.get_action_instance(self._config_good)
            self.assertIsInstance(action, BaseAction)

    def test_get_connection_info(self):
        action = self.get_action_instance(self._config_good)

        # define test variables
        test_one = 'default'
        # The following values are from the cfg_config_new
        expected_result = {'passwd': 'passwd', 'host': 'test.com',
                           'port': 2633, 'user': 'user'}

        # invoke action with a valid config
        result = action._get_connection_info(test_one)

        self.assertEqual(result, expected_result)

    def test_get_connection_info_partial(self):
        action = self.get_action_instance(self._config_partial)

        # define test variables
        test_one = 'default'

        # invoke action with an invalid config
        with self.assertRaises(KeyError):
            action._get_connection_info(test_one)

    @mock.patch("lib.action_base.pyone")
    def test_pyone_session_create(self, mock_pyone):
        action = self.get_action_instance(self._config_good)

        # define test variables
        test_one = 'default'
        expected_result = 'result'

        mock_pyone.OneServer.return_value = expected_result

        result = action.pyone_session_create(test_one)

        self.assertEqual(result, expected_result)
        # Values below came from the _config_good file
        mock_pyone.OneServer.assert_called_with('http://test.com:2633/RPC2',
                                                session='user:passwd')

    @mock.patch("lib.action_base.xmlrpc")
    def test_xmlrpc_session_create(self, mock_xmlrpc):
        action = self.get_action_instance(self._config_good)

        # define test variables
        test_one = 'default'
        expected_result = 'result'

        mock_xmlrpc.client.ServerProxy.return_value = expected_result

        result = action.xmlrpc_session_create(test_one)

        self.assertEqual(result, expected_result)
        # Values below came from the _config_good file
        mock_xmlrpc.client.ServerProxy.assert_called_with('http://test.com:2633')

    def test_vm_labels_get(self):
        action = self.get_action_instance(self._config_good)

        # define test variables
        labels = 'label1,label2'
        test_vm = mock.Mock()
        test_vm.USER_TEMPLATE = {
            'NAME': 'TEST-VM',
            'LABELS': labels
        }
        expected_result = labels.split(',')

        result = action.vm_labels_get(test_vm)

        self.assertEqual(result, expected_result)

    def test_template_disks_get_single(self):
        action = self.get_action_instance(self._config_good)

        # define test variables
        test_disk = OrderedDict()
        test_disk['name'] = 'disk1'
        test_template = mock.Mock()
        test_template.TEMPLATE = {
            'NAME': 'TEST-TEMP',
            'DISK': test_disk
        }
        expected_result = [{'name': 'disk1'}]

        result = action.template_disks_get(test_template)

        self.assertEqual(result, expected_result)

    def test_template_disks_get_many(self):
        action = self.get_action_instance(self._config_good)

        # define test variables
        expected_result = [{'name': 'disk1'}, {'name': 'disk2'}]
        test_template = mock.Mock()
        test_template.TEMPLATE = {
            'NAME': 'TEST-TEMP',
            'DISK': expected_result
        }

        result = action.template_disks_get(test_template)

        self.assertEqual(result, expected_result)

    def test_get_all_vm_ids(self):
        action = self.get_action_instance(self._config_good)

        # define test variables
        mock_vm1 = mock.Mock()
        mock_vm1.ID = '6'
        mock_vm2 = mock.Mock()
        mock_vm2.ID = '7'
        mock_vms = mock.Mock()
        mock_vms.VM = [mock_vm1, mock_vm2]
        mock_one = mock.Mock()
        mock_one.vmpool.info.return_value = mock_vms
        expected_result = [6, 7]

        result = action.get_all_vm_ids(mock_one)

        self.assertEqual(result, expected_result)
        mock_one.vmpool.info.assert_called_with(-2, -1, -1, -1)

    def test_run(self):
        action = self.get_action_instance(self._config_good)

        with self.assertRaises(RuntimeError):
            action.run()
