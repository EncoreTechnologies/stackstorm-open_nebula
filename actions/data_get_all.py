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

class DataGetAll(BaseAction):

    def get_vm_snapshot_count(self, vm):
        template_info = json.loads(json.dumps(vm['template']))

        snapshot_count = 0
        if 'snapshot' in template_info:
            snapshot_count = len(template_info['snapshot'])

        return str(snapshot_count)

    def filter_vm(self, obj):
        mem_gb = 0.0
        if 'disk' in obj['template']:
            if isinstance(obj['template']['disk'], list):
                for disk in obj['template']['disk']:
                    mem_gb += round(int(disk['size']) / 1024, 1)
                mem_gb = round(mem_gb, 1)
            else:
                mem_gb = round(int(obj['template']['disk']['size']) / 1024, 1)
        obj['template']['mem_gb'] = str(mem_gb)

        snapshot_count = self.get_vm_snapshot_count(obj)
        obj['snapshot_count'] = snapshot_count

        return obj

    def filter_datastore(self, obj):
        obj['capacity_gb'] = str(round(int(obj['total_mb']) / 1024, 1))
        return obj

    def filter_host(self, obj):
        if 'numa_nodes' in obj['host_share']:
            obj['host_share'].pop('numa_nodes')
        obj['host_share']['cpu_ghz'] = str(round(int(obj['host_share']['total_cpu']) / 1000, 2))
        obj['host_share']['mem_gb'] = str(round(int(obj['host_share']['total_mem']) / 1024**2, 1))
        return obj

    def filter_network(self, obj):
        return obj

    def filter_objects(self, objects, object_type):
        # define filter functions
        filter_functions = {
            'VM': self.filter_vm,
            'DATASTORE': self.filter_datastore,
            'HOST': self.filter_host,
            'VNET': self.filter_network
        }

        # Get the filter function based on object type
        for obj in objects:
            if object_type == 'CLUSTER':
                continue

            filter_function = filter_functions.get(object_type)
            obj = filter_function(obj)

        return objects

    def get_objects(self, endpoint, object_options, object_type):
        method = getattr(self.session, endpoint)
        response = method(self.auth_string, *tuple(object_options))

        # Check the result for an error (first element will be FALSE on error)
        if response[0]:
            object_pool = json.loads(xmltojson.parse(response[1]))
            objects = object_pool[object_type + '_POOL'][object_type]
            # If only one object is found then it will be returned as a single object and not a list
            if type(objects) is dict:
                objects = [objects]
        else:
            raise Exception(response[1])

        # All  keys from the API are capitalized by default, so we change them to lowercase here
        lowercase_objects = self.lowercase_keys(objects)

        # filter objects
        return_objects = self.filter_objects(lowercase_objects, object_type)

        return return_objects

    def lowercase_keys(self, obj):
        if isinstance(obj, dict):
            return {key.lower(): self.lowercase_keys(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self.lowercase_keys(item) for item in obj]
        else:
            return obj

    def run(self, api_config, open_nebula=None):
        self.session = self.xmlrpc_session_create(open_nebula)

        all_objs = {}
        for config in api_config:
            objects = self.get_objects(config['endpoint'], config['options'], config['type'])
            all_objs[config['name']] = objects
        
        return json.dumps(all_objs, sort_keys=True, indent=4, default=str)
