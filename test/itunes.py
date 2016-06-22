"""Unit tests for the rubepl.itunes module"""

import logging
import os
import shutil
import tempfile
import unittest

import rubepl.itunes

from test.utils import captured_output

class Fixture(unittest.TestCase):

    _ML1 = os.path.join(os.getcwd(), 'test/resources/iTunes/itunes-music-library-1.xml')
    _PL1 = os.path.join(os.getcwd(), 'test/resources/iTunes/Fall 2013.m3u')
    _PL2 = os.path.join(os.getcwd(), 'test/resources/iTunes/Spring 2010.m3u')
    _PL3 = os.path.join(os.getcwd(), 'test/resources/iTunes/Summer 2007.m3u')

    _JIN1 = """#EXTM3U
#EXTINF:262,Mary Black - Mary Black - The Loving Time
/Users/mgh/Music/iTunes/iTunes Media/Music/Noel Brazil/The Loving Time/14 The Loving Time.mp3
#EXTINF:185,Vienna Teng - Vienna Teng - Anna Rose
/Users/mgh/Music/iTunes/iTunes Media/Music/Vienna Teng/Warm Strangers/09 Anna Rose.mp3
#EXTINF:237,Lunasa - Lunasa - Glentrasna
/Users/mgh/Music/iTunes/iTunes Media/Music/Lunasa/Sé/10 Glentrasna.mp3
#EXTINF:189,Mary Black - Mary Black - The Fog In Monterey
/Users/mgh/Music/iTunes/iTunes Media/Music/Mary Black/No Frontiers/11 The Fog In Monterey.mp3
#EXTINF:309,Rolling Stones, The - Rolling Stones, The - Wild Horses
/Users/mgh/Music/iTunes/iTunes Media/Music/Unknown Artist/Unknown Album/Rolling Stones, The - Wild Horses.mp3
#EXTINF:344,Dixie Chicks - Dixie Chicks - Travelin' Soldier (Album Version) [Clean]
/Users/mgh/Music/iTunes/iTunes Media/Music/Dixie Chicks/Home [Clean]/03 Travelin' Soldier (Album Version) [Clean].mp3
#EXTINF:264,Groove Armada - Groove Armada - Hands Of Time
/Users/mgh/Music/iTunes/iTunes Media/Music/Assorted/iTunes Stuff/01 Hands Of Time.mp3
#EXTINF:328,Tori Amos - Tori Amos - A Sorta Fairytale (Album Version)
/Users/mgh/Music/iTunes/iTunes Media/Music/Tori Amos/Scarlet's Walk/02 A Sorta Fairytale (Album Version).mp3
#EXTINF:240,Tori Amos - Tori Amos - Taxi Ride (Album Version)
/Users/mgh/Music/iTunes/iTunes Media/Music/Tori Amos/Scarlet's Walk/14 Taxi Ride (Album Version).mp3
#EXTINF:234,Stevie Nicks & Don Henley - Stevie Nicks & Don Henley - Leather And Lace
/Users/mgh/Music/iTunes/iTunes Media/Music/Stevie Nicks/Bella Donna (US Release)/08 Leather And Lace.mp3
#EXTINF:221,Five For Fighting - Five For Fighting - Superman (It's Not Easy) (New Album Version)
/Users/mgh/Music/iTunes/iTunes Media/Music/Five For Fighting/America Town/03 Superman (It's Not Easy) (New Album Version).mp3
#EXTINF:215,Matt Nathanson - Matt Nathanson - Come On Get Higher
/Users/mgh/Music/iTunes/iTunes Media/Music/Matt Nathanson/Some Mad Hope/02 Come On Get Higher.mp3
#EXTINF:188,String Sisters - String Sisters - The Fly And Dodger
/Users/mgh/Music/iTunes/iTunes Media/Music/String Sisters/Live/10 The Fly And Dodger.mp3
#EXTINF:363,William Tyler - William Tyler - Missionary Ridge
/Users/mgh/Music/iTunes/iTunes Media/Music/William Tyler/Behold The Spirit/02 Missionary Ridge.mp3
#EXTINF:202,Thulla - Thulla - Where Ur Buddha Live
/Users/mgh/Music/iTunes/iTunes Media/Music/Thulla/Trip/06 Where Ur Buddha Live.mp3
#EXTINF:613,Pat Metheny Group - Pat Metheny Group - San Lorenzo
/Users/mgh/Music/iTunes/iTunes Media/Music/Pat Metheny Group/Pat Metheny Group/01 San Lorenzo.mp3
#EXTINF:246,Five For Fighting - Five For Fighting - 100 Years (Album Version)
/Users/mgh/Music/iTunes/iTunes Media/Music/Five For Fighting/The Battle For Everything/04 100 Years (Album Version).mp3
#EXTINF:230,Dixie Chicks - Dixie Chicks - Landslide (Album Version) [Clean]
/Users/mgh/Music/iTunes/iTunes Media/Music/Dixie Chicks/Home [Clean]/02 Landslide (Album Version) [Clean].mp3
#EXTINF:238,The Ocean Blue - The Ocean Blue - Cerulean (LP Version)
/Users/mgh/Music/iTunes/iTunes Media/Music/The Ocean Blue/Cerulean (US Release)/02 Cerulean (LP Version).mp3
#EXTINF:186,The Ocean Blue - The Ocean Blue - Marigold (LP Version)
/Users/mgh/Music/iTunes/iTunes Media/Music/The Ocean Blue/Cerulean (US Release)/03 Marigold (LP Version).mp3
#EXTINF:246,The Ocean Blue - The Ocean Blue - A Seperate Reality (LP Version)
/Users/mgh/Music/iTunes/iTunes Media/Music/The Ocean Blue/Cerulean (US Release)/04 A Seperate Reality (LP Version).mp3
#EXTINF:252,The Ocean Blue - The Ocean Blue - Mercury (LP Version)
/Users/mgh/Music/iTunes/iTunes Media/Music/The Ocean Blue/Cerulean (US Release)/05 Mercury (LP Version).mp3
#EXTINF:225,The Ocean Blue - The Ocean Blue - Questions Of Travel (LP Version)
/Users/mgh/Music/iTunes/iTunes Media/Music/The Ocean Blue/Cerulean (US Release)/06 Questions Of Travel (LP Version).mp3
#EXTINF:85,The Ocean Blue - The Ocean Blue - Falling Through The Ice (LP Version)
/Users/mgh/Music/iTunes/iTunes Media/Music/The Ocean Blue/Cerulean (US Release)/09 Falling Through The Ice (LP Version).mp3
#EXTINF:234,The Ocean Blue - The Ocean Blue - Ballerina Out Of Control (LP Version)
/Users/mgh/Music/iTunes/iTunes Media/Music/The Ocean Blue/Cerulean (US Release)/10 Ballerina Out Of Control (LP Version).mp3
#EXTINF:234,The Ocean Blue - The Ocean Blue - I've Sung One Too Many Songs For A Crowd That Didn't Want To Hear (LP Version)
/Users/mgh/Music/iTunes/iTunes Media/Music/The Ocean Blue/Cerulean (US Release)/12 I've Sung One Too Many Songs For A Crowd That Didn't Want To Hear (LP Version).mp3
#EXTINF:244,Mazzy Star - Mazzy Star - Disappear
/Users/mgh/Music/iTunes/iTunes Media/Music/Mazzy Star/Among My Swan/01 Disappear.mp3
#EXTINF:252,Mazzy Star - Mazzy Star - Rhymes Of An Hour
/Users/mgh/Music/iTunes/iTunes Media/Music/Mazzy Star/Among My Swan/03 Rhymes Of An Hour.mp3
#EXTINF:238,Mazzy Star - Mazzy Star - Cry, Cry
/Users/mgh/Music/iTunes/iTunes Media/Music/Mazzy Star/Among My Swan/04 Cry, Cry.mp3
#EXTINF:293,Mazzy Star - Mazzy Star - Take Everything
/Users/mgh/Music/iTunes/iTunes Media/Music/Mazzy Star/Among My Swan/05 Take Everything.mp3
#EXTINF:288,Mazzy Star - Mazzy Star - Still Cold
/Users/mgh/Music/iTunes/iTunes Media/Music/Mazzy Star/Among My Swan/06 Still Cold.mp3
#EXTINF:316,Mazzy Star - Mazzy Star - All Your Sisters
/Users/mgh/Music/iTunes/iTunes Media/Music/Mazzy Star/Among My Swan/07 All Your Sisters.mp3
#EXTINF:197,Mazzy Star - Mazzy Star - I've Been Let Down
/Users/mgh/Music/iTunes/iTunes Media/Music/Mazzy Star/Among My Swan/08 I've Been Let Down.mp3
#EXTINF:297,Mazzy Star - Mazzy Star - Flowers In December
/Users/mgh/Music/iTunes/iTunes Media/Music/Mazzy Star/Among My Swan/02 Flowers In December.mp3
#EXTINF:290,Mazzy Star - Mazzy Star - Rose Blood
/Users/mgh/Music/iTunes/iTunes Media/Music/Mazzy Star/Among My Swan/09 Rose Blood.mp3
#EXTINF:238,Mazzy Star - Mazzy Star - Happy
/Users/mgh/Music/iTunes/iTunes Media/Music/Mazzy Star/Among My Swan/10 Happy.mp3
#EXTINF:287,Mazzy Star - Mazzy Star - Look On Down From The Bridge
/Users/mgh/Music/iTunes/iTunes Media/Music/Mazzy Star/Among My Swan/12 Look On Down From The Bridge.mp3
"""

    _JIN2 = """#EXTM3U
#EXTINF:216,Smiths, The - Smiths, The - Half A Person
/Users/mgh/Music/iTunes/iTunes Media/Music/Smiths, The/Unknown Album/Half A Person.mp3
#EXTINF:158,Smiths, The - Smiths, The - Cemetry Gates
/Users/mgh/Music/iTunes/iTunes Media/Music/Unknown Artist/Unknown Album/Smiths, The - Cemetry Gates.mp3
#EXTINF:233,Dave Matthews Band - Dave Matthews Band - Where Are You Going
/Users/mgh/Music/iTunes/iTunes Media/Music/Dave Matthews Band/Busted Stuff/03 Where Are You Going.mp3
#EXTINF:296,Van Morrison & The Chieftains - Van Morrison & The Chieftains - Raglan Road
/Users/mgh/Music/iTunes/iTunes Media/Music/Van Morrison & The Chieftains/Irish Heartbeat/04 Raglan Road.mp3
#EXTINF:168,Pixes, The - Pixes, The - Bird Dream Of The Olympus Mons
/Users/mgh/Music/iTunes/iTunes Media/Music/Unknown Artist/Unknown Album/Pixies - Bird Dream Of The Olympus Mons.mp3
#EXTINF:288,Morrissey - Morrissey - My Love Life
/Users/mgh/Music/iTunes/iTunes Media/Music/Morrissey/Unknown Album/My Love Life.mp3
#EXTINF:397,Bob Mould - Bob Mould - Brasilia Crossed With Trenton
/Users/mgh/Music/iTunes/iTunes Media/Music/Bob Mould/Unknown Album/Bob Mould - Brasilia Crossed With Trenton.mp3
#EXTINF:223,Goo Goo Dolls - Goo Goo Dolls - Naked
/Users/mgh/Music/iTunes/iTunes Media/Music/Goo Goo Dolls/Unknown Album/Name.mp3
#EXTINF:193,Gin Blossoms - Gin Blossoms - Not Only Numb (Live)
/Users/mgh/Music/iTunes/iTunes Media/Music/Gin Blossoms/Congratulations I'm Sorry/04 Not Only Numb.mp3
#EXTINF:252,Venice Is Sinking - Venice Is Sinking - Pulaski Heights
/Users/mgh/Music/iTunes/iTunes Media/Music/Venice Is Sinking/http___music.download.com/01 Pulaski Heights.mp3
#EXTINF:136,Sundays - Sundays - I Kicked A Boy
/Users/mgh/Music/iTunes/iTunes Media/Music/Sundays/Unknown Album/God Made Me.mp3
#EXTINF:199,Fleetwood Mac - Fleetwood Mac - Landslide
/Users/mgh/Music/iTunes/iTunes Media/Music/Fleetwood Mac/The Chain (Disc 1)/17 Gypsy.mp3
#EXTINF:248,Dillon, Cara - Dillon, Cara - Garden Valley
/Users/mgh/Music/iTunes/iTunes Media/Music/Dillon, Cara/After The Morning/05 Garden Valley.mp3
#EXTINF:187,Jonae' - Jonae' - The Gloaming
/Users/mgh/Music/iTunes/iTunes Media/Music/Jonae'/Into the Blue/08 The Gloaming.mp3
#EXTINF:299,Bruce Springsteen - Bruce Springsteen - The River
/Users/mgh/Music/iTunes/iTunes Media/Music/Bruce Springsteen/Greatest Hits/04 The River.mp3
#EXTINF:284,Sundays - Sundays - Wild Horses
/Users/mgh/Music/iTunes/iTunes Media/Music/Sundays/Unknown Album/Wild Horses.mp3
#EXTINF:279,Better Than Ezra - Better Than Ezra - Rosealia (Naked Disc)
/Users/mgh/Music/iTunes/iTunes Media/Music/Better Than Ezra/Unknown Album/Better Than Ezra - Rosealia (Naked Disc).mp3
#EXTINF:244,Bob Mould - Bob Mould - Vaporub
/Users/mgh/Music/iTunes/iTunes Media/Music/Bob Mould/The Last Dog And Pony Show [Disc 1]/1-08 Vaporub.mp3
#EXTINF:227,Fleetwood Mac - Fleetwood Mac - Say You Will
/Users/mgh/Music/iTunes/iTunes Media/Music/Fleetwood Mac/The Chain (Disc 1)/01 Paper Doll.mp3
#EXTINF:240,Mary Black - Mary Black - No Frontiers
/Users/mgh/Music/iTunes/iTunes Media/Music/Mary Black/iist (Songs In Their Native Language)/10 Mo Ghille Mear.mp3
#EXTINF:242,Dillon, Cara - Dillon, Cara - October Winds
/Users/mgh/Music/iTunes/iTunes Media/Music/Dillon, Cara/After The Morning/05 Garden Valley.mp3
/Users/mgh/Music/iTunes/iTunes Media/Music/Moby/Ambient/02 Heaven.mp3
#EXTINF:273,The Soundtrack of Our Lives - The Soundtrack of Our Lives - Fly
/Users/mgh/Music/iTunes/iTunes Media/Music/The Soundtrack of Our Lives/Communion/1-08 Fly.mp3
"""

    _JIN3 = """#EXTM3U
#EXTINF:311,Chant - Chant - Theme from Harry's Game
/Users/mgh/Music/iTunes/iTunes Media/Music/Various Artists/Night Sessions/08 You Move Me.mp3
#EXTINF:169,Cellophane Rain - Cellophane Rain - Good Morning Light
/Users/mgh/Music/iTunes/iTunes Media/Music/Cocteau Twins/Love's Easy Tears/Orange Appled.mp3
#EXTINF:229,Styrofoam & Sarah Shannon - Styrofoam & Sarah Shannon - I Found Love
/Users/mgh/Music/iTunes/iTunes Media/Music/Star Ghost Dog/Unknown Album/Knock Down.mp3
#EXTINF:376,Bliss - Bliss - Kissing (Album Version)
/Users/mgh/Music/iTunes/iTunes Media/Music/Hanna/Lounge Basics Vol. 1/13 Daysp.mp3
#EXTINF:250,Third Eye Blind - Third Eye Blind - Deep Inside of You
/Users/mgh/Music/iTunes/iTunes Media/Music/Third Eye Blind/Unknown Album/Never Let You Go.mp3
#EXTINF:167,Can't Find the Time To Tell You - Can't Find the Time To Tell You - Hootie & The Blowfish
/Users/mgh/Music/iTunes/iTunes Media/Music/Antônio Carlos Jobim/Tide/Antônio Carlos Jobim - Carinhoso.m4a
#EXTINF:305,Bob Mould - Bob Mould - Days Of Rain
/Users/mgh/Music/iTunes/iTunes Media/Music/Steely Dan/Unknown Album/FM.mp3
#EXTINF:287,Kasey Chambers - Kasey Chambers - Don't Talk Back
/Users/mgh/Music/iTunes/iTunes Media/Music/Lamb/What Sound/Scratch Bass.mp3
#EXTINF:145,Mary Lou Lord - Mary Lou Lord - Cold Kilburn Rain
/Users/mgh/Music/iTunes/iTunes Media/Music/Mary Lou Lord/Baby Blue/05 Cold Kilburn Rain.mp3
#EXTINF:241,Replacements, The - Replacements, The - Unsatisfied
/Users/mgh/Music/iTunes/iTunes Media/Music/Replacements, The/Let It Be/07 Unsatisfied.mp3
#EXTINF:243,Collective Soul - Collective Soul - Dandy Life
/Users/mgh/Music/iTunes/iTunes Media/Music/Pete Yorn/Day I Forgot/12 All At Once.mp3
#EXTINF:214,Frank Black - Frank Black - Speedy Marie
/Users/mgh/Music/iTunes/iTunes Media/Music/Bovine Life/Bip-Hop Generation Vol. 3/04 Ardeonaig.mp3
#EXTINF:213,Tom Wolfe - Tom Wolfe - Where He Can Hide
/Users/mgh/Music/iTunes/iTunes Media/Music/Tom Petty/Greatest Hits/01 American Girl.mp3
#EXTINF:181,Asobi Seksu - Asobi Seksu - New Years
/Users/mgh/Music/iTunes/iTunes Media/Music/R.E.M_/Unknown Album/We Walk.mp3
#EXTINF:202,Thulla - Thulla - Where Ur Buddha Live
/Users/mgh/Music/iTunes/iTunes Media/Music/Thulla/Trip/06 Where Ur Buddha Live.mp3
#EXTINF:253,4our5ive6ix - 4our5ive6ix - 7even8ight
/Users/mgh/Music/iTunes/iTunes Media/Music/4our5ive6ix/Something Light EP/01 7even8ight.mp3
#EXTINF:264,Groove Armada - Groove Armada - Hands Of Time
/Users/mgh/Music/iTunes/iTunes Media/Music/Assorted/iTunes Stuff/01 Hands Of Time.mp3
#EXTINF:250,Sasha - Sasha - Requiem
/Users/mgh/Music/iTunes/iTunes Media/Music/Lamb/What Sound/Just Is.mp3
#EXTINF:393,Groove Armada - Groove Armada - At the River (Old Cape Code)
/Users/mgh/Music/iTunes/iTunes Media/Music/Blamstrain/Ensi/Blamstrain - Alive In Arms.mp3
#EXTINF:249,Lamb - Lamb - Just Is
/Users/mgh/Music/iTunes/iTunes Media/Music/Lamb/What Sound/Just Is.mp3
#EXTINF:435,Caia - Caia - Remembrance
/Users/mgh/Music/iTunes/iTunes Media/Music/Caia/Ultra Chilled 04.2/04 Remembrance.mp3
#EXTINF:324,Funky Procini - Funky Procini - Dubble
/Users/mgh/Music/iTunes/iTunes Media/Music/Funky Procini/Pure Chill Out 2/Dubble.mp3
#EXTINF:319,Lamb - Lamb - Small
/Users/mgh/Music/iTunes/iTunes Media/Music/Lamb/What Sound/Small.mp3
#EXTINF:148,Original Soundtrack - Original Soundtrack - Harry's Game
/Users/mgh/Music/iTunes/iTunes Media/Music/Clannad/Patriot Games/03 Harry's Game.mp3
#EXTINF:219,Thievery Corporation - Thievery Corporation - Shadows Of Ourselves
/Users/mgh/Music/iTunes/iTunes Media/Music/Thievery Corporation/The Mirror Conspiracy/09 Shadows Of Ourselves.mp3
#EXTINF:182,Thievery Corporation - Thievery Corporation - The Hong Kong Triad
/Users/mgh/Music/iTunes/iTunes Media/Music/Thievery Corporation/Sounds From The Thievery Hi-Fi/08 Scene At The Open Air Market.mp3
#EXTINF:212,Collective Soul - Collective Soul - 05 - Slow
/Users/mgh/Music/iTunes/iTunes Media/Music/Collective Soul/Dosage/05 05 - Slow.mp3
#EXTINF:206,James - James - Say Something
/Users/mgh/Music/iTunes/iTunes Media/Music/James/Unknown Album/Say Something.mp3
#EXTINF:244,Kasey Chambers - Kasey Chambers - You Got This Car
/Users/mgh/Music/iTunes/iTunes Media/Music/Kasey Chambers/The Captain/07 Southern Kind Of Life.mp3
#EXTINF:277,Pearl Jam - Pearl Jam - Corduroy
/Users/mgh/Music/iTunes/iTunes Media/Music/Panaphonic/Café Samba 2/11 Sambast.mp3
#EXTINF:257,Gin Blossoms - Gin Blossoms - 29
/Users/mgh/Music/iTunes/iTunes Media/Music/Assorted/iTunes Stuff/12 Cruisin'.mp3
#EXTINF:234,Lemongrass - Lemongrass - La Mer
/Users/mgh/Music/iTunes/iTunes Media/Music/Lemongrass/Pure Chill Out 2/La Mer.mp3
"""

    def _find_difference(self, text, jin):
        import sys

        def print_err(text):
            sys.stderr.write('{0}\n'.format(text))

        ntext = len(text)
        njin = len(jin)
        print_err('\nGolden/test lengths: {0}/{1}'.format(njin, ntext))
        n = ntext if ntext <= njin else njin
        for i in range(n):
            if text[i] != jin[i]:
                print_err('First difference at index {0}: {1}/{2}'.format(i, jin[i], text[i]))
                break

    def setUp(self):
        self._tmp = tempfile.mkdtemp()
        self._ml1 = os.path.join(self._tmp, 'ml1.xml')
        self._pl1 = os.path.join(self._tmp, 'fall-2013.m3u')
        self._pl2 = os.path.join(self._tmp, 'spring-2010.m3u')
        self._pl3 = os.path.join(self._tmp, 'summer-2007.m3u')
        shutil.copyfile(self._ML1, self._ml1)
        shutil.copyfile(self._PL1, self._pl1)
        shutil.copyfile(self._PL2, self._pl2)
        shutil.copyfile(self._PL3, self._pl3)
        logging.getLogger(rubepl.itunes.__name__).setLevel(logging.ERROR)

    def tearDown(self):
        shutil.rmtree(self._tmp)

    def test_build_track_map(self):
        """Exercise itunes.build_track_map"""

        D = rubepl.itunes.build_track_map(self._ml1)
        assert 1687 == len(D.keys())
        assert ('/Users/mgh/Music/iTunes/iTunes Media/Music/The Pogues/' +
                'The Very Best Of The Pogues/07 The Body Of An American.mp3', 291) == \
            D[('Pogues, The', 'The Body Of An American')]

    def test_levenshtein(self):
        """Exercise itunes.levenshtein"""

        assert 0 == rubepl.itunes.levenshtein("aaa", "aaa")
        assert 1 == rubepl.itunes.levenshtein("aaa", "aab")

    def test_extinfo(self):
        """Exercise ExtInfo"""

        ei00 = rubepl.itunes.ExtInf(123, 'Pogues, The - Lorca\'s Novena')
        assert 123 == ei00.get_duration()
        assert ei00.parsed_artist_and_track()
        assert 'Pogues, The' == ei00.get_artist()
        assert 'Lorca\'s Novena' == ei00.get_track()
        assert 'Pogues, The - Lorca\'s Novena' == ei00.get_title()

    def test_find_best_match(self):
        """Exercise itunes.find_best_match"""

        D = rubepl.itunes.build_track_map(self._ml1)

        m = rubepl.itunes.find_best_match(D, 'The Pogues', 'The Body of An American', 291)
        assert m ==  '/Users/mgh/Music/iTunes/iTunes Media/Music/The Pogues/The Very Best Of The Pogues/07 The Body Of An American.mp3'

        m = rubepl.itunes.find_best_match(D, 'Pogues, The', 'The Body of An American', 291)
        assert m ==  '/Users/mgh/Music/iTunes/iTunes Media/Music/The Pogues/The Very Best Of The Pogues/07 The Body Of An American.mp3'

    def test_match_itunes_track(self):
        """Exercise itunes.match_itunes_track"""

        D = rubepl.itunes.build_track_map(self._ml1)

        ei00 = rubepl.itunes.ExtInf(211, 'Van Morrison & The Chieftains - Ta '
                                    + 'Mo Chleamhnas Deanta (My Match It Is Made)')
        m3u00 = rubepl.itunes.M3UTrack('/pub/mp3/U-Z/Van Morrison & The '
                                       + 'Chieftains - Ta Mo Chleamhnas Deanta '
                                       + '(My Match It Is Made).mp3', ei00)
        m = rubepl.itunes.match_itunes_track(m3u00, D, 12)
        assert m is None

    def test_m3u_to_itunes(self):
        """Exercise the m3u_to_itunes method."""

        outfile = os.path.join(self._tmp, 'summer-2007-itunified.m3u')
        rubepl.itunes.m3u_to_itunes(self._pl3, outfile, self._ML1)

        with open(os.path.join(self._tmp, 'summer-2007-itunified.m3u')) as fh:
            text = fh.read()
            if text != self._JIN3:
                self._find_difference(text, self._JIN3)
                with open('/tmp/not-jin3.m3u', 'w') as fh:
                    fh.write(text)

            assert text == self._JIN3

    def test_itunify_cmd(self):
        """Exercise the 'itunify-m3u' sub-command"""

        args = ['itunify-m3u', '-o', os.path.join(self._tmp, 'output1.m3u'),
                '-i', self._ml1, self._pl1]
        with captured_output() as (out, err):
            status = rubepl.main(args)
        assert "" == out.getvalue().strip()
        assert "" == err.getvalue().strip()
        with open(os.path.join(self._tmp, 'output1.m3u'), 'r') as fh:
            text = fh.read()
            if text != self._JIN1:
                self._find_difference(text, self._JIN1)
                with open('/tmp/not-jin1.m3u', 'w') as fh:
                    fh.write(text)
            assert text == self._JIN1

        args = ['itunify-m3u', '-o', os.path.join(self._tmp, 'output2.m3u'),
                '-i', self._ml1, self._pl2, '-m', '12']
        with captured_output() as (out, err):
            status = rubepl.main(args)
        assert "" == out.getvalue().strip()
        assert "" == err.getvalue().strip()
        with open(os.path.join(self._tmp, 'output2.m3u'), 'r') as fh:
            text = fh.read()
            if text != self._JIN2:
                self._find_difference(text, self._JIN2)
                with open('/tmp/not-jin2.m3u', 'w') as fh:
                    fh.write(text)

            assert text == self._JIN2
