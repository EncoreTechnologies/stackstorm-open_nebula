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
from one_base_action_test_case import OneBaseActionTestCase
import unittest.mock as mock
import pytest
from vnet_ip_lease_check import VnetIpLeaseCheck
import json

__all__ = [
    'VnetIpLeaseCheckTestCase'
]


class VnetIpLeaseCheckTestCase(OneBaseActionTestCase):
    __test__ = True
    action_cls = VnetIpLeaseCheck

    @mock.patch('vnet_ip_lease_check.xmltojson.parse')
    def test_ip_available(self, mock_parse):
        """Test that an IP not in any lease returns is_available=True"""
        ip_address = "172.22.208.55"
        vnet_name = "vlan_208_dev"
        open_nebula = "onecloud.dev.encore.internal"

        # Mock vnet pool response
        vnet_pool = {
            'VNET_POOL': {
                'VNET': [
                    {'ID': '1', 'NAME': 'vlan_208_dev'},
                    {'ID': '2', 'NAME': 'vlan_209_dev'}
                ]
            }
        }

        # Mock vnet info response (no leases for the IP we're checking)
        vnet_info = {
            'VNET': {
                'ID': '1',
                'NAME': 'vlan_208_dev',
                'AR_POOL': {
                    'AR': {
                        'AR_ID': '0',
                        'LEASES': {
                            'LEASE': [
                                {'IP': '172.22.208.50', 'VM': '100', 'MAC': '02:00:ac:16:d0:32'},
                                {'IP': '172.22.208.51', 'VM': '101', 'MAC': '02:00:ac:16:d0:33'}
                            ]
                        }
                    }
                }
            }
        }

        mock_session = mock.Mock()
        mock_session.one.vnpool.info.return_value = (True, "<xml></xml>")
        mock_session.one.vn.info.return_value = (True, "<xml></xml>")

        self.action.xmlrpc_session_create = mock.Mock(return_value=mock_session)

        # First call returns vnet pool, second returns vnet info
        mock_parse.side_effect = [json.dumps(vnet_pool), json.dumps(vnet_info)]

        result = self.action.run(ip_address, vnet_name, open_nebula)

        assert result['is_available'] is True
        assert result['ip_address'] == ip_address
        assert result['vnet_name'] == vnet_name
        assert result['leased_by'] is None

    @mock.patch('vnet_ip_lease_check.xmltojson.parse')
    def test_ip_leased(self, mock_parse):
        """Test that an IP in a lease returns is_available=False with VM details"""
        ip_address = "172.22.208.55"
        vnet_name = "vlan_208_dev"
        open_nebula = "onecloud.dev.encore.internal"

        vnet_pool = {
            'VNET_POOL': {
                'VNET': {'ID': '1', 'NAME': 'vlan_208_dev'}
            }
        }

        vnet_info = {
            'VNET': {
                'ID': '1',
                'NAME': 'vlan_208_dev',
                'AR_POOL': {
                    'AR': {
                        'AR_ID': '0',
                        'LEASES': {
                            'LEASE': {
                                'IP': '172.22.208.55',
                                'VM': '123',
                                'MAC': '02:00:ac:16:d0:37'
                            }
                        }
                    }
                }
            }
        }

        vm_info = {
            'VM': {
                'ID': '123',
                'NAME': 'nor1devweid01.dev.encore.internal'
            }
        }

        mock_session = mock.Mock()
        mock_session.one.vnpool.info.return_value = (True, "<xml></xml>")
        mock_session.one.vn.info.return_value = (True, "<xml></xml>")
        mock_session.one.vm.info.return_value = (True, "<xml></xml>")

        self.action.xmlrpc_session_create = mock.Mock(return_value=mock_session)

        mock_parse.side_effect = [json.dumps(vnet_pool), json.dumps(vnet_info), json.dumps(vm_info)]

        result = self.action.run(ip_address, vnet_name, open_nebula)

        assert result['is_available'] is False
        assert result['ip_address'] == ip_address
        assert result['vnet_name'] == vnet_name
        assert result['leased_by']['vm_id'] == '123'
        assert result['leased_by']['vm_name'] == 'nor1devweid01.dev.encore.internal'
        assert result['leased_by']['mac'] == '02:00:ac:16:d0:37'

    @mock.patch('vnet_ip_lease_check.xmltojson.parse')
    def test_vnet_not_found(self, mock_parse):
        """Test that a non-existent vnet raises an exception"""
        ip_address = "172.22.208.55"
        vnet_name = "vlan_nonexistent"
        open_nebula = "onecloud.dev.encore.internal"

        vnet_pool = {
            'VNET_POOL': {
                'VNET': [
                    {'ID': '1', 'NAME': 'vlan_208_dev'},
                    {'ID': '2', 'NAME': 'vlan_209_dev'}
                ]
            }
        }

        mock_session = mock.Mock()
        mock_session.one.vnpool.info.return_value = (True, "<xml></xml>")

        self.action.xmlrpc_session_create = mock.Mock(return_value=mock_session)
        mock_parse.return_value = json.dumps(vnet_pool)

        with pytest.raises(Exception) as excinfo:
            self.action.run(ip_address, vnet_name, open_nebula)

        assert "not found" in str(excinfo.value)

    @mock.patch('vnet_ip_lease_check.xmltojson.parse')
    def test_multiple_address_ranges(self, mock_parse):
        """Test checking IP across multiple address ranges"""
        ip_address = "172.22.209.10"
        vnet_name = "vlan_208_dev"
        open_nebula = "onecloud.dev.encore.internal"

        vnet_pool = {
            'VNET_POOL': {
                'VNET': {'ID': '1', 'NAME': 'vlan_208_dev'}
            }
        }

        # Multiple ARs, IP is in the second one
        vnet_info = {
            'VNET': {
                'ID': '1',
                'NAME': 'vlan_208_dev',
                'AR_POOL': {
                    'AR': [
                        {
                            'AR_ID': '0',
                            'LEASES': {
                                'LEASE': {
                                    'IP': '172.22.208.50',
                                    'VM': '100',
                                    'MAC': '02:00:ac:16:d0:32'
                                }
                            }
                        },
                        {
                            'AR_ID': '1',
                            'LEASES': {
                                'LEASE': {
                                    'IP': '172.22.209.10',
                                    'VM': '200',
                                    'MAC': '02:00:ac:16:d1:0a'
                                }
                            }
                        }
                    ]
                }
            }
        }

        vm_info = {
            'VM': {
                'ID': '200',
                'NAME': 'test-vm.dev.encore.internal'
            }
        }

        mock_session = mock.Mock()
        mock_session.one.vnpool.info.return_value = (True, "<xml></xml>")
        mock_session.one.vn.info.return_value = (True, "<xml></xml>")
        mock_session.one.vm.info.return_value = (True, "<xml></xml>")

        self.action.xmlrpc_session_create = mock.Mock(return_value=mock_session)
        mock_parse.side_effect = [json.dumps(vnet_pool), json.dumps(vnet_info), json.dumps(vm_info)]

        result = self.action.run(ip_address, vnet_name, open_nebula)

        assert result['is_available'] is False
        assert result['leased_by']['vm_id'] == '200'
        assert result['leased_by']['ar_id'] == '1'

    def test_api_error_vnet_pool(self):
        """Test handling of API error when getting vnet pool"""
        ip_address = "172.22.208.55"
        vnet_name = "vlan_208_dev"
        open_nebula = "onecloud.dev.encore.internal"

        mock_session = mock.Mock()
        mock_session.one.vnpool.info.return_value = (False, "Authentication failed")

        self.action.xmlrpc_session_create = mock.Mock(return_value=mock_session)

        with pytest.raises(Exception) as excinfo:
            self.action.run(ip_address, vnet_name, open_nebula)

        assert "Failed to get vnet pool" in str(excinfo.value)
