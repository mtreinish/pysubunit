#!/usr/bin/env python
# Copyright (C) 2009  Robert Collins <robertc@robertcollins.net>
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

"""Filter a subunit stream to get aggregate statistics."""


import sys

import testtools

from pysubunit import filters


try:
    from junitxml import JUnitXmlResult
except ImportError:
    sys.stderr.write(
        "python-junitxml (https://launchpad.net/pyjunitxml or "
        "http://pypi.python.org/pypi/junitxml) is required for this filter.")
    raise


def main():
    filters.run_filter_script(
        lambda output: testtools.StreamToExtendedDecorator(
            JUnitXmlResult(output)),
        __doc__,
        protocol_version=2)
