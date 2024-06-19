# Licensed to the StackStorm, Inc ('StackStorm') under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
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

    def get_host(self, cluster):
        """Return a host from the given cluster that's powered on and has the least number of VMs
        :param cluster_name: Name of the cluster to retrieve a host from
        :returns host_obj: Host object from the given cluster
        """
        host_obj = None
        least_vms = None

        for host_id in cluster.HOSTS.ID:
            host = self.one.host.info(host_id)
            # Need to verify that the host is on and connected (STATE 2 = MONITORED)
            # https://docs.opennebula.io/6.8/integration_and_development/references/host_states.html
            if (host.STATE == 2):
                # Find the host that has the least number of VMs on it
                if (least_vms is None or len(host.VMS.ID) < least_vms):
                    host_obj = host
                    least_vms = len(host.VMS.ID)

        if host_obj is not None:
            return host_obj
        else:
            raise Exception("No available hosts found for cluster: {}".format(cluster.NAME))

    def get_storage(self, cluster, datastore_filter_strategy, datastore_filter, disks):
        """Return a datastore on the host that is either specified in the disks variable or
        has the most free space and a name that doesn't match any filters
        :param cluster: Cluster object to retrieve a datastore from
        :param datastore_filter: Object containing list of filtersto exclude certain datastores
          :example: ["string1", "string2"]
        :param disks: Object containing a list of disks to add to the VM
          :example:
            [{
               "size_gb": "string",
               "uuid": "string",
               "datastore": "string",
               "controller_bus": "string",
               "scsi_bus": "string"
            }]
        :returns datastore: Datastore object from the given host
        """
        datastore = None

        # First check the disks variable for a datastore to use
        if disks is not None:
            first_disk = disks[0]
            datastore_name = first_disk['datastore']
            # If the disks variable is given and it's datastore key is not "automatic" then
            # the datastore from the disks variable will be returned
            if datastore_name != "automatic":
                #atastores = self.one.datastorepool.info()
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
        :param ds_name: Name of the datastore to check filters for
        :param datastore_filter: Array containing list of filters to exclude certain datastores
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
            disks, open_nebula=None):
        """
        Returns a host and datastore name and MOID from the given cluster and filters.
        The result host will be the one with the least amount of VMs and the result
        datastore will be the one with the most free space

        Args:
        - cluster_name: Name of the cluster in vSphere to get a host from
        - datastore_filter_regex_list: List of regular expressions to filter the list of datastores
        - disks: List of disks to attach to a new VM
        - open_nebula: Pre-Configured open nebula connection details

        Returns:
        - dict: key value pairs with calculated host and datastore names and ids
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

        # Return a host from the given cluster that's powered on and has the least amount of VMs
        host = self.get_host(cluster)

        # Return a datastore on the host that is either specified in the disks variable or
        # has the most free space and a name that doesn't match any filters
        datastore = self.get_storage(cluster,
                                     datastore_filter_strategy,
                                     datastore_filter_regex_list,
                                     disks)

        return {'clusterName': cluster.NAME,
                'hostName': host.NAME,
                'hostID': host.ID,
                'datastoreName': datastore.NAME,
                'datastoreID': datastore.ID}
