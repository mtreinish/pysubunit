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
import unittest

import mock
import testtools
from testtools.compat import _b
from testtools.matchers import StartsWith
from testtools.testresult.doubles import StreamResult

from pysubunit import run
from pysubunit.tests import base
from pysubunit import v2


class TestSubunitTestRunner(base.TestCase):

    def test_includes_timing_output(self):
        bytestream = io.BytesIO()
        runner = run.SubunitTestRunner(stream=bytestream)
        test = testtools.PlaceHolder('name')
        runner.run(test)
        bytestream.seek(0)
        eventstream = StreamResult()
        v2.ByteStreamToStreamResult(bytestream).run(eventstream)
        timestamps = [
            event[-1] for event in eventstream._events if event is not None]
        self.assertNotEqual([], timestamps)

    def test_enumerates_tests_before_run(self):
        bytestream = io.BytesIO()
        runner = run.SubunitTestRunner(stream=bytestream)
        test1 = testtools.PlaceHolder('name1')
        test2 = testtools.PlaceHolder('name2')
        case = unittest.TestSuite([test1, test2])
        runner.run(case)
        bytestream.seek(0)
        eventstream = StreamResult()
        v2.ByteStreamToStreamResult(bytestream).run(eventstream)
        self.assertEqual([
            ('status', 'name1', 'exists'),
            ('status', 'name2', 'exists'),
            ], [event[:3] for event in eventstream._events[:2]])

    def test_list_errors_if_errors_from_list_test(self):
        bytestream = io.BytesIO()
        runner = run.SubunitTestRunner(stream=bytestream)

        def list_test(test):
            return [], ['failed import']

        with mock.patch('testtools.run.list_test',
                        return_value=([], ['failed import'])):
            exc = self.assertRaises(SystemExit, runner.list, None)
            self.assertEqual((2,), exc.args)

    def test_list_includes_loader_errors(self):
        bytestream = io.BytesIO()
        runner = run.SubunitTestRunner(stream=bytestream)

        def list_test(test):
            return [], []

        class Loader(object):
            errors = ['failed import']

        loader = Loader()
        with mock.patch('testtools.run.list_test', return_value=([], [])):
            exc = self.assertRaises(SystemExit, runner.list, None,
                                    loader=loader)
            self.assertEqual((2,), exc.args)

    class FailingTest(base.TestCase):
        def test_fail(self):
            raise ZeroDivisionError('Math is hard')

    def test_exits_zero_when_tests_fail(self):
        bytestream = io.BytesIO()
        stream = io.TextIOWrapper(bytestream, encoding="utf8")
        try:
            self.assertEqual(
                None, run.main(
                    argv=["progName",
                          "pysubunit.tests.test_run.TestSubunitTestRunner.:"
                          "FailingTest"], stdout=stream))
        except SystemExit:
            self.fail("SystemExit raised")
        self.assertThat(bytestream.getvalue(), StartsWith(_b('\xb3')))

    class ExitingTest(base.TestCase):
        def test_exit(self):
            raise SystemExit(0)

    def test_exits_nonzero_when_execution_errors(self):
        bytestream = io.BytesIO()
        stream = io.TextIOWrapper(bytestream, encoding="utf8")
        exc = self.assertRaises(
            SystemExit, run.main,
            argv=["progName",
                  "pysubunit.tests.test_run.TestSubunitTestRunner."
                  "ExitingTest"], stdout=stream)
        self.assertEqual(0, exc.args[0])
