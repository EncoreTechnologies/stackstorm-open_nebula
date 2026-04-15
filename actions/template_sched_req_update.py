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
from dict2xml import dict2xml
import json


class TemplateSchedReqUpdate(BaseAction):
    def replace_datastore_ids(self, sched_ds_reqs, one):
        # Check if datastore ID is already in SCHED_REQUIREMENTS and if so, change it to datastore_name
        new_reqs = []
        cluster_id = None
        replaced = False
        for req in sched_ds_reqs:
            # Make sure it's a datastore ID and not a cluster ID
            if 'ID' in req and 'CLUSTER_ID' not in req:
                # Check for parentheses and remove them if found
                if req.startswith("("):
                    req = req[1:]
                if req.endswith(")"):
                    req = req[:-1]
                # Check if multiple datastore requirements exist (e.g. ID=1|ID=2)
                or_reqs = req.split("|")
                or_reqs = [s.strip() for s in or_reqs]
                new_or_reqs = []
                for or_req in or_reqs:
                    if 'ID' in or_req:
                        ds_id = or_req.split("=", 1)[1].strip().replace('"', '').replace("'", '')
                        # Get datastore name from datastore ID and replace in requirement
                        ds_name = one.datastore.info(int(ds_id)).NAME
                        new_or_reqs.append('NAME = "' + ds_name + '"')
                # If multiple datastore requirements were found, join them with OR and add parentheses if needed
                if len(new_or_reqs) > 1:
                    new_reqs.append("(" + " | ".join(new_or_reqs) + ")")
                else:
                    new_reqs.append(new_or_reqs[0])
                replaced = True
            else:
                new_reqs.append(req)

        return new_reqs, replaced

    def replace_host_ids(self, sched_reqs, one):
        # Check if host ID is already in SCHED_REQUIREMENTS and if so, change it to host_name
        new_reqs = []
        cluster_id = None
        replaced = False
        for req in sched_reqs:
            # Make sure it's a host ID and not a cluster ID
            if 'ID' in req and 'CLUSTER_ID' not in req:
                # Check for parentheses and remove them if found
                if req.startswith("("):
                    req = req[1:]
                if req.endswith(")"):
                    req = req[:-1]
                # Check if multiple host requirements exist (e.g. ID=1|ID=2)
                or_reqs = req.split("|")
                or_reqs = [s.strip() for s in or_reqs]
                new_or_reqs = []
                for or_req in or_reqs:
                    if 'ID' in or_req:
                        host_id = or_req.split("=", 1)[1].strip().replace('"', '').replace("'", '')
                        # Get host name from host ID and replace in requirement
                        host_name = one.host.info(int(host_id)).NAME
                        new_or_reqs.append('NAME = "' + host_name + '"')
                # If multiple host requirements were found, join them with OR and add parentheses if needed
                if len(new_or_reqs) > 1:
                    new_reqs.append("(" + " | ".join(new_or_reqs) + ")")
                else:
                    new_reqs.append(new_or_reqs[0])
                replaced = True
            else:
                new_reqs.append(req)

        return new_reqs, replaced

    def replace_cluster_ids(self, sched_reqs, one):
        # Check if cluster ID is already in SCHED_REQUIREMENTS and if so, change it to cluster_name
        new_reqs = []
        cluster_id = None
        replaced = False
        for req in sched_reqs:
            if 'CLUSTER_ID' in req:
                # Check for parentheses and remove them if found
                if req.startswith("("):
                    req = req[1:]
                if req.endswith(")"):
                    req = req[:-1]
                # Check if multiple cluster requirements exist (e.g. CLUSTER_ID=1|CLUSTER_ID=2)
                or_reqs = req.split("|")
                or_reqs = [s.strip() for s in or_reqs]
                new_or_reqs = []
                for or_req in or_reqs:
                    if 'CLUSTER_ID' in or_req:
                        cluster_id = or_req.split("=", 1)[1].strip().replace('"', '').replace("'", '')
                        # Get cluster name from cluster ID and replace in requirement
                        cluster_name = one.cluster.info(int(cluster_id)).NAME
                        new_or_reqs.append('CLUSTER = "' + cluster_name + '"')
                # If multiple cluster requirements were found, join them with OR and add parentheses if needed
                if len(new_or_reqs) > 1:
                    new_reqs.append("(" + " | ".join(new_or_reqs) + ")")
                else:
                    new_reqs.append(new_or_reqs[0])
                replaced = True
            else:
                new_reqs.append(req)

        return new_reqs, replaced

    def run(self, cluster_name, datastore_name, host_name, noop, template_id,
            template_name, open_nebula=None):
        """ Updates the SCHED_REQUIREMENTS and/or SCHED_DS_REQUIREMENTS of Open Nebula templates
        :returns: Template information with name and ID appended
        """
        result = {
            'messages': '',
            'sched_requirements_old': '',
            'sched_requirements_new': '',
            'sched_ds_requirements_old': '',
            'sched_ds_requirements_new': ''
        }
        # Check that either template_id or template_name is provided
        # If both are provided, template_id will be used and template_name will be ignored
        if not template_id and not template_name:
            raise Exception("ERROR: Either template_id or template_name must be provided.")
        elif template_id:
            filter_type = "ID"
        elif template_name:
            filter_type = "NAME"

        one = self.pyone_session_create(open_nebula)

        # More info on these params can be found here:
        # https://docs.opennebula.io/6.8/integration_and_development/system_interfaces/api.html#one-templatepool-info
        temppoolInfo = one.templatepool.info(-2, -1, -1, -1)
        temps = temppoolInfo.VMTEMPLATE

        temp_obj = None
        for temp in temps:
            if getattr(temp, filter_type) == (template_id if filter_type == "ID" else template_name):
                temp_obj = temp.TEMPLATE
                temp_obj['ID'] = temp.ID
                temp_obj['NAME'] = temp.NAME
                break

        if not temp_obj:
            raise Exception("ERROR: No templates found with " + filter_type + ": " + (str(template_id) if filter_type == "ID" else template_name))

        # Check for existing SCHED_REQUIREMENTS and split into list if found
        sched_reqs = []
        if 'SCHED_REQUIREMENTS' in temp_obj:
            result['sched_requirements_old'] = temp_obj['SCHED_REQUIREMENTS']
            sched_reqs = temp_obj['SCHED_REQUIREMENTS'].split("&")
            sched_reqs = [s.strip() for s in sched_reqs]

        # Check if cluster ID is already in SCHED_REQUIREMENTS and if so, change it to cluster_name
        sched_reqs, replaced = self.replace_cluster_ids(sched_reqs, one)
        if replaced:
            result['messages'] += "Cluster IDs were found and replaced with cluster names. "

        # After cluster IDs are replaced, check if cluster_name is already in SCHED_REQUIREMENTS and add or replace it
        if cluster_name:
            cluster_req = 'CLUSTER = "' + cluster_name + '"'
            # Check if cluster requirements need to be replaced
            for s in sched_reqs:
                if "CLUSTER" in s:
                    if cluster_name not in s:
                        result['messages'] += "Cluster requirement replaced with '" + cluster_req + "'. "
                        sched_reqs.remove(s)
                        sched_reqs.append(cluster_req)

        # Check if cluster ID is already in SCHED_REQUIREMENTS and if so, change it to cluster_name
        sched_reqs, replaced = self.replace_host_ids(sched_reqs, one)
        if replaced:
            result['messages'] += "Host IDs were found and replaced with host names. "

        # After host IDs are replaced, check if host_name is already in SCHED_REQUIREMENTS and add or replace it
        if host_name:
            host_req = 'NAME = "' + host_name + '"'
            # Check if host requirements need to be replaced
            for s in sched_reqs:
                if "NAME" in s:
                    if host_name not in s:
                        result['messages'] += "Host requirement replaced with '" + host_req + "'. "
                        sched_reqs.remove(s)
                        sched_reqs.append(host_req)

        result['sched_requirements_new'] = ' & '.join(sched_reqs)

        # Check for existing SCHED_DS_REQUIREMENTS and split into list if found
        sched_ds_reqs = []
        if 'SCHED_DS_REQUIREMENTS' in temp_obj:
            result['sched_ds_requirements_old'] = temp_obj['SCHED_DS_REQUIREMENTS']
            sched_ds_reqs = temp_obj['SCHED_DS_REQUIREMENTS'].split("&")
            sched_ds_reqs = [s.strip() for s in sched_ds_reqs]

        # Check if datastore ID is already in SCHED_DS_REQUIREMENTS and if so, change it to datastore_name
        sched_ds_reqs, replaced = self.replace_datastore_ids(sched_ds_reqs, one)
        if replaced:
            result['messages'] += "Datastore IDs were found and replaced with datastore names. "

        # After datastore IDs are replaced, check if datastore_name is already in SCHED_DS_REQUIREMENTS and add or replace it
        if datastore_name:
            datastore_req = 'NAME = "' + datastore_name + '"'
            # Check if datastore requirements need to be replaced
            for s in sched_ds_reqs:
                if "NAME" in s:
                    if datastore_name not in s:
                        result['messages'] += "Datastore requirement replaced with '" + datastore_req + "'. "
                        sched_ds_reqs.remove(s)
                        sched_ds_reqs.append(datastore_req)

        result['sched_ds_requirements_new'] = ' & '.join(sched_ds_reqs)

        # Update the template with the new SCHED_REQUIREMENTS
        xml = dict2xml({'TEMPLATE': {
            'SCHED_REQUIREMENTS': ' &amp; '.join(sched_reqs),
            'SCHED_DS_REQUIREMENTS': ' &amp; '.join(sched_ds_reqs)
        }})
        # The 1 below merges this new template with the existing one
        if not noop:
            one.template.update(temp_obj['ID'], xml, 1)
        
        # Update result message
        if not result['messages']:
            result['messages'] = "No updates needed for SCHED REQUIREMENTS."
        elif noop:
            result['messages'] = "NOOP enabled, the following updates would be made: " + result['messages']
        else:
            result['messages'] = "SCHED REQUIREMENTS updated successfully. " + result['messages']

        return result
