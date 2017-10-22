#!/usr/bin/env python
# Copyright (C) 2009  Robert Collins <robertc@robertcollins.net>
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


"""A filter to change tags on a subunit stream.

subunit-tags foo -> adds foo
subunit-tags foo -bar -> adds foo and removes bar
"""

import sys

import pysubunit


def main():
    sys.exit(pysubunit.tag_stream(sys.stdin, sys.stdout, sys.argv[1:]))

if __name__ == 'main':
    main()
