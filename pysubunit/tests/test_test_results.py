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

import csv
import datetime
import sys
import unittest

import iso8601
from testtools import compat
from testtools import content
from testtools.testresult import doubles

import pysubunit
import pysubunit.test_results
from pysubunit.tests import base


class LoggingDecorator(pysubunit.test_results.HookedTestResultDecorator):

    def __init__(self, decorated):
        self._calls = 0
        super(LoggingDecorator, self).__init__(decorated)

    def _before_event(self):
        self._calls += 1


class AssertBeforeTestResult(LoggingDecorator):
    """A TestResult for checking preconditions."""

    def __init__(self, decorated, test):
        self.test = test
        super(AssertBeforeTestResult, self).__init__(decorated)

    def _before_event(self):
        self.test.assertEqual(1, self.earlier._calls)
        super(AssertBeforeTestResult, self)._before_event()


class TimeCapturingResult(unittest.TestResult):

    def __init__(self):
        super(TimeCapturingResult, self).__init__()
        self._calls = []
        self.failfast = False

    def time(self, a_datetime):
        self._calls.append(a_datetime)


class TestHookedTestResultDecorator(base.TestCase):

    def setUp(self):
        super(TestHookedTestResultDecorator, self).setUp()
        # An end to the chain
        terminal = unittest.TestResult()
        # Asserts that the call was made to self.result before asserter was
        # called.
        asserter = AssertBeforeTestResult(terminal, self)
        # The result object we call, which much increase its call count.
        self.result = LoggingDecorator(asserter)
        asserter.earlier = self.result
        self.decorated = asserter

    def tearDown(self):
        # The hook in self.result must have been called
        self.assertEqual(1, self.result._calls)
        # The hook in asserter must have been called too, otherwise the
        # assertion about ordering won't have completed.
        self.assertEqual(1, self.decorated._calls)
        super(TestHookedTestResultDecorator, self).tearDown()

    def test_startTest(self):
        self.result.startTest(self)

    def test_startTestRun(self):
        self.result.startTestRun()

    def test_stopTest(self):
        self.result.stopTest(self)

    def test_stopTestRun(self):
        self.result.stopTestRun()

    def test_addError(self):
        self.result.addError(self, pysubunit.RemoteError())

    def test_addError_details(self):
        self.result.addError(self, details={})

    def test_addFailure(self):
        self.result.addFailure(self, pysubunit.RemoteError())

    def test_addFailure_details(self):
        self.result.addFailure(self, details={})

    def test_addSuccess(self):
        self.result.addSuccess(self)

    def test_addSuccess_details(self):
        self.result.addSuccess(self, details={})

    def test_addSkip(self):
        self.result.addSkip(self, "foo")

    def test_addSkip_details(self):
        self.result.addSkip(self, details={})

    def test_addExpectedFailure(self):
        self.result.addExpectedFailure(self, pysubunit.RemoteError())

    def test_addExpectedFailure_details(self):
        self.result.addExpectedFailure(self, details={})

    def test_addUnexpectedSuccess(self):
        self.result.addUnexpectedSuccess(self)

    def test_addUnexpectedSuccess_details(self):
        self.result.addUnexpectedSuccess(self, details={})

    def test_progress(self):
        self.result.progress(1, pysubunit.PROGRESS_SET)

    def test_wasSuccessful(self):
        self.result.wasSuccessful()

    def test_shouldStop(self):
        self.result.shouldStop

    def test_stop(self):
        self.result.stop()

    def test_time(self):
        self.result.time(None)


class TestAutoTimingTestResultDecorator(base.TestCase):

    def setUp(self):
        super(TestAutoTimingTestResultDecorator, self).setUp()
        # And end to the chain which captures time events.
        terminal = TimeCapturingResult()
        # The result object under test.
        self.result = pysubunit.test_results.AutoTimingTestResultDecorator(
            terminal)
        self.decorated = terminal

    def test_without_time_calls_time_is_called_and_not_None(self):
        self.result.startTest(self)
        self.assertEqual(1, len(self.decorated._calls))
        self.assertNotEqual(None, self.decorated._calls[0])

    def test_no_time_from_progress(self):
        self.result.progress(1, pysubunit.PROGRESS_CUR)
        self.assertEqual(0, len(self.decorated._calls))

    def test_no_time_from_shouldStop(self):
        self.decorated.stop()
        self.result.shouldStop
        self.assertEqual(0, len(self.decorated._calls))

    def test_calling_time_inhibits_automatic_time(self):
        # Calling time() outputs a time signal immediately and prevents
        # automatically adding one when other methods are called.
        time = datetime.datetime(2009, 10, 11, 12, 13, 14, 15, iso8601.UTC)
        self.result.time(time)
        self.result.startTest(self)
        self.result.stopTest(self)
        self.assertEqual(1, len(self.decorated._calls))
        self.assertEqual(time, self.decorated._calls[0])

    def test_calling_time_None_enables_automatic_time(self):
        time = datetime.datetime(2009, 10, 11, 12, 13, 14, 15, iso8601.UTC)
        self.result.time(time)
        self.assertEqual(1, len(self.decorated._calls))
        self.assertEqual(time, self.decorated._calls[0])
        # Calling None passes the None through, in case other results care.
        self.result.time(None)
        self.assertEqual(2, len(self.decorated._calls))
        self.assertEqual(None, self.decorated._calls[1])
        # Calling other methods doesn't generate an automatic time event.
        self.result.startTest(self)
        self.assertEqual(3, len(self.decorated._calls))
        self.assertNotEqual(None, self.decorated._calls[2])

    def test_set_failfast_True(self):
        self.assertFalse(self.decorated.failfast)
        self.result.failfast = True
        self.assertTrue(self.decorated.failfast)


class TestTagCollapsingDecorator(base.TestCase):

    def test_tags_collapsed_outside_of_tests(self):
        result = doubles.ExtendedTestResult()
        tag_collapser = pysubunit.test_results.TagCollapsingDecorator(result)
        tag_collapser.tags(set(['a']), set())
        tag_collapser.tags(set(['b']), set())
        tag_collapser.startTest(self)
        self.assertEqual(
            [('tags', set(['a', 'b']), set([])),
             ('startTest', self),
             ], result._events)

    def test_tags_collapsed_outside_of_tests_are_flushed(self):
        result = doubles.ExtendedTestResult()
        tag_collapser = pysubunit.test_results.TagCollapsingDecorator(result)
        tag_collapser.startTestRun()
        tag_collapser.tags(set(['a']), set())
        tag_collapser.tags(set(['b']), set())
        tag_collapser.startTest(self)
        tag_collapser.addSuccess(self)
        tag_collapser.stopTest(self)
        tag_collapser.stopTestRun()
        self.assertEqual(
            [('startTestRun',),
             ('tags', set(['a', 'b']), set([])),
             ('startTest', self),
             ('addSuccess', self),
             ('stopTest', self),
             ('stopTestRun',),
             ], result._events)

    def test_tags_forwarded_after_tests(self):
        test = pysubunit.RemotedTestCase('foo')
        result = doubles.ExtendedTestResult()
        tag_collapser = pysubunit.test_results.TagCollapsingDecorator(result)
        tag_collapser.startTestRun()
        tag_collapser.startTest(test)
        tag_collapser.addSuccess(test)
        tag_collapser.stopTest(test)
        tag_collapser.tags(set(['a']), set(['b']))
        tag_collapser.stopTestRun()
        self.assertEqual(
            [('startTestRun',),
             ('startTest', test),
             ('addSuccess', test),
             ('stopTest', test),
             ('tags', set(['a']), set(['b'])),
             ('stopTestRun',),
             ],
            result._events)

    def test_tags_collapsed_inside_of_tests(self):
        result = doubles.ExtendedTestResult()
        tag_collapser = pysubunit.test_results.TagCollapsingDecorator(result)
        test = pysubunit.RemotedTestCase('foo')
        tag_collapser.startTest(test)
        tag_collapser.tags(set(['a']), set())
        tag_collapser.tags(set(['b']), set(['a']))
        tag_collapser.tags(set(['c']), set())
        tag_collapser.stopTest(test)
        self.assertEqual(
            [('startTest', test),
             ('tags', set(['b', 'c']), set(['a'])),
             ('stopTest', test)],
            result._events)

    def test_tags_collapsed_inside_of_tests_different_ordering(self):
        result = doubles.ExtendedTestResult()
        tag_collapser = pysubunit.test_results.TagCollapsingDecorator(result)
        test = pysubunit.RemotedTestCase('foo')
        tag_collapser.startTest(test)
        tag_collapser.tags(set(), set(['a']))
        tag_collapser.tags(set(['a', 'b']), set())
        tag_collapser.tags(set(['c']), set())
        tag_collapser.stopTest(test)
        self.assertEqual(
            [('startTest', test),
             ('tags', set(['a', 'b', 'c']), set()),
             ('stopTest', test)],
            result._events)

    def test_tags_sent_before_result(self):
        # Because addSuccess and friends tend to send subunit output
        # immediately, and because 'tags:' before a result line means
        # something different to 'tags:' after a result line, we need to be
        # sure that tags are emitted before 'addSuccess' (or whatever).
        result = doubles.ExtendedTestResult()
        tag_collapser = pysubunit.test_results.TagCollapsingDecorator(result)
        test = pysubunit.RemotedTestCase('foo')
        tag_collapser.startTest(test)
        tag_collapser.tags(set(['a']), set())
        tag_collapser.addSuccess(test)
        tag_collapser.stopTest(test)
        self.assertEqual(
            [('startTest', test),
             ('tags', set(['a']), set()),
             ('addSuccess', test),
             ('stopTest', test)],
            result._events)


class TestTimeCollapsingDecorator(base.TestCase):

    def make_time(self):
        # Heh heh.
        return datetime.datetime(
            2000, 1, self.getUniqueInteger(), tzinfo=iso8601.UTC)

    def test_initial_time_forwarded(self):
        # We always forward the first time event we see.
        result = doubles.ExtendedTestResult()
        tag_collapser = pysubunit.test_results.TimeCollapsingDecorator(result)
        a_time = self.make_time()
        tag_collapser.time(a_time)
        self.assertEqual([('time', a_time)], result._events)

    def test_time_collapsed_to_first_and_last(self):
        # If there are many consecutive time events, only the first and last
        # are sent through.
        result = doubles.ExtendedTestResult()
        tag_collapser = pysubunit.test_results.TimeCollapsingDecorator(result)
        times = [self.make_time() for i in range(5)]
        for a_time in times:
            tag_collapser.time(a_time)
        tag_collapser.startTest(pysubunit.RemotedTestCase('foo'))
        self.assertEqual(
            [('time', times[0]), ('time', times[-1])], result._events[:-1])

    def test_only_one_time_sent(self):
        # If we receive a single time event followed by a non-time event, we
        # send exactly one time event.
        result = doubles.ExtendedTestResult()
        tag_collapser = pysubunit.test_results.TimeCollapsingDecorator(result)
        a_time = self.make_time()
        tag_collapser.time(a_time)
        tag_collapser.startTest(pysubunit.RemotedTestCase('foo'))
        self.assertEqual([('time', a_time)], result._events[:-1])

    def test_duplicate_times_not_sent(self):
        # Many time events with the exact same time are collapsed into one
        # time event.
        result = doubles.ExtendedTestResult()
        tag_collapser = pysubunit.test_results.TimeCollapsingDecorator(result)
        a_time = self.make_time()
        for i in range(5):
            tag_collapser.time(a_time)
        tag_collapser.startTest(pysubunit.RemotedTestCase('foo'))
        self.assertEqual([('time', a_time)], result._events[:-1])

    def test_no_times_inserted(self):
        result = doubles.ExtendedTestResult()
        tag_collapser = pysubunit.test_results.TimeCollapsingDecorator(result)
        a_time = self.make_time()
        tag_collapser.time(a_time)
        foo = pysubunit.RemotedTestCase('foo')
        tag_collapser.startTest(foo)
        tag_collapser.addSuccess(foo)
        tag_collapser.stopTest(foo)
        self.assertEqual(
            [('time', a_time),
             ('startTest', foo),
             ('addSuccess', foo),
             ('stopTest', foo)], result._events)


class TestByTestResultTests(base.TestCase):

    def setUp(self):
        super(TestByTestResultTests, self).setUp()
        self.log = []
        self.result = pysubunit.test_results.TestByTestResult(self.on_test)
        if sys.version_info >= (3, 0):
            self.result._now = iter(range(5)).__next__
        else:
            self.result._now = iter(range(5)).next

    def assertCalled(self, **kwargs):
        defaults = {
            'test': self,
            'tags': set(),
            'details': None,
            'start_time': 0,
            'stop_time': 1,
            }
        defaults.update(kwargs)
        self.assertEqual([defaults], self.log)

    def on_test(self, **kwargs):
        self.log.append(kwargs)

    def test_no_tests_nothing_reported(self):
        self.result.startTestRun()
        self.result.stopTestRun()
        self.assertEqual([], self.log)

    def test_add_success(self):
        self.result.startTest(self)
        self.result.addSuccess(self)
        self.result.stopTest(self)
        self.assertCalled(status='success')

    def test_add_success_details(self):
        self.result.startTest(self)
        details = {'foo': 'bar'}
        self.result.addSuccess(self, details=details)
        self.result.stopTest(self)
        self.assertCalled(status='success', details=details)

    def test_tags(self):
        if not getattr(self.result, 'tags', None):
            self.skipTest("No tags in testtools")
        self.result.tags(['foo'], [])
        self.result.startTest(self)
        self.result.addSuccess(self)
        self.result.stopTest(self)
        self.assertCalled(status='success', tags=set(['foo']))

    def test_add_error(self):
        self.result.startTest(self)
        try:
            raise ZeroDivisionError('Math is hard!')
        except ZeroDivisionError:
            error = sys.exc_info()
        self.result.addError(self, error)
        self.result.stopTest(self)
        self.assertCalled(
            status='error',
            details={'traceback': content.TracebackContent(error, self)})

    def test_add_error_details(self):
        self.result.startTest(self)
        details = {"foo": content.text_content("bar")}
        self.result.addError(self, details=details)
        self.result.stopTest(self)
        self.assertCalled(status='error', details=details)

    def test_add_failure(self):
        self.result.startTest(self)
        try:
            self.fail("intentional failure")
        except self.failureException:
            failure = sys.exc_info()
        self.result.addFailure(self, failure)
        self.result.stopTest(self)
        self.assertCalled(
            status='failure',
            details={'traceback': content.TracebackContent(failure, self)})

    def test_add_failure_details(self):
        self.result.startTest(self)
        details = {"foo": content.text_content("bar")}
        self.result.addFailure(self, details=details)
        self.result.stopTest(self)
        self.assertCalled(status='failure', details=details)

    def test_add_xfail(self):
        self.result.startTest(self)
        try:
            raise ZeroDivisionError('Math is hard!')
        except ZeroDivisionError:
            error = sys.exc_info()
        self.result.addExpectedFailure(self, error)
        self.result.stopTest(self)
        self.assertCalled(
            status='xfail',
            details={'traceback': content.TracebackContent(error, self)})

    def test_add_xfail_details(self):
        self.result.startTest(self)
        details = {"foo": content.text_content("bar")}
        self.result.addExpectedFailure(self, details=details)
        self.result.stopTest(self)
        self.assertCalled(status='xfail', details=details)

    def test_add_unexpected_success(self):
        self.result.startTest(self)
        details = {'foo': 'bar'}
        self.result.addUnexpectedSuccess(self, details=details)
        self.result.stopTest(self)
        self.assertCalled(status='success', details=details)

    def test_add_skip_reason(self):
        self.result.startTest(self)
        reason = self.getUniqueString()
        self.result.addSkip(self, reason)
        self.result.stopTest(self)
        self.assertCalled(
            status='skip', details={'reason': content.text_content(reason)})

    def test_add_skip_details(self):
        self.result.startTest(self)
        details = {'foo': 'bar'}
        self.result.addSkip(self, details=details)
        self.result.stopTest(self)
        self.assertCalled(status='skip', details=details)

    def test_twice(self):
        self.result.startTest(self)
        self.result.addSuccess(self, details={'foo': 'bar'})
        self.result.stopTest(self)
        self.result.startTest(self)
        self.result.addSuccess(self)
        self.result.stopTest(self)
        self.assertEqual(
            [{'test': self,
              'status': 'success',
              'start_time': 0,
              'stop_time': 1,
              'tags': set(),
              'details': {'foo': 'bar'}},
             {'test': self,
              'status': 'success',
              'start_time': 2,
              'stop_time': 3,
              'tags': set(),
              'details': None},
             ],
            self.log)


class TestCsvResult(base.TestCase):

    def parse_stream(self, stream):
        stream.seek(0)
        reader = csv.reader(stream)
        return list(reader)

    def test_csv_output(self):
        stream = compat.StringIO()
        result = pysubunit.test_results.CsvResult(stream)
        if sys.version_info >= (3, 0):
            result._now = iter(range(5)).__next__
        else:
            result._now = iter(range(5)).next
        result.startTestRun()
        result.startTest(self)
        result.addSuccess(self)
        result.stopTest(self)
        result.stopTestRun()
        self.assertEqual(
            [['test', 'status', 'start_time', 'stop_time'],
             [self.id(), 'success', '0', '1'],
             ],
            self.parse_stream(stream))

    def test_just_header_when_no_tests(self):
        stream = compat.StringIO()
        result = pysubunit.test_results.CsvResult(stream)
        result.startTestRun()
        result.stopTestRun()
        self.assertEqual(
            [['test', 'status', 'start_time', 'stop_time']],
            self.parse_stream(stream))

    def test_no_output_before_events(self):
        stream = compat.StringIO()
        pysubunit.test_results.CsvResult(stream)
        self.assertEqual([], self.parse_stream(stream))
