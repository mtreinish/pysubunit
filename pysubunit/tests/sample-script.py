#!/usr/bin/env python
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

import sys


if sys.platform == "win32":
    import msvcrt
    import os
    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
if len(sys.argv) == 2:
    # subunit.tests.test_test_protocol.TestExecTestCase.test_sample_method_args
    # uses this code path to be sure that the arguments were passed to
    # sample-script.py
    print("test fail")
    print("error fail")
    sys.exit(0)
print("test old mcdonald")
print("success old mcdonald")
print("test bing crosby")
print("failure bing crosby [")
print("foo.c:53:ERROR invalid state")
print("]")
print("test an error")
print("error an error")
sys.exit(0)
