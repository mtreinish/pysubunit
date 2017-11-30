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

import io
import os.path

import fixtures
from testtools import matchers

from pysubunit import _to_disk
from pysubunit.tests import base
from pysubunit import v2


class SmokeTest(base.TestCase):

    def test_smoke(self):
        output = os.path.join(
            self.useFixture(fixtures.TempDir()).path, 'output')
        stdin = io.BytesIO()
        stdout = io.StringIO()
        writer = v2.StreamResultToBytes(stdin)
        writer.startTestRun()
        writer.status(
            'foo', 'success', set(['tag']), file_name='fred',
            file_bytes=b'abcdefg', eof=True, mime_type='text/plain')
        writer.stopTestRun()
        stdin.seek(0)
        _to_disk.to_disk(['-d', output], stdin=stdin, stdout=stdout)
        self.expectThat(
            os.path.join(output, 'foo/test.json'),
            matchers.FileContains(
                '{"details": ["fred"], "id": "foo", "start": null, '
                '"status": "success", "stop": null, "tags": ["tag"]}'))
        self.expectThat(
            os.path.join(output, 'foo/fred'),
            matchers.FileContains('abcdefg'))
