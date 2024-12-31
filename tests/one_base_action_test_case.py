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
import yaml
import json
import logging
import mock

from st2tests.base import BaseActionTestCase


class OneBaseActionTestCase(BaseActionTestCase):
    __test__ = False

    def setUp(self):
        super(OneBaseActionTestCase, self).setUp()
        logging.disable(logging.CRITICAL)  # disable logging
        self._config_good = self.load_yaml('config_good.yaml')
        self._config_blank = self.load_yaml('config_blank.yaml')
        self._config_partial = self.load_yaml('config_partial.yaml')
        self._config_one_blank = self.load_yaml('config_one_blank.yaml')
        self._config_no_one = self.load_yaml('config_no_one.yaml')
        self.action = self.get_action_instance(self._config_good)
        self.action.session = mock.Mock()
        self.action.auth_string = "auth_string"

    def tearDown(self):
        super(OneBaseActionTestCase, self).tearDown()
        logging.disable(logging.NOTSET)  # enable logging

    def load_yaml(self, filename):
        return yaml.safe_load(self.get_fixture_content(filename))

    def load_json(self, filename):
        return json.loads(self.get_fixture_content(filename))

    @property
    def config_good(self):
        return self._config_good

    @property
    def config_blank(self):
        return self._config_blank

    @property
    def config_partial(self):
        return self._config_partial

    @property
    def config_one_blank(self):
        return self._config_one_blank

    @property
    def config_no_one(self):
        return self._config_no_one
