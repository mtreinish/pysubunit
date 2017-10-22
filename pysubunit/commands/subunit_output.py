#!/usr/bin/env python
# Copyright (C) 2013 Subunit Contributors
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


"""A command-line tool to generate a subunit result byte-stream."""

import sys

from pysubunit import _output


def main():
    sys.exit(_output.output_main())

if __name__ == '__main__':
    main()
