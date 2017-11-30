#  Copyright (C) 2005  Robert Collins <robertc@robertcollins.net>
#  Copyright (C) 2011  Martin Pool <mbp@sourcefrog.net>
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

import io
import unittest

import six

import pysubunit.chunked


class TestDecode(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.output = io.BytesIO()
        self.decoder = pysubunit.chunked.Decoder(self.output)

    def test_close_read_length_short_errors(self):
        self.assertRaises(ValueError, self.decoder.close)

    def test_close_body_short_errors(self):
        self.assertEqual(None, self.decoder.write(six.binary_type('2\r\na')))
        self.assertRaises(ValueError, self.decoder.close)

    def test_close_body_buffered_data_errors(self):
        self.assertEqual(None, self.decoder.write(six.binary_type('2\r')))
        self.assertRaises(ValueError, self.decoder.close)

    def test_close_after_finished_stream_safe(self):
        self.assertEqual(None, self.decoder.write(six.binary_type('2\r\nab')))
        self.assertEqual(six.binary_type(''),
                         self.decoder.write(six.binary_type('0\r\n')))
        self.decoder.close()

    def test_decode_nothing(self):
        self.assertEqual(six.binary_type(''),
                         self.decoder.write(six.binary_type('0\r\n')))
        self.assertEqual(six.binary_type(''), self.output.getvalue())

    def test_decode_serialised_form(self):
        self.assertEqual(None, self.decoder.write(six.binary_type("F\r\n")))
        self.assertEqual(None,
                         self.decoder.write(six.binary_type("serialised\n")))
        self.assertEqual(six.binary_type(''),
                         self.decoder.write(six.binary_type("form0\r\n")))

    def test_decode_short(self):
        self.assertEqual(six.binary_type(''),
                         self.decoder.write(six.binary_type('3\r\nabc0\r\n')))
        self.assertEqual(six.binary_type('abc'), self.output.getvalue())

    def test_decode_combines_short(self):
        self.assertEqual(six.binary_data(''),
                         self.decoder.write(six.binary_data(
                             '6\r\nabcdef0\r\n')))
        self.assertEqual(six.binary_data('abcdef'),
                         self.output.getvalue())

    def test_decode_excess_bytes_from_write(self):
        self.assertEqual(six.binary_data('1234'),
                         self.decoder.write(six.binary_data(
                             '3\r\nabc0\r\n1234')))
        self.assertEqual(six.binary_data('abc'), self.output.getvalue())

    def test_decode_write_after_finished_errors(self):
        self.assertEqual(six.binary_data('1234'),
                         self.decoder.write(six.binary_data(
                             '3\r\nabc0\r\n1234')))
        self.assertRaises(ValueError, self.decoder.write, six.binary_data(''))

    def test_decode_hex(self):
        self.assertEqual(six.binary_data(''),
                         self.decoder.write(six.binary_data(
                             'A\r\n12345678900\r\n')))
        self.assertEqual(six.binary_data('1234567890'), self.output.getvalue())

    def test_decode_long_ranges(self):
        self.assertEqual(None,
                         self.decoder.write(six.binary_data('10000\r\n')))
        self.assertEqual(None,
                         self.decoder.write(six.binary_data('1' * 65536)))
        self.assertEqual(None,
                         self.decoder.write(six.binary_data('10000\r\n')))
        self.assertEqual(None,
                         self.decoder.write(six.binary_data('2' * 65536)))
        self.assertEqual(six.binary_data(''),
                         self.decoder.write(six.binary_data('0\r\n')))
        self.assertEqual(six.binary_data('1' * 65536 + '2' * 65536),
                         self.output.getvalue())

    def test_decode_newline_nonstrict(self):
        """Tolerate chunk markers with no CR character."""
        # From <http://pad.lv/505078>
        self.decoder = pysubunit.chunked.Decoder(self.output, strict=False)
        self.assertEqual(None, self.decoder.write(six.binary_data('a\n')))
        self.assertEqual(None,
                         self.decoder.write(six.binary_data('abcdeabcde')))
        self.assertEqual(six.binary_data(''),
                         self.decoder.write(six.binary_data('0\n')))
        self.assertEqual(six.binary_data('abcdeabcde'), self.output.getvalue())

    def test_decode_strict_newline_only(self):
        """Reject chunk markers with no CR character in strict mode."""
        # From <http://pad.lv/505078>
        self.assertRaises(ValueError,
                          self.decoder.write, six.binary_data('a\n'))

    def test_decode_strict_multiple_crs(self):
        self.assertRaises(ValueError,
                          self.decoder.write, six.binary_data('a\r\r\n'))

    def test_decode_short_header(self):
        self.assertRaises(ValueError,
                          self.decoder.write, six.binary_data('\n'))


class TestEncode(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.output = io.BytesIO()
        self.encoder = pysubunit.chunked.Encoder(self.output)

    def test_encode_nothing(self):
        self.encoder.close()
        self.assertEqual(six.binary_data('0\r\n'), self.output.getvalue())

    def test_encode_empty(self):
        self.encoder.write(six.binary_data(''))
        self.encoder.close()
        self.assertEqual(six.binary_data('0\r\n'), self.output.getvalue())

    def test_encode_short(self):
        self.encoder.write(six.binary_data('abc'))
        self.encoder.close()
        self.assertEqual(six.binary_data('3\r\nabc0\r\n'),
                         self.output.getvalue())

    def test_encode_combines_short(self):
        self.encoder.write(six.binary_data('abc'))
        self.encoder.write(six.binary_data('def'))
        self.encoder.close()
        self.assertEqual(six.binary_data('6\r\nabcdef0\r\n'),
                         self.output.getvalue())

    def test_encode_over_9_is_in_hex(self):
        self.encoder.write(six.binary_data('1234567890'))
        self.encoder.close()
        self.assertEqual(six.binary_data('A\r\n12345678900\r\n'),
                         self.output.getvalue())

    def test_encode_long_ranges_not_combined(self):
        self.encoder.write(six.binary_data('1' * 65536))
        self.encoder.write(six.binary_data('2' * 65536))
        self.encoder.close()
        self.assertEqual(
            six.binary_data('10000\r\n' + '1' * 65536 + '10000\r\n' +
                            '2' * 65536 + '0\r\n'), self.output.getvalue())
