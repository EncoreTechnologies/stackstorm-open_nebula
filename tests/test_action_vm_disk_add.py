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
from vm_disk_add import VmDiskAdd

__all__ = [
    'VmDiskAddTestCase'
]


class VmDiskAddTestCase(OneBaseActionTestCase):
    __test__ = True
    action_cls = VmDiskAdd

    def test_get_template(self):
        # Arrange
        template_id = 1
        self.action.one = MagicMock()
        self.action.one.templatepool.info.return_value = MagicMock(VMTEMPLATE=[MagicMock()])

        # Act
        result = self.action.get_template(template_id)

        # Assert
        self.assertIsNotNone(result)
        self.action.one.templatepool.info.assert_called_once_with(-2, template_id, template_id)

    def test_get_template_not_found(self):
        # Arrange
        template_id = 1
        self.action.one = MagicMock()
        self.action.one.templatepool.info.return_value = MagicMock(VMTEMPLATE=[])

        # Act & Assert
        with self.assertRaises(Exception) as context:
            self.action.get_template(template_id)
        
        self.assertTrue('Could not find template with id' in str(context.exception))

    def test_get_vm(self):
        # Arrange
        vm_name = 'test_vm'
        self.action.one = MagicMock()
        self.action.one.vmpool.infoextended.return_value = MagicMock(VM=[MagicMock()])

        # Act
        result = self.action.get_vm(vm_name)

        # Assert
        self.assertIsNotNone(result)
        self.action.one.vmpool.infoextended.assert_called_once_with(-2, -1, -1, -1, "VM.NAME={}".format(vm_name))

    def test_get_vm_not_found(self):
        # Arrange
        vm_name = 'test_vm'
        self.action.one = MagicMock()
        self.action.one.vmpool.infoextended.return_value = MagicMock(VM=[])

        # Act & Assert
        with self.assertRaises(Exception) as context:
            self.action.get_vm(vm_name)
        
        self.assertTrue('Could not find VM with name' in str(context.exception))

    def test_get_datastore_id(self):
        # Arrange
        datastore_name = 'test_datastore'
        self.action.one = MagicMock()
        self.action.one.datastorepool.info.return_value = MagicMock(DATASTORE=[MagicMock(NAME='test_datastore', ID=1)])

        # Act
        result = self.action.get_datastore_id(datastore_name)

        # Assert
        self.assertEqual(result, 1)
        self.action.one.datastorepool.info.assert_called_once()

    def test_get_datastore_none(self):
        # Arrange
        datastore_name = 'test_datastore'
        self.action.one = MagicMock()
        self.action.one.datastorepool.info.return_value = MagicMock(DATASTORE=[])

        # Act & Assert
        with self.assertRaises(Exception) as context:
            self.action.get_datastore_id(datastore_name)

        self.assertTrue('No datastores found' in str(context.exception))

    def test_get_datastore_id_not_found(self):
        # Arrange
        datastore_name = 'does_not_exist'
        self.action.one = MagicMock()
        self.action.one.datastorepool.info.return_value = MagicMock(DATASTORE=[MagicMock(NAME='test_datastore', ID=1)])

        # Act & Assert
        with self.assertRaises(Exception) as context:
            self.action.get_datastore_id(datastore_name)

        self.assertTrue('Could not find datastore with name' in str(context.exception))

    @patch('time.sleep', return_value=None)
    def test_allocate_image(self, mock_sleep):
        # Arrange
        disk_name = 'test_disk'
        disk_description = 'test_description'
        disk_type = 'test_type'
        disk_size_gb = 10
        disk_format = 'test_format'
        datastore_id = 1
        disk_check_timeout = 10

        mock_sleep.return_value = None
        self.action.one = MagicMock()
        self.action.one.image.allocate.return_value = 1
        self.action.one.image.info.return_value = MagicMock(STATE=1)

        # Act
        result = self.action.allocate_image(disk_name, disk_description, disk_type, disk_size_gb,
                                            disk_format, datastore_id, disk_check_timeout)

        # Assert
        self.assertEqual(result, 1)
        self.action.one.image.allocate.assert_called_once()
        self.action.one.image.info.assert_called()

    @patch('time.sleep', return_value=None)
    def test_allocate_image_timeout(self, mock_sleep):
        # Arrange
        disk_name = 'test_disk'
        disk_description = 'test_description'
        disk_type = 'test_type'
        disk_size_gb = 10
        disk_format = 'test_format'
        datastore_id = 1
        disk_check_timeout = 1

        mock_sleep.return_value = None
        self.action.one = MagicMock()
        self.action.one.image.allocate.return_value = 1
        self.action.one.image.info.return_value = MagicMock(STATE=0)

        # Act & Assert
        with self.assertRaises(Exception) as context:
            self.action.allocate_image(disk_name, disk_description, disk_type, disk_size_gb,
                                       disk_format, datastore_id, disk_check_timeout)
        
        self.assertTrue('Timed out waiting for disk to enter a ready state' in str(context.exception))

    def test_attach_disk(self):
        # Arrange
        vm_id = 1
        image_id = 1
        disk_format = 'test_format'

        self.action.one = MagicMock()
        self.action.one.vm.attach.return_value = True

        # Act
        result = self.action.attach_disk(vm_id, image_id, disk_format)

        # Assert
        self.assertTrue(result)
        self.action.one.vm.attach.assert_called_once()

    @patch('vm_disk_add.VmDiskAdd.template_disks_get')
    def test_update_template_linux(self, mock_disks_get):
        # Arrange
        template = MagicMock(ID=1)
        image_id = 1
        os_type = 'linux'

        mock_disks_get.return_value = [{'key1': 'value1', 'key2': 'value2'}]
        expected_result = 'result'
        self.action.one = MagicMock()
        self.action.one.template.update.return_value = expected_result

        # Act
        result = self.action.update_template(template, image_id, os_type)

        # Assert
        self.assertEqual(result, expected_result)
        expected_attributes = (
            "DISK = [ key1 = value1 , key2 = value2 ]\n"
            "DISK = [ IMAGE_ID = 1 ]"
        )
        mock_disks_get.assert_called_once_with(template)
        self.action.one.template.update.assert_called_once_with(template.ID, expected_attributes, 1)

    @patch('vm_disk_add.VmDiskAdd.template_disks_get')
    def test_update_template_windows(self, mock_disks_get):
        # Arrange
        template = MagicMock(ID=1)
        image_id = 1
        os_type = 'windows'

        mock_disks_get.return_value = [{'key1': 'value1', 'key2': 'value2'}]
        expected_result = 'result'
        self.action.one = MagicMock()
        self.action.one.template.update.return_value = expected_result

        # Act
        result = self.action.update_template(template, image_id, os_type)

        # Assert
        self.assertEqual(result, expected_result)
        expected_attributes = (
            "DISK = [ key1 = value1 , key2 = value2 ]\n"
            "DISK = [ IMAGE_ID = 1 , DEV_PREFIX = vd , TARGET = vda , BUS = virtio ]"
        )
        mock_disks_get.assert_called_once_with(template)
        self.action.one.template.update.assert_called_once_with(template.ID, expected_attributes, 1)

    @patch('vm_disk_add.VmDiskAdd.pyone_session_create')
    @patch('vm_disk_add.VmDiskAdd.get_vm')
    @patch('vm_disk_add.VmDiskAdd.get_template')
    @patch('vm_disk_add.VmDiskAdd.get_datastore_id')
    @patch('vm_disk_add.VmDiskAdd.allocate_image')
    @patch('vm_disk_add.VmDiskAdd.attach_disk')
    @patch('vm_disk_add.VmDiskAdd.update_template')
    def test_run(self, mock_update_template, mock_attach_disk, mock_allocate_image, mock_get_datastore_id, mock_get_template, mock_get_vm, mock_pyone_session_create):
        # Arrange
        datastore_name = 'test_datastore'
        disk_check_timeout = 10
        disk_description = 'test_description'
        disk_format = 'test_format'
        disk_type = 'test_type'
        disk_name = 'test_disk'
        disk_size_gb = 10
        os_type = 'linux'
        vm_name = 'test_vm'
        open_nebula = 'open_nebula'

        mock_pyone_session_create.return_value = MagicMock()
        mock_get_vm.return_value = MagicMock(ID=1, TEMPLATE={'TEMPLATE_ID': 1})
        mock_get_template.return_value = MagicMock(ID=1)
        mock_get_datastore_id.return_value = 1
        mock_allocate_image.return_value = 1
        mock_attach_disk.return_value = True
        mock_update_template.return_value = True

        # Act
        result = self.action.run(datastore_name, disk_check_timeout, disk_description, disk_format,
                                 disk_type, disk_name, disk_size_gb, os_type, vm_name, open_nebula)

        # Assert
        self.assertEqual(result, (True, "Disk ID: 1"))
        mock_pyone_session_create.assert_called_once()
        mock_get_vm.assert_called_once_with(vm_name)
        mock_get_template.assert_called_once_with(1)
        mock_get_datastore_id.assert_called_once_with(datastore_name)
        mock_allocate_image.assert_called_once_with(disk_name, disk_description, disk_type, disk_size_gb,
                                                    disk_format, 1, disk_check_timeout)
        mock_attach_disk.assert_called_once_with(1, 1, disk_format)
        mock_update_template.assert_called_once_with(mock_get_template.return_value, 1, os_type)

if __name__ == '__main__':
    unittest.main()