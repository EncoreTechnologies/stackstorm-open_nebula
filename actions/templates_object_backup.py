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
import os
import datetime


class TemplatesObjectBackup(BaseAction):
    def run(self, backup_dir, template_ids, open_nebula=None):
        """ Saves a copy of all or a subset of templates to the backup directory in this pack's actions folder
        :returns: List of backed up template IDs
        """
        # Create backup directory if it doesn't exist
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        one_session = self.xmlrpc_session_create(open_nebula)
        response = one_session.one.templatepool.info(self.auth_string, *tuple([-2, -1, -1, -1]))

        # Check the result for an error (first element will be FALSE on error)
        if response[0]:
            template_pool = json.loads(xmltojson.parse(response[1]))
            templates = template_pool['VMTEMPLATE_POOL']['VMTEMPLATE']
            # If only one object is found then it will be returned as a single object and not a list
            if type(templates) is dict:
                templates = [templates]
        else:
            raise Exception(response[1])

        backup_temps = []
        for temp in templates:
            if template_ids and len(template_ids) > 0:
                if int(temp['ID']) not in template_ids:
                    continue
            
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
            file_path = backup_dir + "/" + temp['NAME'] + "_" + str(temp['ID']) + "_" + timestamp + ".json"
            backup_temps.append(file_path)
            with open(file_path, "w") as f:
                json.dump(temp, f, indent=4)

        return backup_temps
