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

from st2common.runners.base_action import Action
from collections import OrderedDict
import requests
import time
import ssl
import pyone
import xmlrpc

CONNECTION_ITEMS = ['host', 'port', 'user', 'passwd']


class BaseAction(Action):
    def __init__(self, config):
        """Creates a new BaseAction given a StackStorm config object (kwargs works too)
        :param config: StackStorm configuration object for the pack
        :returns: a new BaseAction
        """
        super(BaseAction, self).__init__(config)
        if config is None:
            raise ValueError("No connection configuration details found")
        if "open_nebula" in config:
            if config['open_nebula'] is None:
                raise ValueError("'open_nebula' config defined but empty.")
            else:
                pass
        else:
            raise ValueError("No connection configuration details found")

        self.ssl_verify = config.get('ssl_verify', None)
        if self.ssl_verify is False:
            # Don't print out ssl warnings
            requests.packages.urllib3.disable_warnings()  # pylint: disable=no-member

            try:
                _create_unverified_https_context = ssl._create_unverified_context()
            except AttributeError:
                pass
            else:
                ssl._create_default_https_context = _create_unverified_https_context

    def _get_connection_info(self, open_nebula=None):
        if open_nebula:
            connection = self.config['open_nebula'].get(open_nebula)
        else:
            connection = self.config['open_nebula'].get('default')

        for item in CONNECTION_ITEMS:
            if item in connection:
                pass
            else:
                raise KeyError("open_nebula.yaml Mising: open_nebula:%s:%s"
                               % (open_nebula, item))

        return connection

    def pyone_session_create(self, open_nebula):
        conn = self._get_connection_info(open_nebula)
        # Create a connection to the server:
        session = pyone.OneServer("http://{}:{}/RPC2".format(conn['host'], conn['port']),
                                  session="{}:{}".format(conn['user'], conn['passwd']))

        return session

    def xmlrpc_session_create(self, open_nebula):
        conn = self._get_connection_info(open_nebula)
        # Create a connection to the server
        client = xmlrpc.client.ServerProxy("http://{}:{}".format(conn['host'], conn['port']))
        self.auth_string = "{}:{}".format(conn['user'], conn['passwd'])

        return client

    # Search for and return a list of labels on the given VM or an empty list
    def vm_labels_get(self, vm):
        labels = []
        # Labels are found in the USER_TEMPLATE field of the VM
        for attr, value in vm.USER_TEMPLATE.items():
            if attr == 'LABELS':
                labels = value.split(',')
        return labels

    # Return all disks associated with the given template
    def template_disks_get(self, template):
        disks = template.TEMPLATE['DISK']
        if isinstance(disks, (dict, OrderedDict)):
            disks = [disks]

        result = [dict(disk) for disk in disks]

        return result

    def get_all_vm_ids(self, one):
        # List of options to pass into the info function
        # https://docs.opennebula.io/6.6/integration_and_development/system_interfaces/api.html#one-vmpool-info
        vms = one.vmpool.info(-2, -1, -1, -1).VM
        vm_ids = [int(vm.ID) for vm in vms]
        vm_ids.sort()

        return vm_ids

    def wait_for_vm(self, one, vm_id, timeout=30):
        # Wait for VM to enter LCM State of 3 = 'running'
        lcm_state = one.vm.info(vm_id).LCM_STATE
        start_time = time.time()
        while lcm_state != 3:
            # Set elapsed time for timeout check
            elapsed_time = time.time() - start_time
            if elapsed_time > timeout:
                return lcm_state

            # Wait before checking again
            time.sleep(5)

            # Update the image state for next check
            lcm_state = one.vm.info(vm_id).LCM_STATE

        return lcm_state

    def run(self, **kwargs):
        raise RuntimeError("run() not implemented")
