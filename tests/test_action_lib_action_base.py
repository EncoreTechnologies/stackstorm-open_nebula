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

    def test_run(self):
        action = self.get_action_instance(self._config_good)

        with self.assertRaises(RuntimeError):
            action.run()
