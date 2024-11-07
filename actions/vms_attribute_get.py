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
from collections.abc import Mapping
import json


class VmsAttributeGet(BaseAction):
    def run(self, attribute_name, vm_ids, open_nebula=None):
        """ Return the value of the given attribute from the VMs
        :returns: Dictionary with results and attribute_not_set lists
        """
        results = []
        attribute_not_set = []

        one = self.pyone_session_create(open_nebula)

        for vm_id in vm_ids:
            vm = one.vm.info(vm_id)
            return_value = vm
            attribute_found = True

            for attr in attribute_name:
                if hasattr(return_value, attr):
                    return_value = json.loads(json.dumps(getattr(return_value, attr)))
                elif isinstance(return_value, Mapping) and attr in return_value:
                    return_value = return_value[attr]
                else:
                    attribute_found = False
                    break

            if attribute_found:
                results.append({
                    'vm_id': vm_id,
                    'vm_name': vm.NAME,
                    attribute_name[-1]: return_value
                })
            else:
                attribute_not_set.append({
                    'vm_id': vm_id,
                    'vm_name': vm.NAME
                })

        return {
            'vms_with_attribute': results,
            'attribute_not_set': attribute_not_set
        }
