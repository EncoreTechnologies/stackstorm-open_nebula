#!/usr/bin/env python
# Copyright 2026 Encore Technologies
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


class VmHostGet(BaseAction):
    def run(self, vm_id, open_nebula=None):
        one = self.pyone_session_create(open_nebula)
        host_pool = one.hostpool.info()

        vm_id_str = str(vm_id)

        for host in host_pool.HOST:
            try:
                host_vm_ids = host.VMS.ID
            except (AttributeError, TypeError):
                continue

            if not isinstance(host_vm_ids, list):
                host_vm_ids = [host_vm_ids]

            if vm_id_str in [str(vid) for vid in host_vm_ids]:
                return host.NAME

        return None
