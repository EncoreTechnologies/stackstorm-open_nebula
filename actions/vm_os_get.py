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

class VmOsGet(BaseAction):
    OS_MAP = {
        'rhel8': {
            'type': 'linux',
            'distro': 'rhel',
            'version': '8'
        },
        'rhel9': {
            'type': 'linux',
            'distro': 'rhel',
            'version': '9'
        }
    }

    # If a key from the OS_MAP is found in the name from Open Nebula
    # then return the OS hash associated with that key
    def get_os_name(self, one_os):
        for attr, value in self.OS_MAP.items():
            if attr in one_os:
                return value
        raise Exception("No OS found in hash for {}".format(one_os))

    def run(self, vm_id, open_nebula=None):
        """ Return the OS name of the given VM from the extended info
        :returns: VM OS name
        """
        one = self.pyone_session_create(open_nebula)
        vm = one.vm.info(vm_id)
        try:
            one_os = vm.TEMPLATE['OS']['MACHINE']
        except:
            raise Exception("No OS name found for VM ID: {}".format(vm_id))

        return self.get_os_name(one_os)
