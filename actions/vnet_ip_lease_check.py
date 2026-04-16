#!/usr/bin/env python
# Copyright 2026 Encore Technologies
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
"""
Check if an IP address is already leased in an OpenNebula virtual network.

This action queries OpenNebula's vnet lease table to verify an IP is available
before attempting to provision a VM with that IP. This prevents failures when
Men&Mice (IPAM) and OpenNebula's internal IPAM are out of sync.
"""

from lib.action_base import BaseAction
import xmltojson
import json


class VnetIpLeaseCheck(BaseAction):

    def run(self, ip_address, vnet_name, open_nebula=None):
        """Check if an IP is already leased in the specified vnet.

        Args:
            ip_address: The IP address to check (e.g., "172.22.208.55")
            vnet_name: The virtual network name (e.g., "vlan_208_dev_172.22.208_VM_NETWORK_0")
            open_nebula: OpenNebula connection name from config

        Returns:
            dict: {
                'is_available': bool,
                'ip_address': str,
                'vnet_name': str,
                'leased_by': dict or None  # VM details if leased
            }

        Raises:
            Exception: If vnet not found or API error
        """
        xmlrpc_session = self.xmlrpc_session_create(open_nebula)

        # Get all vnets to find the one we're looking for
        # one.vnpool.info(auth, filter_flag, start_id, end_id)
        # -2 = all resources, -1/-1 = no pagination
        response = xmlrpc_session.one.vnpool.info(self.auth_string, -2, -1, -1)

        if not response[0]:
            raise Exception("Failed to get vnet pool: {}".format(response[1]))

        vnet_pool = json.loads(xmltojson.parse(response[1]))
        vnets = vnet_pool.get('VNET_POOL', {}).get('VNET', [])

        # Handle single vnet case (returned as dict instead of list)
        if isinstance(vnets, dict):
            vnets = [vnets]

        # Find the target vnet by name
        target_vnet = None
        for vnet in vnets:
            if vnet.get('NAME') == vnet_name:
                target_vnet = vnet
                break

        if not target_vnet:
            raise Exception("Virtual network '{}' not found in OpenNebula".format(vnet_name))

        vnet_id = target_vnet['ID']

        # Get detailed vnet info including leases
        # one.vn.info(auth, vnet_id, decrypt)
        response = xmlrpc_session.one.vn.info(self.auth_string, int(vnet_id), False)

        if not response[0]:
            raise Exception("Failed to get vnet info for ID {}: {}".format(vnet_id, response[1]))

        vnet_info = json.loads(xmltojson.parse(response[1]))
        vnet_data = vnet_info.get('VNET', {})

        # Check AR_POOL for leases
        ar_pool = vnet_data.get('AR_POOL', {})
        address_ranges = ar_pool.get('AR', [])

        # Handle single AR case
        if isinstance(address_ranges, dict):
            address_ranges = [address_ranges]

        # Search through all address ranges for the IP
        for ar in address_ranges:
            leases = ar.get('LEASES', {}).get('LEASE', [])

            # Handle single lease case
            if isinstance(leases, dict):
                leases = [leases]

            for lease in leases:
                if lease.get('IP') == ip_address:
                    # IP is leased - get VM details
                    vm_id = lease.get('VM')
                    vm_name = None

                    # Try to get VM name if we have an ID
                    if vm_id and vm_id != '-1':
                        try:
                            vm_response = xmlrpc_session.one.vm.info(
                                self.auth_string, int(vm_id), False
                            )
                            if vm_response[0]:
                                vm_info = json.loads(xmltojson.parse(vm_response[1]))
                                vm_name = vm_info.get('VM', {}).get('NAME')
                        except Exception:
                            # If we can't get VM name, continue with ID only
                            pass

                    return {
                        'is_available': False,
                        'ip_address': ip_address,
                        'vnet_name': vnet_name,
                        'leased_by': {
                            'vm_id': vm_id,
                            'vm_name': vm_name,
                            'mac': lease.get('MAC'),
                            'ar_id': ar.get('AR_ID')
                        }
                    }

        # IP not found in any lease - it's available
        return {
            'is_available': True,
            'ip_address': ip_address,
            'vnet_name': vnet_name,
            'leased_by': None
        }
