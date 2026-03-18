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


class ConnectionTest(BaseAction):

    def run(self, open_nebula=None):
        conn = self._get_connection_info(open_nebula)
        success = None
        try:
            # Connect to the Open Nebula instance
            one = self.pyone_session_create(open_nebula)
            # Make a simple API call to verify the connection works
            one.hostpool.info()
            success = True
        except:
            # if the connection errors then an exception is thrown
            success = False

        return (success, {'data': {'server': conn['host'],
                                   'username': conn['user']}})
