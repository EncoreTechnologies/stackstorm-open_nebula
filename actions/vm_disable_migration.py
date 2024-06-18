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


class VmDisableMigration(BaseAction):
    def get_vm(self, vm_id):
        vms = self.one.vmpool.infoextended(-2, -1, -1, -1, "ID={}".format(vm_id))
        if not vms.VM:
            raise Exception("Could not find VM with ID: {}".format(vm_id))

        return vms.VM[0]

    def get_template_id(self, vm_id):
        vm = self.get_vm(vm_id)

        return int(vm.TEMPLATE['TEMPLATE_ID'])

    def run(self, host_id, vm_id, open_nebula=None):
        # Create pyone session
        self.one = self.pyone_session_create(open_nebula)

        # Get template ID
        template_id = self.get_template_id(vm_id)

        # Set new attributes to merge with current attributes
        attributes = {"SCHED_REQUIREMENTS": "ID='{}'".format(host_id)}

        # Update the template
        self.one.template.update(template_id, attributes, 1)

        # Update the VM with the new scheduling requirement
        self.one.vm.update(int(vm_id), attributes, 1)

        return