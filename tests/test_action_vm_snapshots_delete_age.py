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
from one_base_action_test_case import OneBaseActionTestCase
import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta, timezone
from vm_snapshots_delete_age import VmSnapshotsDeleteAge

__all__ = [
    'VmSnapshotsDeleteAgeTestCase'
]


class VmSnapshotsDeleteAgeTestCase(OneBaseActionTestCase):
    __test__ = True
    action_cls = VmSnapshotsDeleteAge

    def test_delete_check_true(self):
        # Arrange
        utc_timestamp = (datetime.now(timezone.utc) - timedelta(days=10)).timestamp()
        age_days = 5

        # Act
        result = self.action.delete_check(utc_timestamp, age_days)

        # Assert
        self.assertTrue(result)

    def test_delete_check_false(self):
        # Arrange
        utc_timestamp = (datetime.now(timezone.utc) - timedelta(days=3)).timestamp()
        age_days = 5

        # Act
        result = self.action.delete_check(utc_timestamp, age_days)

        # Assert
        self.assertFalse(result)

    @patch('vm_snapshots_delete_age.VmSnapshotsDeleteAge.pyone_session_create')
    @patch('vm_snapshots_delete_age.VmSnapshotsDeleteAge.remove_snapshots')
    def test_run_with_vm_id(self, mock_remove_snapshots, mock_pyone_session_create):
        # Arrange
        snapshot_age_days = 5
        vm_id = 1
        open_nebula = 'open_nebula'

        mock_pyone_session_create.return_value = MagicMock()
        mock_remove_snapshots.return_value = {'vm1': ['snap1']}

        # Act
        result = self.action.run(snapshot_age_days, vm_id, open_nebula)

        # Assert
        self.assertEqual(result, {'deleted_snaps': {'vm1': ['snap1']}})
        mock_pyone_session_create.assert_called_once_with(open_nebula)
        mock_remove_snapshots.assert_called_once_with(mock_pyone_session_create.return_value, vm_id, snapshot_age_days)

    @patch('vm_snapshots_delete_age.VmSnapshotsDeleteAge.pyone_session_create')
    @patch('vm_snapshots_delete_age.VmSnapshotsDeleteAge.get_all_vm_ids')
    @patch('vm_snapshots_delete_age.VmSnapshotsDeleteAge.remove_snapshots')
    def test_run_without_vm_id(self, mock_remove_snapshots, mock_get_all_vm_ids, mock_pyone_session_create):
        # Arrange
        snapshot_age_days = 5
        vm_id = None
        open_nebula = 'open_nebula'

        mock_pyone_session_create.return_value = MagicMock()
        mock_get_all_vm_ids.return_value = [1, 2]
        mock_remove_snapshots.side_effect = [{'vm1': ['snap1']}, {'vm2': ['snap2']}]

        # Act
        result = self.action.run(snapshot_age_days, vm_id, open_nebula)

        # Assert
        self.assertEqual(result, {'deleted_snaps': {'vm1': ['snap1'], 'vm2': ['snap2']}})
        mock_pyone_session_create.assert_called_once_with(open_nebula)
        mock_get_all_vm_ids.assert_called_once_with(mock_pyone_session_create.return_value)
        self.assertEqual(mock_remove_snapshots.call_count, 2)

    def test_remove_snapshots(self):
        # Arrange
        vm_id = 1
        age_days = 5

        vm = MagicMock()
        vm.NAME = 'vm1'
        vm.TEMPLATE = {
            'SNAPSHOT': [
                {'TIME': (datetime.now(timezone.utc) - timedelta(days=10)).timestamp(), 'ID': 1, 'NAME': 'snap1'},
                {'TIME': (datetime.now(timezone.utc) - timedelta(days=3)).timestamp(), 'ID': 2, 'NAME': 'snap2'}
            ]
        }
        self.action.one = MagicMock()
        self.action.one.vm.info.return_value = vm

        # Act
        result = self.action.remove_snapshots(self.action.one, vm_id, age_days)

        # Assert
        self.assertEqual(result, {'vm1': ['snap1']})
        self.action.one.vm.snapshotdelete.assert_called_once_with(vm_id, 1)

if __name__ == '__main__':
    unittest.main()
