# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import tempfile

from testtools import TestCase

from pysubunit import filters


class TestFindStream(TestCase):

    def test_no_argv(self):
        self.assertEqual('foo', filters.find_stream('foo', []))

    def test_opens_file(self):
        f = tempfile.NamedTemporaryFile()
        f.write(b'foo')
        f.flush()
        stream = filters.find_stream('bar', [f.name])
        self.assertEqual(b'foo', stream.read())
