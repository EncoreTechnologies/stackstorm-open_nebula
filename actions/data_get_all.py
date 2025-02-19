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
        # Get snapshots from VM object, default to empty list if not present
        snapshots = vm.get('snapshots', {}).get('snapshot', [])

        # Convert to list if needed
        if isinstance(snapshots, dict):
            snapshots = [snapshots]

        return len(snapshots)

    def update_vm(self, obj):
        # Add capacity of all disks on VM
        disk_space = 0.0
        if 'disk' in obj['template']:
            disk = obj['template']['disk']
            if isinstance(disk, list):
                disk_space = sum(int(disk_item['size']) / 1024 for disk_item in disk)
            else:
                disk_space = int(disk['size']) / 1024

        # Round the disk space and add to obj
        disk_space = round(disk_space, 1)
        obj['template']['disk_space'] = str(disk_space)

        # Get number of snapshots on VM
        snapshot_count = self.get_vm_snapshot_count(obj)
        obj['snapshot_count'] = snapshot_count

        return obj

    def update_datastore(self, obj):
        obj['capacity_gb'] = str(round(int(obj['total_mb']) / 1024, 1))
        return obj

    def update_host(self, obj):
        if 'numa_nodes' in obj['host_share']:
            obj['host_share'].pop('numa_nodes')
        obj['host_share']['cpu_ghz'] = str(round(int(obj['host_share']['total_cpu']) / 1000, 2))
        obj['host_share']['mem_gb'] = str(round(int(obj['host_share']['total_mem']) / 1024**2, 1))
        return obj

    def update_network(self, obj):
        return obj

    def zones_to_csv(self, obj, obj_type):
        # Get template based on obj type if it exists
        if obj_type == 'VM':
            template = obj.get('user_template', None)
        else:
            template = obj.get('template', None)

        # If template exists and has zone attr, update it
        if template and template.get('zone') is not None:
            obj['template']['zone'] = template['zone'].replace(" ", ",")

        return obj

    def update_objects(self, objects, object_type):
        # define update functions
        update_functions = {
            'VM': self.update_vm,
            'DATASTORE': self.update_datastore,
            'HOST': self.update_host,
            'VNET': self.update_network
        }

        # Get correct update function
        update_function = update_functions.get(object_type)

        # Get the update function based on object type
        for i, obj in enumerate(objects):
            # Convert zone names to CSV format
            objects[i] = self.zones_to_csv(obj, object_type)

            if object_type not in update_functions.keys():
                continue

            objects[i] = update_function(objects[i])

        return objects

    def filter_templates(self, templates):
        # If no label filters were passed then return all templates
        if self.template_label_filters and len(self.template_label_filters) > 0:
            label_temps = []
            for temp in templates:
                try:
                    labels = temp['template']['labels']
                    vm_labels = labels.split(',')
                except KeyError:
                    vm_labels = []

                if any(x in vm_labels for x in self.template_label_filters):
                    label_temps.append(temp)
        else:
            label_temps = templates

        return label_temps

    def filter_objects(self, objects, object_type):
        # define filter functions
        filter_functions = {
            'VMTEMPLATE': self.filter_templates
        }

        # Get the filter function based on object type
        if object_type not in filter_functions.keys():
            return objects

        filter_function = filter_functions.get(object_type)
        filtered_objs = filter_function(objects)

        return filtered_objs

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

        # All keys from the API are capitalized by default, so we change them to lowercase here
        lowercase_objects = self.lowercase_keys(objects)

        # filter objects
        filtered_objects = self.filter_objects(lowercase_objects, object_type)

        # update objects
        return_objects = self.update_objects(filtered_objects, object_type)

        return return_objects

    def lowercase_keys(self, obj):
        if isinstance(obj, dict):
            return {key.lower(): self.lowercase_keys(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self.lowercase_keys(item) for item in obj]
        else:
            return obj

    def add_wilds(self, hosts):
        result = []
        for host in hosts:
            # continue to next host if no wilds are found
            if 'vm' not in host['template']:
                continue

            # Convert instances of single wilds to lists
            wilds = host['template']['vm']
            if isinstance(wilds, dict):
                wilds = [wilds]

            # Add all wilds to our list of vm objects
            for wild in wilds:
                result.append(wild['vm_name'])

        return result

    def run(self, api_config, template_label_filters, open_nebula=None):
        self.session = self.xmlrpc_session_create(open_nebula)
        self.template_label_filters = template_label_filters

        all_objs = {}
        for config in api_config:
            objects = self.get_objects(config['endpoint'], config['options'], config['type'])
            all_objs[config['name']] = objects

        # Add wilds from host data to separate object
        all_objs['wilds'] = self.add_wilds(all_objs['hosts'])

        # Add hostname to data
        conn = self._get_connection_info(open_nebula)
        all_objs['hostname'] = conn['host']

        return all_objs
