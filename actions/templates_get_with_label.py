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

from lib.action_base import BaseAction
import xmltojson
import json


class TemplatesGetWithLabel(BaseAction):
    def run(self, label_name, open_nebula=None):
        """ Retrieves the given template by name on an Open Nebula system
        :returns: Template information with name and ID appended
        """
        one_session = self.xmlrpc_session_create(open_nebula)

        method = getattr(one_session, 'one.templatepool.info')
        response = method(self.auth_string, *tuple([-2, -1, -1, -1]))

        # Check the result for an error (first element will be FALSE on error)
        if response[0]:
            template_pool = json.loads(xmltojson.parse(response[1]))
            templates = template_pool['VMTEMPLATE_POOL']['VMTEMPLATE']
            # If only one object is found then it will be returned as a single object and not a list
            if type(templates) is dict:
                templates = [templates]
        else:
            raise Exception(response[1])

        label_temps = []
        for temp in templates:
            try:
                labels = temp['TEMPLATE']['LABELS']
                if label_name in labels.split(','):
                    label_temps.append(temp)
            except KeyError:
                continue

        return label_temps
