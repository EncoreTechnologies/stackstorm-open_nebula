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


class DatastoreAttributeGet(BaseAction):
    def run(self, attribute_name, ds_id, open_nebula=None):
        """ Return the value of the given attribute from the datastore
        :returns: Dictionary with results and attribute_not_set lists
        """
        one = self.pyone_session_create(open_nebula)
        ds = one.datastore.info(ds_id)

        if len(attribute_name) == 1:
            return_value = json.loads(json.dumps(getattr(ds, attribute_name[0])))
        else:
            return_value = ds
            # Check the datastore for the given attribute and raise an error if it isn't found
            for attr in attribute_name:
                if hasattr(return_value, attr):
                    return_value = json.loads(json.dumps(getattr(return_value, attr)))
                elif isinstance(return_value, Mapping) and attr in return_value:
                    return_value = return_value[attr]
                else:
                    raise ValueError("Given attribute: {} not found on datastore: {}".format(
                        attr, ds_id))

        return return_value
