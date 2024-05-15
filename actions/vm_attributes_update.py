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

class VmAttributesUpdate(BaseAction):
    def run(self, attributes, vm_id, open_nebula=None):
        """ Updates the given hash of attributes of the given VM
        Can be used to update the following:
        https://docs.opennebula.io/6.8/management_and_operations/references/template.html
        :returns: Return object with the VM ID
        """
        one = self.pyone_session_create(open_nebula)
        # The 1 below merges this new template with the existing one
        return one.vm.update(vm_id, attributes, 1)
