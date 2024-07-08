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

class OpenNebulaHostCount(BaseAction):
    
    def run(self, open_nebula=None):

        one = self.pyone_session_create(open_nebula)
        clustersInfo = one.clusterpool.info()
        clusters = clustersInfo.CLUSTER

        return_value = {}
        for clst in clusters:
            cluster_value = {}
            if isinstance(clst.HOSTS.ID, list):
                cluster_value["host_list"] = clst.HOSTS.ID
                cluster_value["host_count"] = len(clst.HOSTS.ID)
            else:
                cluster_value["host_list"] = [clst.HOSTS.ID]
                cluster_value["host_count"] = 1
            return_value[clst.NAME] = cluster_value

        return return_value