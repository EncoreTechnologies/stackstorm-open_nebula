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

class ObjectsGet(BaseAction):
    
    def run(self, api_endpoint, object_ids, object_options, object_type, open_nebula=None):
        xmlrpc_session = self.xmlrpc_session_create(open_nebula)

        # Run the given method with the auth string generated from the config
        method = getattr(xmlrpc_session, api_endpoint)
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
        
        if object_ids:
            result = []
            # Convert any integers to be compared with the string response
            object_ids = [str(id) for id in object_ids]
            for obj in objects:
                if obj['ID'] in object_ids:
                    result.append(obj)
                    object_ids.remove(obj['ID'])
            if object_ids:
                obj_str = ','.join(object_ids)
                raise Exception('No objects found with the given ID: ' + obj_str)
        else:
            result = objects

        return result