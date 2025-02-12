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
from collections.abc import Mapping
import json


class DatastoresAttributeGet(BaseAction):
    def run(self, attribute_name, ds_ids, open_nebula=None):
        """ Return the value of the given attribute from the datastores
        :returns: Dictionary with results and attribute_not_set lists
        """
        results = []
        attribute_not_set = []

        one = self.pyone_session_create(open_nebula)

        for ds_id in ds_ids:
            datastore = one.datastore.info(ds_id)
            return_value = datastore
            attribute_found = True

            for attr in attribute_name:
                if hasattr(return_value, attr):
                    return_value = json.loads(json.dumps(getattr(return_value, attr)))
                elif isinstance(return_value, Mapping) and attr in return_value:
                    return_value = return_value[attr]
                else:
                    attribute_found = False
                    break

            if attribute_found:
                results.append({
                    'ds_id': ds_id,
                    'ds_name': datastore.NAME,
                    attribute_name[-1]: return_value
                })
            else:
                attribute_not_set.append({
                    'ds_id': ds_id,
                    'ds_name': datastore.NAME
                })

        return {
            'ds_with_attribute': results,
            'attribute_not_set': attribute_not_set
        }
