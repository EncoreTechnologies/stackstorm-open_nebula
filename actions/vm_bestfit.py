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
import re


class BestFit(BaseAction):

    def __init__(self, config):
        """Creates a new BaseAction given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new BaseAction
        """
        super(BestFit, self).__init__(config)

    def validate_host(self, cluster, host_name):
        for host_id in cluster.HOSTS.ID:
            host = self.one.host.info(host_id)
            if host.NAME == host_name:
                if host.STATE != 2:
                    raise Exception(
                        "Host {} is not available (STATE={}, expected 2/MONITORED)".format(
                            host_name, host.STATE))
                return host
        raise Exception(
            "Host {} not found in cluster {}".format(host_name, cluster.NAME))

    def get_host(self, cluster, exclude_vm_ids=None, host_strategy='vm_count'):
        """Return a host from the given cluster that's powered on and best-fit
        based on the given strategy. Optionally exclude hosts running specific VMs.
        """
        host_obj = None
        best_score = None

        for host_id in cluster.HOSTS.ID:
            host = self.one.host.info(host_id)
            # Need to verify that the host is on and connected (STATE 2 = MONITORED)
            # https://docs.opennebula.io/6.8/integration_and_development/references/host_states.html
            if host.STATE != 2:
                continue

            # Skip hosts running any of the excluded VMs
            if exclude_vm_ids:
                host_vm_ids = host.VMS.ID
                if not isinstance(host_vm_ids, list):
                    host_vm_ids = [host_vm_ids]
                host_vm_ids = [str(vid) for vid in host_vm_ids]
                exclude_ids_str = [str(vid) for vid in exclude_vm_ids]
                if any(vm_id in host_vm_ids for vm_id in exclude_ids_str):
                    continue

            score = self._get_host_score(host, host_strategy)
            if best_score is None or score < best_score:
                host_obj = host
                best_score = score

        if host_obj is not None:
            return host_obj
        else:
            raise Exception("No available hosts found for cluster: {}".format(cluster.NAME))

    def _get_host_score(self, host, strategy):
        """Return a numeric score for the host based on the given strategy.
        Lower score = better fit.
        """
        if strategy == 'cpu':
            cpu_usage = int(host.HOST_SHARE.CPU_USAGE)
            max_cpu = int(host.HOST_SHARE.MAX_CPU)
            return cpu_usage / max_cpu if max_cpu > 0 else float('inf')
        elif strategy == 'memory':
            mem_usage = int(host.HOST_SHARE.MEM_USAGE)
            max_mem = int(host.HOST_SHARE.MAX_MEM)
            return mem_usage / max_mem if max_mem > 0 else float('inf')
        else:
            # Default: vm_count
            return len(host.VMS.ID)

    def get_storage(self, cluster, datastore_filter_strategy, datastore_filter, disks):
        """Return a datastore on the host that is either specified in the disks variable or
        has the most free space and a name that doesn't match any filters
        """
        datastore = None

        # First check the disks variable for a datastore to use
        if disks is not None:
            first_disk = disks[0]
            datastore_name = first_disk['datastore']
            # If the disks variable is given and it's datastore key is not "automatic" then
            # the datastore from the disks variable will be returned
            if datastore_name != "automatic":
                for ds_id in cluster.DATASTORES.ID:
                    ds = self.one.datastore.info(ds_id)
                    if ds.NAME == datastore_name:
                        datastore = ds
                        break

        # If the disks variable is empty or the datastore is set to "automatic" then search
        # the available datastores on the host for the one with the most free space
        if datastore is None:
            most_space = 0
            for ds_id in cluster.DATASTORES.ID:
                ds = self.one.datastore.info(ds_id)
                # only allow placing onto a datastore in "ON" mode (STATE 0)
                if ds.STATE != 0:
                    continue

                # The following function returns False if the name of the datastore
                # matches any of the regex filters
                if self.filter_datastores(ds.NAME, datastore_filter_strategy, datastore_filter):
                    if ds.FREE_MB > most_space:
                        datastore = ds
                        most_space = ds.FREE_MB

        return datastore

    def filter_datastores(self, ds_name, datastore_filter_strategy, datastore_filter_regex_list):
        """Check if a datastore should be filtered from the list or not.
        If no regex filters are given then all datastores can be used
        :returns boolean: True if the datastore name does NOT match any of the regex expressions
        """
        if datastore_filter_regex_list is None:
            return True

        filter_return = False
        default_return = True
        if datastore_filter_strategy == 'include_matches':
            filter_return = True
            default_return = False

        for regex in datastore_filter_regex_list:
            if re.search(regex.strip(), ds_name):
                return filter_return

        return default_return

    def run(self, cluster_name, datastore_filter_strategy, datastore_filter_regex_list,
            disks, exclude_vm_ids=None, host_strategy='vm_count', host_name=None,
            open_nebula=None):
        """
        Returns a host and datastore name and ID from the given cluster and filters.
        The result host will be selected based on the given strategy and the result
        datastore will be the one with the most free space.
        """
        # Create pyone session
        self.one = self.pyone_session_create(open_nebula)

        clusters = self.one.clusterpool.info()

        cluster = None
        for clst in clusters.CLUSTER:
            if clst.NAME == cluster_name:
                cluster = clst
                break

        if not cluster:
            raise Exception('No cluster found with the given name: ' + cluster_name)

        if host_name:
            host = self.validate_host(cluster, host_name)
        else:
            host = self.get_host(cluster, exclude_vm_ids, host_strategy)

        # Calculate host usage percentage for the selected strategy
        host_usage_percent = round(self._get_host_score(host, host_strategy) * 100, 2)

        # Return a datastore on the host that is either specified in the disks variable or
        # has the most free space and a name that doesn't match any filters
        datastore = self.get_storage(cluster,
                                     datastore_filter_strategy,
                                     datastore_filter_regex_list,
                                     disks)

        return {'clusterName': cluster.NAME,
                'hostName': host.NAME,
                'hostID': host.ID,
                'hostUsagePercent': host_usage_percent,
                'datastoreName': datastore.NAME,
                'datastoreID': datastore.ID}
