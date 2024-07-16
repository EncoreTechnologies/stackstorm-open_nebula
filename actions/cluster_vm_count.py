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

class OpenNebulaVMCount(BaseAction):

    def run(self, open_nebula=None):

        one = self.pyone_session_create(open_nebula)
        clustersInfo = one.clusterpool.info()
        clusters = clustersInfo.CLUSTER

        result = {}
        for clst in clusters:
            cluster_value = {}
            vm_count = 0
            if isinstance(clst.HOSTS.ID, list):
                cluster_value = clst.HOSTS.ID
                for host_id in cluster_value:
                    host = one.host.info(host_id)
                    vm_count += len(host.VMS.ID)

            else:
                cluster_value = [clst.HOSTS.ID]
                host = one.host.info(cluster_value)
                vm_count = len(host.VMS.ID)

            result[clst.NAME] = vm_count

        return result