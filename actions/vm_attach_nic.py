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
import time


class VmAttachNic(BaseAction):
    def parse_gateway(self, ip_addr):
        parts = ip_addr.split('.')
        parts[-1] = '1'
        gateway = '.'.join(parts)
        return gateway

    def wait_for_nic(self, one, vm_id, attach_timeout):
        # Wait for nic to attach - LCM State of 3 is 'running'
        lcm_state = one.vm.info(vm_id).LCM_STATE
        start_time = time.time()
        while lcm_state != 3:
            # Set elapsed time for timeout check
            elapsed_time = time.time() - start_time
            if elapsed_time > attach_timeout:
                return lcm_state

            # Wait before checking again
            time.sleep(5)

            # Update the image state for next check
            lcm_state = one.vm.info(vm_id).LCM_STATE

        return lcm_state

    def run(self, attach_timeout, ip_addr, method, network_id, vm_id, open_nebula=None):
        # Create one session
        one = self.pyone_session_create(open_nebula)

        # Create nic attributes
        gateway = self.parse_gateway(ip_addr)
        nic_attributes = "NIC=[IP={}, NETWORK_ID={}, GATEWAY={}, METHOD={}]".format(ip_addr,
                                                                                    network_id,
                                                                                    gateway,
                                                                                    method)

        # Attach nic
        one.vm.attachnic(vm_id, nic_attributes)

        # Wait for nic to attach
        lcm_state = self.wait_for_nic(one, vm_id, attach_timeout)

        # Check if nic was attached
        if lcm_state != 3:
            return (False, "Timed out waiting for VM {} to enter running state after attaching NIC".format(vm_id))
        else:
            return (True, "Succesfully attached NIC to VM {}".format(vm_id))
