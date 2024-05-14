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

import json
from datetime import datetime, timedelta, timezone
from lib.action_base import BaseAction

class VmSnapshotsDeleteAge(BaseAction):
    # Compare the snapshot timestamp with now - age
    def delete_check(self, utc_timestamp, age_days):
        snap_date = datetime.fromtimestamp(utc_timestamp, timezone.utc)
        remove_age = datetime.now(timezone.utc) - timedelta(age_days)
        if remove_age > snap_date:
            return True
        else:
            return False

    def remove_snapshots(self, one, vm_id, age_days):
        vm = one.vm.info(vm_id)
        template_info = json.loads(json.dumps(vm.TEMPLATE))
        result = {}
        if 'SNAPSHOT' in template_info:
            snapshots = template_info['SNAPSHOT']
            deleted_snaps = []
            for snap in snapshots:
                if self.delete_check(int(snap['TIME']), age_days):
                    one.vm.snapshotdelete(vm_id, int(snap['ID']))
                    deleted_snaps.append(snap['NAME'])
                    result[vm.NAME] = deleted_snaps
        
        return result

    def run(self, snapshot_age_days, vm_id, open_nebula=None):
        """ Delete snapshots older than a given age
        :returns: Dict of removed snapshots {'vmid': 'snap name'}
        """
        one = self.pyone_session_create(open_nebula)

        if vm_id:
            result = self.remove_snapshots(one, vm_id, snapshot_age_days)
        else:
            vm_ids = self.get_all_vm_ids(one)
            result = {}
            # The snapshotes aren't found in the VMPool info so need
            # to check each VM individually
            for id in vm_ids:
                removed = self.remove_snapshots(one, id, snapshot_age_days)
                result.update(removed)

        return {'deleted_snaps': result}
