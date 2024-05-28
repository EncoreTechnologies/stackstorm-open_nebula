
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


class TemplateClone(BaseAction):
    def run(self, clone_images, new_name, template_id, open_nebula=None):
        """ Clones an existing virtual machine template
        :returns: Result from template clone action
        """
        one = self.pyone_session_create(open_nebula)

        # More info on these params can be found here:
        # https://docs.opennebula.io/6.8/integration_and_development/system_interfaces/api.html#one-template-clone
        return one.template.clone(template_id, new_name, clone_images)
