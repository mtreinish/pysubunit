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

"""Tests for subunit.TestResultStats."""

import unittest

from testtools import compat

import pysubunit


class TestTestResultStats(unittest.TestCase):
    """Test for TestResultStats, a TestResult object that generates stats."""

    def setUp(self):
        self.output = compat.StringIO()
        self.result = pysubunit.TestResultStats(self.output)
        self.input_stream = compat.BytesIO()
        self.test = pysubunit.ProtocolTestCase(self.input_stream)

    def test_stats_empty(self):
        self.test.run(self.result)
        self.assertEqual(0, self.result.total_tests)
        self.assertEqual(0, self.result.passed_tests)
        self.assertEqual(0, self.result.failed_tests)
        self.assertEqual(set(), self.result.seen_tags)

    def setUpUsedStream(self):
        self.input_stream.write(compat._b("""tags: global
test passed
success passed
test failed
tags: local
failure failed
test error
error error
test skipped
skip skipped
test todo
xfail todo
"""))
        self.input_stream.seek(0)
        self.test.run(self.result)

    def test_stats_smoke_everything(self):
        # Statistics are calculated usefully.
        self.setUpUsedStream()
        self.assertEqual(5, self.result.total_tests)
        self.assertEqual(2, self.result.passed_tests)
        self.assertEqual(2, self.result.failed_tests)
        self.assertEqual(1, self.result.skipped_tests)
        self.assertEqual(set(["global", "local"]), self.result.seen_tags)

    def test_stat_formatting(self):
        expected = ("""
Total tests:       5
Passed tests:      2
Failed tests:      2
Skipped tests:     1
Seen tags: global, local
""")[1:]
        self.setUpUsedStream()
        self.result.formatStats()
        self.assertEqual(expected, self.output.getvalue())
