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


class TemplateGetByName(BaseAction):
    def run(self, template_name, open_nebula=None):
        """ Retrieves the given template by name on an Open Nebula system
        :returns: Template information with name and ID appended
        """
        one = self.pyone_session_create(open_nebula)

        # More info on these params can be found here:
        # https://docs.opennebula.io/6.8/integration_and_development/system_interfaces/api.html#one-templatepool-info
        temppoolInfo = one.templatepool.info(-2, -1, -1, -1)
        temps = temppoolInfo.VMTEMPLATE

        for temp in temps:
            if temp.NAME == template_name:
                return_obj = temp.TEMPLATE
                return_obj['ID'] = temp.ID
                return_obj['NAME'] = temp.NAME
                return return_obj

        # Fallback: try matching by stripped name in case of whitespace in Open Nebula
        matches = []
        for temp in temps:
            if temp.NAME.strip() == template_name:
                matches.append(temp)

        if len(matches) == 1:
            return_obj = matches[0].TEMPLATE
            return_obj['ID'] = matches[0].ID
            return_obj['NAME'] = matches[0].NAME
            return return_obj
        elif len(matches) > 1:
            raise Exception("ERROR: Multiple templates found matching '{}' "
                            "after stripping whitespace".format(template_name))

        raise Exception("ERROR: No templates found with name: " + template_name)
