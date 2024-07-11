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


class TemplateInstantiate(BaseAction):
    def run(self, template_id, vm_name, open_nebula=None):
        """ Instantiates a new virtual machine from a given template ID
        :returns: ID of the newly instantiated VM
        """
        one = self.pyone_session_create(open_nebula)

        # More info on these params can be found here:
        # https://docs.opennebula.io/6.8/integration_and_development/system_interfaces/api.html#one-template-instantiate
        return one.template.instantiate(template_id, vm_name)
