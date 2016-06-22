import unittest

import rubepl.encode

class Encoding(unittest.TestCase):

    def test_encode_line(self):
        assert 'test' == rubepl.encode.encode_line('test   ')
        # '123 ' in utf16
        utf16 = bytearray([49,0,50,0,51,0,32,0]).decode('utf-16-le')
        # '123' in utf8
        utf8 = bytearray([49,50,51,]).decode('utf-8')
        assert utf8 == rubepl.encode.encode_line(utf16)

    def test_maybe_add_utf8_bom(self):
        x = rubepl.encode.maybe_add_utf8_bom('123')
        assert '\ufeff123' == rubepl.encode.maybe_add_utf8_bom(x)

if __name__ == '__main__':
    unittest.main()
