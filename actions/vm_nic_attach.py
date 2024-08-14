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


class VmNicAttach(BaseAction):
    def run(self, attach_timeout, gateway, ip_addr, method, network_id, vm_id, open_nebula=None):
        # Create one session
        one = self.pyone_session_create(open_nebula)

        # Create nic attributes
        nic_attributes = "NIC=[IP={}, NETWORK_ID={}, GATEWAY={}, METHOD={}]".format(ip_addr,
                                                                                    network_id,
                                                                                    gateway,
                                                                                    method)

        # Attach nic
        one.vm.attachnic(vm_id, nic_attributes)

        # Wait for nic to attach
        lcm_state = self.wait_for_vm(one, vm_id, attach_timeout)

        # Check if nic was attached
        if lcm_state != 3:
            return (False, "Timed out waiting for VM {} to enter running state after attaching NIC".format(vm_id))
        else:
            return (True, "Succesfully attached NIC to VM {}".format(vm_id))
