#!/usr/bin/env python
# Copyright (C) 2008  Robert Collins <robertc@robertcollins.net>
#
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

"""List tests in a subunit stream."""

import optparse
import sys

import testtools

import pysubunit
from pysubunit import filters
from pysubunit import test_results


def main():
    parser = optparse.OptionParser(description=__doc__)
    parser.add_option(
        "--times", action="store_true",
        help="list the time each test took (requires a timestamped stream)",
        default=False)
    parser.add_option(
        "--exists", action="store_true",
        help="list tests that are reported as existing (as well as ran)",
        default=False)
    parser.add_option(
        "--no-passthrough", action="store_true",
        help="Hide all non subunit input.", default=False,
        dest="no_passthrough")
    (options, args) = parser.parse_args()
    test = pysubunit.ByteStreamToStreamResult(
        filters.find_stream(sys.stdin, args), non_subunit_name="stdout")
    result = test_results.TestIdPrintingResult(sys.stdout,
                                               options.times,
                                               options.exists)
    if not options.no_passthrough:
        result = testtools.StreamResultRouter(result)
        cat = test_results.CatFiles(sys.stdout)
        result.add_rule(cat, 'test_id', test_id=None)
    summary = testtools.StreamSummary()
    result = testtools.CopyStreamResult([result, summary])
    result.startTestRun()
    test.run(result)
    result.stopTestRun()
    if summary.wasSuccessful():
        exit_code = 0
    else:
        exit_code = 1
    sys.exit(exit_code)

if __name__ == 'main':
    main()
