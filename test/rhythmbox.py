"""Unit tests for the rubepl.rhythmbox module"""

import os
import shutil
import tempfile
import unittest

import rubepl.rhythmbox

from test.utils import captured_output

class Fixture(unittest.TestCase):

    _DB = 'test/resources/rhythmbox/rhythmdb.xml'
    _PL = 'test/resources/rhythmbox/playlists.xml'

    _ATHENS = """#EXTM3U
#EXTINF:218,Matthew Sweet - Where You Get Love
/mnt/Took-Hall/mp3/M/Matthew Sweet - Where You Get Love.mp3
#EXTINF:230,Alanis Morissette - Hands Clean
/mnt/Took-Hall/mp3/0-A/Alanis  Morissette - Hands Clean.mp3
#EXTINF:307,Jane's Addiction - Classic Girl
/mnt/Took-Hall/mp3/J-K/Jane's Addiction - Classic Girl.mp3
#EXTINF:215,The Jam - The Bitterest Pill
/mnt/Took-Hall/mp3/J-K/Jam, The - The Bitterest Pill.mp3
#EXTINF:148,Amps, The - Pacer
/mnt/Took-Hall/mp3/0-A/Amps, The - Pacer.mp3
#EXTINF:213,Breeders, The - Cannonball
/mnt/Took-Hall/mp3/B/Breeders, The - Cannonball.mp3
#EXTINF:241,Buffalo Tom - Summer
/mnt/Took-Hall/mp3/B/Buffalo Tom - Summer.mp3
#EXTINF:296,Talking Heads - This Must be the Place (Naive
/mnt/Took-Hall/mp3/T/Talking Heads - This Must Be The Place (Naive Melody).mp3
#EXTINF:250,Hunters & Collectors - Throw Your Arms Around Me
/mnt/Took-Hall/mp3/H-I/Hunters & Collectors - Throw Your Arms Around Me.mp3
#EXTINF:354,Guns N' Roses - Sweet Child O' Mine
/mnt/Took-Hall/mp3/G/Guns N' Roses - Sweet Child O' Mine (LP Version).mp3
#EXTINF:260,Luscious Jackson - Citysong
/mnt/Took-Hall/mp3/L/Luscious Jackson - Citysong.mp3
#EXTINF:161,La's, The - There She Goes
/mnt/Took-Hall/mp3/L/La's, The - There She Goes.mp3
#EXTINF:208,Clash, The - Rudy Can't Fail
/mnt/Took-Hall/mp3/C/Clash, The - Rudy Can't Fail.mp3
#EXTINF:172,Frank Black & The Catholics - Smoke Up
/mnt/Took-Hall/mp3/F/Frank Black & The Catholics - Smoke Up.mp3
#EXTINF:190,Led Zeppelin - Tangerine
/mnt/Took-Hall/mp3/L/Led Zeppelin - Tangerine.mp3
#EXTINF:271,Primitive Radio Gods - Standing Outside a Phonebooth
/mnt/Took-Hall/mp3/P/Primitive Radio Gods - Standing Outside.mp3
#EXTINF:353,Peter Murphy - Indigo Eyes
/mnt/Took-Hall/mp3/P/Peter Murphy - Indigo Eyes.mp3
#EXTINF:163,Guadalcanal Diary - Trail Of Tears
/mnt/Took-Hall/mp3/G/Guadalcanal Diary - Trail Of Tears.mp3
#EXTINF:284,Sundays - Goodbye
/mnt/Took-Hall/mp3/Sm-Sz/Sundays - Goodbye.mp3
"""

    _FALL = """#EXTM3U
#EXTINF:262,Mary Black - The Loving Time
/mnt/Took-Hall/mp3/M/Mary Black - The Loving Time.mp3
#EXTINF:185,Vienna Teng - Anna Rose
/mnt/Took-Hall/mp3/U-Z/Vienna Teng - Anna Rose.mp3
#EXTINF:237,Lunasa - Glentrasna
/mnt/Took-Hall/mp3/L/Lunasa - Glentrasna.mp3
#EXTINF:189,Mary Black - The Fog In Monterey
/mnt/Took-Hall/mp3/M/Mary Black - The Fog In Monterey.mp3
#EXTINF:215,Matt Nathanson - Come On Get Higher
/mnt/Took-Hall/mp3/N-O/Matt Nathanson - Come On Get Higher.mp3
#EXTINF:221,Five For Fighting - Superman (It's Not Easy) (New Album Version)
/mnt/Took-Hall/mp3/F/Five for Fighting - Superman (It's Not Easy) (New Album Version).mp3
#EXTINF:188,String Sisters - The Fly And Dodger
/mnt/Took-Hall/mp3/Sm-Sz/String Sisters - The Fly And Dodger.mp3
#EXTINF:281,The Pogues - Lorca's Novena
/mnt/Took-Hall/mp3/P/Pogues, The - Lorcas Novena
#EXTINF:328,Tori Amos - A Sorta Fairytale (Album Version)
/mnt/Took-Hall/mp3/T/Tori Amos - A Sorta Fairytale (Album Version).mp3
#EXTINF:190,Led Zeppelin - Tangerine
/mnt/Took-Hall/mp3/L/Led Zeppelin - Tangerine.mp3
#EXTINF:293,Mazzy Star - Take Everything
/mnt/Took-Hall/mp3/M/Mazzy Star - Take Everything.mp3
#EXTINF:286,Led Zeppelin - Over The Hills And Far Away
/mnt/Took-Hall/mp3/L/Led Zeppelin - Over The Hills And Far Away.mp3
#EXTINF:287,Mazzy Star - Look On Down From The Bridge
/mnt/Took-Hall/mp3/M/Mazzy Star - Look On Down From The Bridge.mp3
#EXTINF:264,Groove Armada - Hands Of Time
/mnt/Took-Hall/mp3/G/Groove Armada - Hands Of Time.mp3
#EXTINF:613,Pat Metheny Group - San Lorenzo
/mnt/Took-Hall/mp3/P/Pat Metheny Group, The - San Lorenzo.mp3
#EXTINF:240,Tori Amos - Taxi Ride (Album Version)
/mnt/Took-Hall/mp3/T/Tori Amos - Taxi Ride.mp3
#EXTINF:225,The Ocean Blue - Questions Of Travel (LP Version)
/mnt/Took-Hall/mp3/C/Cerulean - Questions Of Travel (LP Version).mp3
#EXTINF:363,William Tyler - Missionary Ridge
/mnt/Took-Hall/mp3/U-Z/William Tyler - Missionary Ridge.mp3
#EXTINF:191,Steve Earle - Lonelier Than This
/mnt/Took-Hall/mp3/Sm-Sz/Steve Earle - Lonelier Than This.mp3
#EXTINF:202,Thulla - Where Ur Buddha Live
/mnt/Took-Hall/mp3/T/Thulla-Where Ur Buddha Live.mp3
#EXTINF:246,Five For Fighting - 100 Years (Album Version)
/mnt/Took-Hall/mp3/F/Five for Fighting - 100 Years.mp3
#EXTINF:262,Angels and Airwaves - Rite Of Spring
/mnt/Took-Hall/mp3/0-A/Angels and Airwaves - Rite Of Spring.mp3
#EXTINF:234,The Ocean Blue - Ballerina Out Of Control (LP Version)
/mnt/Took-Hall/mp3/C/Cerulean - Ballerina Out Of Control (LP Version).mp3
#EXTINF:247,P!nk - Try
/mnt/Took-Hall/mp3/P/Pink - Try.mp3
#EXTINF:297,Mazzy Star - Flowers In December
/mnt/Took-Hall/mp3/M/Mazzy Star - Flowers In December.mp3
#EXTINF:242,P!nk feat. Nate Ruess - Just Give Me a Reason
/mnt/Took-Hall/mp3/P/Pink - Just Give Me a Reason.mp3
#EXTINF:246,Yo La Tengo - Drug Test
/mnt/Took-Hall/mp3/U-Z/Yo La Tengo - Drug Test.mp3
#EXTINF:372,Martyn Bennett - Blackbird
/mnt/Took-Hall/mp3/M/Martyn Bennett - Blackbird.mp3
#EXTINF:234,Stevie Nicks & Don Henley - Leather And Lace
/mnt/Took-Hall/mp3/Sm-Sz/Stevey Nicks - Leather And Lace.mp3
#EXTINF:538,Pearl Jam - Release (Brendan O'Brien Mix)
/mnt/Took-Hall/mp3/P/Pearl Jam - Release.mp3
#EXTINF:230,Dixie Chicks - Landslide (Album Version) [Clean]
/mnt/Took-Hall/mp3/D/Dixie Chicks - Landslide (Album Version) .mp3
#EXTINF:344,Dixie Chicks - Travelin' Soldier (Album Version) [Clean]
/mnt/Took-Hall/mp3/D/Dixie Chicks - Travelin' Soldier (Album Version) .mp3
#EXTINF:238,The Ocean Blue - Cerulean (LP Version)
/mnt/Took-Hall/mp3/C/Cerulean - Cerulean (LP Version).mp3
#EXTINF:186,The Ocean Blue - Marigold (LP Version)
/mnt/Took-Hall/mp3/C/Cerulean - Marigold (LP Version).mp3
#EXTINF:252,The Ocean Blue - Mercury (LP Version)
/mnt/Took-Hall/mp3/C/Cerulean - Mercury (LP Version).mp3
#EXTINF:244,Mazzy Star - Disappear
/mnt/Took-Hall/mp3/M/Mazzy Star - Disappear.mp3
#EXTINF:238,Mazzy Star - Cry, Cry
/mnt/Took-Hall/mp3/M/Mazzy Star - Cry, Cry.mp3
#EXTINF:197,Mazzy Star - I've Been Let Down
/mnt/Took-Hall/mp3/M/Mazzy Star - Ive Been Let Down.mp3
#EXTINF:193,Tom Waits - Never Let Go
/mnt/Took-Hall/mp3/T/Tom Waits - Never Let Go.mp3
"""

    def setUp(self):
        self._tmp = tempfile.mkdtemp()
        self._db = os.path.join(os.getcwd(), self._DB)
        self._pl = os.path.join(os.getcwd(), self._PL)

    def tearDown(self):
        shutil.rmtree(self._tmp)

    def test_build_db(self):
        """Exercise rubepl.rhythmbox.build_db"""

        db = rubepl.rhythmbox.build_db(self._db)
        assert 6046 == len(db)
        assert (392, 'Tom Harrell', 'Opaling') == db['/mnt/Took-Hall/mp3/T/Tom Harrell - Opaling.mp3']

    def test_get_playlists(self):
        """Exercise rubepl.rhythmbox.get_playlists"""

        pls = rubepl.rhythmbox.get_playlists(self._pl)
        assert 2 == len(pls)
        (title, tracks) = pls[0]
        assert 'Athens 2002' == title
        assert 19 == len(tracks)

    def test_playlists_xml_to_m3u(self):
        """Exercise rubepl.rhythmbox.playlists_xml_to_m3u"""

        rubepl.rhythmbox.playlists_xml_to_m3u(self._pl, self._db,
                                              output=self._tmp)
        with open(os.path.join(self._tmp, 'Athens 2002.m3u'), 'r') as fh:
            text = fh.read()
            assert text == self._ATHENS
        with open(os.path.join(self._tmp, 'Fall 2013.m3u'), 'r') as fh:
            text = fh.read()
            assert text == self._FALL

    def test_playlists_xml_to_m3u_cmd(self):
        """Exercise the get-playlists-xml sub-command"""

        args = ['get-playlists-xml', '-o', self._tmp,
                '-y', 'Athens 2002', self._db, self._pl]
        with captured_output() as (out, err):
            status = rubepl.main(args)
        print(out.getvalue().strip())
        print(err.getvalue().strip())
        with open(os.path.join(self._tmp, 'Athens 2002.m3u'), 'r') as fh:
            text = fh.read()
            assert text == self._ATHENS
