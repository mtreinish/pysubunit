#!/usr/bin/env python
# Copyright (C) 200-2013  Robert Collins <robertc@robertcollins.net>
# Copyright (C) 2009  Martin Pool
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""Filter a subunit stream to include/exclude tests.

The default is to strip successful tests.

Tests can be filtered by Python regular expressions with --with and --without,
which match both the test name and the error text (if any).  The result
contains tests which match any of the --with expressions and none of the
--without expressions.  For case-insensitive matching prepend '(?i)'.
Remember to quote shell metacharacters.
"""

import optparse
import re
import sys

import testtools

import pysubunit
from pysubunit import filters
from pysubunit import test_results


def make_options(description):
    parser = optparse.OptionParser(description=__doc__)
    parser.add_option("--error", action="store_false",
                      help="include errors", default=False, dest="error")
    parser.add_option("-e", "--no-error", action="store_true",
                      help="exclude errors", dest="error")
    parser.add_option("--failure", action="store_false",
                      help="include failures", default=False, dest="failure")
    parser.add_option("-f", "--no-failure", action="store_true",
                      help="exclude failures", dest="failure")
    parser.add_option("--passthrough", action="store_false",
                      help="Forward non-subunit input as 'stdout'.",
                      default=False, dest="no_passthrough")
    parser.add_option("--no-passthrough", action="store_true",
                      help="Discard all non subunit input.", default=False,
                      dest="no_passthrough")
    parser.add_option("-s", "--success", action="store_false",
                      help="include successes", dest="success")
    parser.add_option("--no-success", action="store_true",
                      help="exclude successes", default=True, dest="success")
    parser.add_option("--no-skip", action="store_true",
                      help="exclude skips", dest="skip")
    parser.add_option("--xfail", action="store_false",
                      help="include expected failures", default=True,
                      dest="xfail")
    parser.add_option("--no-xfail", action="store_true",
                      help="exclude expected failures", default=True,
                      dest="xfail")
    parser.add_option("--with-tag", type=str,
                      help="include tests with these tags", action="append",
                      dest="with_tags")
    parser.add_option("--without-tag", type=str,
                      help="exclude tests with these tags", action="append",
                      dest="without_tags")
    parser.add_option("-m", "--with", type=str,
                      help="regexp to include (case-sensitive by default)",
                      action="append", dest="with_regexps")
    parser.add_option("--fixup-expected-failures", type=str,
                      help="File with list of test ids that are expected to "
                           "fail; on failure their result will be changed "
                           "to xfail; on success they will be changed to "
                           "error.",
                      dest="fixup_expected_failures", action="append")
    parser.add_option("--without", type=str,
                      help="regexp to exclude (case-sensitive by default)",
                      action="append", dest="without_regexps")
    parser.add_option("-F", "--only-genuine-failures", action="callback",
                      callback=only_genuine_failures_callback,
                      help="Only pass through failures and exceptions.")
    return parser


def only_genuine_failures_callback(option, opt, value, parser):
    parser.rargs.insert(0, '--no-passthrough')
    parser.rargs.insert(0, '--no-xfail')
    parser.rargs.insert(0, '--no-skip')
    parser.rargs.insert(0, '--no-success')


def _compile_re_from_list(l):
    return re.compile("|".join(l), re.MULTILINE)


def _make_regexp_filter(with_regexps, without_regexps):
    """Make a callback that checks tests against regexps.

    with_regexps and without_regexps are each either a list of regexp strings,
    or None.
    """
    with_re = with_regexps and _compile_re_from_list(with_regexps)
    without_re = without_regexps and _compile_re_from_list(without_regexps)

    def check_regexps(test, outcome, err, details, tags):
        """Check if this test and error match the regexp filters."""
        test_str = str(test) + outcome + str(err) + str(details)
        if with_re and not with_re.search(test_str):
            return False
        if without_re and without_re.search(test_str):
            return False
        return True
    return check_regexps


def _make_result(output, options, predicate):
    """Make the result that we'll send the test outcomes to."""
    fixup_expected_failures = set()
    for path in options.fixup_expected_failures or ():
        fixup_expected_failures.update(pysubunit.read_test_list(path))
    return testtools.StreamToExtendedDecorator(test_results.TestResultFilter(
        testtools.ExtendedToStreamDecorator(
            pysubunit.StreamResultToBytes(output)),
        filter_error=options.error,
        filter_failure=options.failure,
        filter_success=options.success,
        filter_skip=options.skip,
        filter_xfail=options.xfail,
        filter_predicate=predicate,
        fixup_expected_failures=fixup_expected_failures))


def main():
    parser = make_options(__doc__)
    (options, args) = parser.parse_args()

    regexp_filter = _make_regexp_filter(
        options.with_regexps, options.without_regexps)
    tag_filter = test_results.make_tag_filter(
        options.with_tags, options.without_tags)
    filter_predicate = test_results.and_predicates(
        [regexp_filter, tag_filter])

    filters.filter_by_result(
        lambda output_to: _make_result(sys.stdout, options, filter_predicate),
        output_path=None,
        passthrough=(not options.no_passthrough),
        forward=False,
        protocol_version=2,
        input_stream=filters.find_stream(sys.stdin, args))
    sys.exit(0)


if __name__ == '__main__':
    main()
