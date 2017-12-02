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


from testtools import compat
from testtools import content
from testtools import content_type

import pysubunit
from pysubunit.tests import base


class TestSimpleDetails(base.TestCase):

    def test_lineReceived(self):
        parser = pysubunit.details.SimpleDetailsParser(None)
        parser.lineReceived(compat._b("foo\n"))
        parser.lineReceived(compat._b("bar\n"))
        self.assertEqual(compat._b("foo\nbar\n"), parser._message)

    def test_lineReceived_escaped_bracket(self):
        parser = pysubunit.details.SimpleDetailsParser(None)
        parser.lineReceived(compat._b("foo\n"))
        parser.lineReceived(compat._b(" ]are\n"))
        parser.lineReceived(compat._b("bar\n"))
        self.assertEqual(compat._b("foo\n]are\nbar\n"), parser._message)

    def test_get_message(self):
        parser = pysubunit.details.SimpleDetailsParser(None)
        self.assertEqual(compat._b(""), parser.get_message())

    def test_get_details(self):
        parser = pysubunit.details.SimpleDetailsParser(None)
        expected = {}
        expected['traceback'] = content.Content(
            content_type.ContentType("text", "x-traceback",
                                     {'charset': 'utf8'}),
            lambda: [compat._b("")])
        found = parser.get_details()
        self.assertEqual(expected.keys(), found.keys())
        self.assertEqual(expected['traceback'].content_type,
                         found['traceback'].content_type)
        self.assertEqual(
            compat._b('').join(expected['traceback'].iter_bytes()),
            compat._b('').join(found['traceback'].iter_bytes()))

    def test_get_details_skip(self):
        parser = pysubunit.details.SimpleDetailsParser(None)
        expected = {}
        expected['reason'] = content.Content(
            content_type.ContentType("text", "plain"),
            lambda: [compat._b("")])
        found = parser.get_details("skip")
        self.assertEqual(expected, found)

    def test_get_details_success(self):
        parser = pysubunit.details.SimpleDetailsParser(None)
        expected = {}
        expected['message'] = content.Content(
            content_type.ContentType("text", "plain"),
            lambda: [compat._b("")])
        found = parser.get_details("success")
        self.assertEqual(expected, found)


class TestMultipartDetails(base.TestCase):

    def test_get_message_is_None(self):
        parser = pysubunit.details.MultipartDetailsParser(None)
        self.assertEqual(None, parser.get_message())

    def test_get_details(self):
        parser = pysubunit.details.MultipartDetailsParser(None)
        self.assertEqual({}, parser.get_details())

    def test_parts(self):
        parser = pysubunit.details.MultipartDetailsParser(None)
        parser.lineReceived(compat._b("Content-Type: text/plain\n"))
        parser.lineReceived(compat._b("something\n"))
        parser.lineReceived(compat._b("F\r\n"))
        parser.lineReceived(compat._b("serialised\n"))
        parser.lineReceived(compat._b("form0\r\n"))
        expected = {}
        expected['something'] = content.Content(
            content_type.ContentType("text", "plain"),
            lambda: [compat._b("serialised\nform")])
        found = parser.get_details()
        self.assertEqual(expected.keys(), found.keys())
        self.assertEqual(expected['something'].content_type,
                         found['something'].content_type)
        self.assertEqual(
            compat._b('').join(expected['something'].iter_bytes()),
            compat._b('').join(found['something'].iter_bytes()))
