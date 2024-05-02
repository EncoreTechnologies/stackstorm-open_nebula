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

import requests
from lib.action_base import BaseAction

import time


class VmDiskAdd(BaseAction):

    def get_vm_id(self, vm_name):
        vms = self.one.vmpool.info(-2, -1, -1, -1, "NAME={}".format(vm_name))
        if not vms.VM:
            raise Exception("Could not find VM with name: {}".format(vm_name))

        return vms.VM[0].ID

    def get_datastore_id(self, datastore_name):
        datastores = self.one.datastorepool.info()
        if not datastores.DATASTORE:
            raise Exception("No datastores found!")
        for datastore in datastores.DATASTORE:
            if datastore_name == datastore.NAME:
                return datastore.ID

        raise Exception("Could not find datastore with name: {}".format(datastore_name))

    def allocate_image(self, disk_name, disk_description, disk_type, disk_size_gb,
                       disk_format, datastore_id, disk_check_timeout):
        # Create the template for your image. Size is specified in MB.
        image_template = {
            "NAME": disk_name,
            "DESCRIPTION": disk_description,
            "TYPE": disk_type,
            "SIZE": disk_size_gb * 1024,
            "FORMAT": disk_format,
            "PERSISTENT": "yes"
        }

        result = self.one.image.allocate(image_template, datastore_id)

        # Wait for disk to enter a ready state
        image_state = self.one.image.info(result).STATE
        start_time = time.time()
        while image_state != 1:
            # Set elapsed time for timeout check
            elapsed_time = time.time() - start_time
            if elapsed_time > disk_check_timeout:
                raise Exception("Timed out waiting for disk to enter a ready state.")

            # Wait a couple seconds before checking again
            time.sleep(5)

            # Update the image state for next check
            image_state = self.one.image.info(result).STATE

        return result

    def attach_disk(self, vm_id, image_id, disk_format):
        # Create the template for your image. Size is specified in MB.
        disk_vector = "DISK=[IMAGE_ID={}, DRIVER={}]".format(image_id, disk_format)

        return self.one.vm.attach(vm_id, disk_vector)

    def run(self, datastore_name, disk_check_timeout, disk_description, disk_format,
            disk_type, disk_name, disk_size_gb, vm_name, open_nebula=None):
        self.one = self.session_create(open_nebula)

        # Grab the VM ID
        vm_id = self.get_vm_id(vm_name)

        # Grab the datastore ID
        datastore_id = self.get_datastore_id(datastore_name)

        # Allocate a new image
        image_id = self.allocate_image(disk_name, disk_description, disk_type, disk_size_gb,
                                       disk_format, datastore_id, disk_check_timeout)

        # Attach the disk to the VM
        self.attach_disk(vm_id, image_id, disk_format)

        return (True, "Disk ID: {}".format(image_id))
