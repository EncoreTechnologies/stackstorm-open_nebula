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

class VmLabelsAdd(BaseAction):
    def run(self, new_labels, vm_id, open_nebula=None):
        """ Append one or more labels to the given VM
        :returns: Return object with the VM ID
        """
        one = self.pyone_session_create(open_nebula)
        vm = one.vm.info(vm_id)
        labels = self.vm_labels_get(vm)
        attributes = {
            'LABELS': ','.join(labels + new_labels)
        }

        # The 1 below merges this new template with the existing one
        return one.vm.update(vm_id, attributes, 1)
