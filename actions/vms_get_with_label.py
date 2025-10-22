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
import xmltojson
import json


class VmsGetWithLabel(BaseAction):
    def run(self, label_name, open_nebula=None):
        """ Retrieves a list of VMs on an Open Nebula system that include the given label
        :returns: VM information with name and ID appended
        """
        one_session = self.xmlrpc_session_create(open_nebula)
        response = one_session.one.vmpool.infoextended(self.auth_string, *tuple([-2, -1, -1, -1]))

        # Check the result for an error (first element will be FALSE on error)
        if response[0]:
            vm_pool = json.loads(xmltojson.parse(response[1]))
            vms = vm_pool['VM_POOL']['VM']
        else:
            raise Exception(response[1])

        label_vms = []
        for vm in vms:
            try:
                labels = vm['USER_TEMPLATE']['LABELS']
                if labels and label_name in labels.split(','):
                    label_vms.append(vm)
            except KeyError:
                continue

        return label_vms
