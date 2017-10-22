# Copyright (C) 2005  Robert Collins <robertc@robertcollins.net>
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


"""Handlers for outcome details."""

import io

import six
import testtools

from pysubunit import chunked

end_marker = six.binary_type("]\n")
quoted_marker = six.binary_type(" ]")
empty = six.binary_type('')


class DetailsParser(object):
    """Base class/API reference for details parsing."""


class SimpleDetailsParser(DetailsParser):
    """Parser for single-part [] delimited details."""

    def __init__(self, state):
        self._message = six.binary_type("")
        self._state = state

    def lineReceived(self, line):
        if line == end_marker:
            self._state.endDetails()
            return
        if line[0:2] == quoted_marker:
            # quoted ] start
            self._message += line[1:]
        else:
            self._message += line

    def get_details(self, style=None):
        result = {}
        if not style:
            # We know that subunit/testtools serialise [] formatted
            # tracebacks as utf8, but perhaps we need a ReplacingContent
            # or something like that.
            result['traceback'] = testtools.content.Content(
                testtools.content_type.ContentType("text", "x-traceback",
                                                   {"charset": "utf8"}),
                lambda: [self._message])
        else:
            if style == 'skip':
                name = 'reason'
            else:
                name = 'message'
            result[name] = testtools.content.Content(
                testtools.content_type.ContentType("text", "plain"),
                lambda: [self._message])
        return result

    def get_message(self):
        return self._message


class MultipartDetailsParser(DetailsParser):
    """Parser for multi-part [] surrounded MIME typed chunked details."""

    def __init__(self, state):
        self._state = state
        self._details = {}
        self._parse_state = self._look_for_content

    def _look_for_content(self, line):
        if line == end_marker:
            self._state.endDetails()
            return
        field, value = line[:-1].decode('utf8').split(' ', 1)
        try:
            main, sub = value.split('/')
        except ValueError:
            raise ValueError("Invalid MIME type %r" % value)
        self._content_type = testtools.content_type.ContentType(main, sub)
        self._parse_state = self._get_name

    def _get_name(self, line):
        self._name = line[:-1].decode('utf8')
        self._body = io.BytesIO()
        self._chunk_parser = chunked.Decoder(self._body)
        self._parse_state = self._feed_chunks

    def _feed_chunks(self, line):
        residue = self._chunk_parser.write(line)
        if residue is not None:
            # Line based use always ends on no residue.
            assert residue == empty, 'residue: %r' % (residue,)
            body = self._body
            self._details[self._name] = testtools.content.Content(
                self._content_type, lambda: [body.getvalue()])
            self._chunk_parser.close()
            self._parse_state = self._look_for_content

    def get_details(self, for_skip=False):
        return self._details

    def get_message(self):
        return None

    def lineReceived(self, line):
        self._parse_state(line)
