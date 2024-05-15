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

import json
from lib.action_base import BaseAction

class VmResize(BaseAction):
    # Open Nebula does not allow allocating less memory or CPU than the template
    # that the VM was instantiated from
    def check_template_sizes(self, cpu_num, mem_mb, vcpu_num, temp):
        temp = json.loads(json.dumps(temp.TEMPLATE))
        # Any values that are 0 will be ignored by the API
        if cpu_num > 0 and cpu_num < int(temp['CPU']):
            raise ValueError("Cannot allocate less CPUs than the template: {}".format(temp['CPU']))
        if mem_mb > 0 and mem_mb < int(temp['MEMORY']):
            raise ValueError("Cannot allocate less memory than the template: {}".format(temp['MEMORY']))
        if vcpu_num > 0 and vcpu_num < int(temp['VCPU']):
            raise ValueError("Cannot allocate less VCPUs than the template: {}".format(temp['VCPU']))


    def run(self, cpu_num, mem_mb, vcpu_num, vm_id, open_nebula=None):
        """ Changes the capacity of CPU, VCPU, and/or MEMORY on the virtual machine
        :returns: Return object from the resize method
        """
        one = self.pyone_session_create(open_nebula)
        vm = one.vm.info(vm_id)

        # Retrieve the template to verify that the VM can be resized
        temp_id = int(vm.TEMPLATE['TEMPLATE_ID'])
        temp = one.template.info(temp_id)
        self.check_template_sizes(cpu_num, mem_mb, vcpu_num, temp)

        template_string = """<TEMPLATE>
            <CPU>{}</CPU>
            <MEMORY>{}</MEMORY>
            <VCPU>{}</VCPU>
        </TEMPLATE>""".format(cpu_num, mem_mb, vcpu_num)

        # True below ensures the Host capacity is not overcommitted
        return one.vm.resize(vm_id, template_string, True)
