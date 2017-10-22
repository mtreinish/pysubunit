#!/usr/bin/env python
# Copyright (C) 2013  Robert Collins <robertc@robertcollins.net>
#
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

"""Convert a version 2 subunit stream to a version 1 stream."""

import optparse
import sys

import testtools

import pysubunit
from pysubunit import filters
from pysubunit import test_results


def make_options(description):
    parser = optparse.OptionParser(description=__doc__)
    return parser


def main():
    parser = make_options(__doc__)
    (options, args) = parser.parse_args()
    case = pysubunit.ByteStreamToStreamResult(
        filters.find_stream(sys.stdin, args), non_subunit_name='stdout')
    result = testtools.StreamToExtendedDecorator(
        pysubunit.decoratedTestProtocolClient(sys.stdout))
    result = testtools.StreamResultRouter(result)
    cat = test_results.CatFiles(sys.stdout)
    result.add_rule(cat, 'test_id', test_id=None)
    result.startTestRun()
    case.run(result)
    result.stopTestRun()
    sys.exit(0)


if __name__ == '__main__':
    main()
