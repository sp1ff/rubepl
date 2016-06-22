import unittest

import rubepl.decode

class Decoding(unittest.TestCase):

    def test_encode_track_location(self):

        TRACK1 = 'file:///mnt/Took-Hall/mp3/H-I/Hunters%20&amp;%20Collectors%20-%20Throw%20Your%20Arms%20Around%20Me.mp3'
        TRACK2 = 'file:///&lt;&gt;&amp;&quot;&apos;%20&lt;&gt;&amp;&quot;&apos;'

        x = rubepl.decode.decode_track_location(TRACK1)
        assert '/mnt/Took-Hall/mp3/H-I/Hunters & Collectors - Throw Your Arms Around Me.mp3' == x

        x = rubepl.decode.decode_track_location(TRACK2)
        assert '/<>&"\' <>&"\'' == x

    def test_maybe_remove_bom(self):

        assert '123' == rubepl.decode.maybe_remove_bom('\ufeff123')
        assert '123' == rubepl.decode.maybe_remove_bom('123')


if __name__ == '__main__':
    unittest.main()
