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

"""Convert a version 1 subunit stream to version 2 stream."""

from optparse import OptionParser
import sys

import testtools

import pysubunit
from pysubunit import filters


def make_options(description):
    parser = OptionParser(description=__doc__)
    return parser


def main():
    parser = make_options(__doc__)
    (options, args) = parser.parse_args()
    filters.run_tests_from_stream(
        filters.find_stream(sys.stdin, args),
        testtools.ExtendedToStreamDecorator(
            pysubunit.StreamResultToBytes(sys.stdout)))
    sys.exit(0)


if __name__ == '__main__':
    main()
