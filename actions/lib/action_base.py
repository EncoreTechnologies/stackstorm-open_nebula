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
import requests
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
                _create_unverified_https_context = ssl._create_unverified_context
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

    def session_create(self, open_nebula):
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
        for attr,value in vm.USER_TEMPLATE.items():
            if attr == 'LABELS':
                labels = value.split(',')
        return labels

    def run(self, **kwargs):
        raise RuntimeError("run() not implemented")
