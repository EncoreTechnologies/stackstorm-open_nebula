
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


class VmsGetByName(BaseAction):
    def run(self, vm_name, open_nebula=None):
        one = self.pyone_session_create(open_nebula)

        filter = 'NAME=' + vm_name
        # More info on these params can be found here:
        # https://docs.opennebula.io/6.8/integration_and_development/system_interfaces/api.html
        vmpoolInfo = one.vmpool.infoextended(-2, -1, -1, -1, filter)
        vms = vmpoolInfo.VM

        if len(vms) == 0:
            raise Exception("ERROR: No VMs found with name: " + vm_name)
        elif len(vms) > 1:
            raise Exception("ERROR: Multiple VMs found with name: " + vm_name)

        # If only 1 VM was found then return its template info
        return vms[0].TEMPLATE