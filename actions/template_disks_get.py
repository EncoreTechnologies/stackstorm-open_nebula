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


class TemplateDisksGet(BaseAction):
    def run(self, template_id, open_nebula=None):
        """ Return a list of disks on the given Template
        :returns: List of disks on the given Template or empty list of none found
        """
        one = self.pyone_session_create(open_nebula)
        template = one.template.info(template_id)

        return self.template_disks_get(template)
