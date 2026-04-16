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


class TemplateImageDatastoreGet(BaseAction):
    def datastore_id_get(self, datastore_name, one_session):
        response = one_session.one.datastorepool.info(self.auth_string, *tuple([-2, -1, -1, -1]))

        # Check the result for an error (first element will be FALSE on error)
        if response[0]:
            datastore_pool = json.loads(xmltojson.parse(response[1]))
            datastores = datastore_pool['DATASTORE_POOL']['DATASTORE']
            # If only one object is found then it will be returned as a single object and not a list
            if type(datastores) is dict:
                datastores = [datastores]
        else:
            raise Exception(response[1])

        for ds in datastores:
            if ds['NAME'] == datastore_name:
                return int(ds['ID'])

        raise ValueError("No datastore found with name {}".format(datastore_name))

    def run(self, template_id, open_nebula=None):
        """ Retrieves the images on a template and returns the datastore(s) they are on
        :returns: List of datastores for the images on the given Template or empty list if none found
        """
        one_session = self.xmlrpc_session_create(open_nebula)
        response = one_session.one.template.info(self.auth_string, *tuple([template_id]))

        # Check the result for an error (first element will be FALSE on error)
        if response[0]:
            template = json.loads(xmltojson.parse(response[1]))
            template = template['VMTEMPLATE']['TEMPLATE']
        else:
            raise Exception(response[1])

        if not 'DISK' in template or template['DISK'] is None or len(template['DISK']) == 0:
            raise ValueError("No disks found on template {}".format(template_id))

        disks = template['DISK']
        # If only one object is found then it will be returned as a single object and not a list
        if type(disks) is dict:
            disks = [disks]

        # Create list of only IDs for the images on the template
        disks = [int(d['IMAGE_ID']) for d in disks if 'IMAGE_ID' in d and d['IMAGE_ID'] != -1]
        datastore_disk_hash = {}
        for disk_id in disks:
            disk_info = one_session.one.image.info(self.auth_string, *tuple([disk_id]))
            # Check the result for an error (first element will be FALSE on error)
            if disk_info[0]:
                disk_info = json.loads(xmltojson.parse(disk_info[1]))
                if 'IMAGE' in disk_info and 'DATASTORE' in disk_info['IMAGE']:
                    datastore_name = disk_info['IMAGE']['DATASTORE']
                    if datastore_name not in datastore_disk_hash:
                        #datastore_disk_hash[datastore_name] = []
                        datastore_disk_hash[datastore_name] = {
                            'datastore_id': self.datastore_id_get(datastore_name, one_session),
                            'disk_ids': []
                        }
                    datastore_disk_hash[datastore_name]['disk_ids'].append(disk_id)
            else:
                raise Exception(disk_info[1])

        return datastore_disk_hash
