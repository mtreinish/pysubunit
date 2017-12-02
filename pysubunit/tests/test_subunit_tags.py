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

"""Tests for subunit.tag_stream."""

import io

from testtools import matchers

import pysubunit
import pysubunit.test_results
from pysubunit.tests import base
from pysubunit import v2


class TestSubUnitTags(base.TestCase):

    def setUp(self):
        super(TestSubUnitTags, self).setUp()
        self.original = io.BytesIO()
        self.filtered = io.BytesIO()

    def test_add_tag(self):
        # Literal values to avoid set sort-order dependencies. Python code show
        # derivation.
        # reference = BytesIO()
        # stream = subunit.StreamResultToBytes(reference)
        # stream.status(
        #     test_id='test', test_status='inprogress',
        #     test_tags=set(['quux', 'foo']))
        # stream.status(
        #     test_id='test', test_status='success',
        #     test_tags=set(['bar', 'quux', 'foo']))
        reference = [
            (b'\xb3)\x82\x17\x04test\x02\x04quux\x03foo\x05\x97n\x86\xb3)'
             b'\x83\x1b\x04test\x03\x03bar\x04quux\x03fooqn\xab)'),
            (b'\xb3)\x82\x17\x04test\x02\x04quux\x03foo\x05\x97n\x86\xb3)'
             b'\x83\x1b\x04test\x03\x04quux\x03foo\x03bar\xaf\xbd\x9d\xd6'),
            (b'\xb3)\x82\x17\x04test\x02\x04quux\x03foo\x05\x97n\x86\xb3)'
             b'\x83\x1b\x04test\x03\x04quux\x03bar\x03foo\x03\x04b\r'),
            (b'\xb3)\x82\x17\x04test\x02\x04quux\x03foo\x05\x97n\x86\xb3)'
             b'\x83\x1b\x04test\x03\x03bar\x03foo\x04quux\xd2\x18\x1bC'),
            (b'\xb3)\x82\x17\x04test\x02\x03foo\x04quux\xa6\xe1\xde\xec\xb3)'
             b'\x83\x1b\x04test\x03\x03foo\x04quux\x03bar\x08\xc2X\x83'),
            (b'\xb3)\x82\x17\x04test\x02\x03foo\x04quux\xa6\xe1\xde\xec\xb3)'
             b'\x83\x1b\x04test\x03\x03bar\x03foo\x04quux\xd2\x18\x1bC'),
            (b'\xb3)\x82\x17\x04test\x02\x03foo\x04quux\xa6\xe1\xde\xec\xb3)'
             b'\x83\x1b\x04test\x03\x03foo\x03bar\x04quux:\x05e\x80')]
        stream = v2.StreamResultToBytes(self.original)
        stream.status(
            test_id='test', test_status='inprogress', test_tags=set(['foo']))
        stream.status(
            test_id='test', test_status='success',
            test_tags=set(['foo', 'bar']))
        self.original.seek(0)
        self.assertEqual(
            0, pysubunit.tag_stream(self.original, self.filtered, ["quux"]))
        self.assertThat(reference, matchers.Contains(self.filtered.getvalue()))

    def test_remove_tag(self):
        reference = io.BytesIO()
        stream = v2.StreamResultToBytes(reference)
        stream.status(
            test_id='test', test_status='inprogress', test_tags=set(['foo']))
        stream.status(
            test_id='test', test_status='success', test_tags=set(['foo']))
        stream = v2.StreamResultToBytes(self.original)
        stream.status(
            test_id='test', test_status='inprogress', test_tags=set(['foo']))
        stream.status(
            test_id='test', test_status='success',
            test_tags=set(['foo', 'bar']))
        self.original.seek(0)
        self.assertEqual(
            0, pysubunit.tag_stream(self.original, self.filtered, ["-bar"]))
        self.assertEqual(reference.getvalue(), self.filtered.getvalue())
