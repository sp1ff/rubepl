"""Unit tests for the rubepl.m3u module"""

import os
import shutil
import sys
import tempfile
import unittest

import rubepl.m3u

from test.utils import captured_output

class NormalizationFixture(unittest.TestCase):
    """Fixture for exercising rubepl.m3u.normalize_m3u_playlist."""

    _SRC_1B2B = """#EXTM3U
#EXTINF:186,Gin Blossoms - Not Only Numb
M:\\G\\Gin Blossoms - Not Only Numb.mp3
#EXTINF:271,Counting Crows - Anna Begins
M:\\C\\Counting Crows - Anna Begins.mp3
#EXTINF:318,Counting Crows - Goodnight Elizabeth
M:\\C\\Counting Crows - Goodnight Elizabeth.mp3
#EXTINF:224,Iguanas - 9 Volt Heart
M:\\H-I\\Iguanas, The - 9 Volt Heart.mp3
#EXTINF:341,Bruce Springsteen - Thunder Road
M:\\B\\Bruce Springsteen & The E Street Band - Thunder Road.mp3
#EXTINF:463,Bob Dylan - Standing In The Doorway (Album Version)
M:\\B\\Bob Dylan - Standing In The Doorway (Album Version).mp3
#EXTINF:145,Mary Lou Lord - Cold Kilburn Rain
M:\\M\\Mary Lou Lord - Cold Kilburn Rain.mp3
#EXTINF:264,Groove Armada - Hands Of Time
M:\\G\\Groove Armada - Hands Of Time.mp3
#EXTINF:303,James Dunn - Sunday Morning (Eyes of Blue)
M:\\J-K\\James Dunn - Sunday Morning (Eyes of Blue).mp3
#EXTINF:290,Robert Plant - 29 Palms (2006 Remastered LP Version)
M:\\Q-R\\Robert Plant - 29 Palms (2006 Remastered LP Version).mp3
#EXTINF:269,Fleetwood Mac - Silver Springs
M:\\F\\Fleetwood Mac - Silver Springs.mp3
#EXTINF:214,Van Morrison - Everyone (Album Version)
M:\\U-Z\\Van Morrison - Everyone (Album Version).mp3
#EXTINF:246,Paul Westerberg - These Days
M:\\P\\Paul Westerberg - These Days.mp3
#EXTINF:295,Counting Crows - A Long December
M:\\C\\Counting Crows - A Long December.mp3
#EXTINF:197,Liz Phair - Go West [Explicit]
M:\\L\\Liz Phair - Go West.mp3
#EXTINF:136,Sundays - I Kicked A Boy
M:\\Sm-Sz\\Sundays - I Kicked A Boy.mp3
#EXTINF:384,U2 - Elvis Presley and America
M:\\U-Z\\U2 - Elvis Presley And America.mp3
#EXTINF:300,Mary Lou Lord - Thunder Road
M:\\M\\Mary Lou Lord - Thunder Road.mp3
#EXTINF:75,Mark Mothersbaugh - 2000)
M:\\M\\Mark Mothersbaugh - Rachel Evans Tenenbaum (1965-2000).mp3
#EXTINF:260,Peter Gabriel - Solsbury Hill
M:\\P\\Peter Gabriel - Solsbury Hill.mp3
#EXTINF:279,Kate Bush - Love And Anger (Album Version)
M:\\J-K\\Kate Bush - Love And Anger (Album Version).mp3
#EXTINF:372,Bryan Ferry - Dance With Life (The Brilliant Light)
M:\\B\\Bryan Ferry - Dance With Life (The Brilliant Light).mp3
#EXTINF:233,Eric Clapton - Change The World
M:\\E\\Eric Clapton - Change The World.mp3
#EXTINF:216,R.E.M. - Texarkana
M:\\Q-R\\R.E.M. - Texarkana.mp3
#EXTINF:222,I Nine - Same In Any Language
M:\\H-I\\I Nine - Same In Any Language.mp3
#EXTINF:246,Nico - The Fairest Of The Seasons
M:\\N-O\\Nico - The Fairest Of The Seasons.mp3
#EXTINF:309,Tori Amos - Cooling
M:\\T\\Tori Amos - Cooling.mp3
#EXTINF:216,Smiths, The - Half A Person
M:\\Sm-Sz\\Smiths, The - Half A Person.mp3
#EXTINF:282,Peter Gabriel - Mercy Street
M:\\P\\Peter Gabriel - Mercy Street.mp3
#EXTINF:370,Bliss - Song For Alabi
M:\\B\\Bliss - Song For Alabi.mp3
#EXTINF:427,Peter Gabriel - Come Talk To Me
M:\\P\\Peter Gabriel - Come Talk To Me.mp3
#EXTINF:208,Rolling Stones, The - Angie
M:\\Q-R\\Rolling Stones, The - Angie.mp3
#EXTINF:201,Blake Hazard - Come Undone
M:\\B\\Blake Hazard - Come Undone.mp3
#EXTINF:210,Nico - These Days
M:\\N-O\\Nico - These Days.mp3
#EXTINF:259,U2 - Running To Stand Still
M:\\U-Z\\U2 - Running To Stand Still.mp3
#EXTINF:197,Nico - I'll Keep It With Mine
M:\\N-O\\Nico - I'll Keep It With Mine.mp3
#EXTINF:243,Tori Amos - Glory Of The 80's
M:\\T\\Tori Amos - Glory Of The 80's.mp3
#EXTINF:283,Ruckus - Same In Any Language
M:\\Q-R\\Ruckus - Same In Any Language.mp3
"""

    _JIN_1B2B = b"""\xef\xbb\xbf#EXTM3U
#EXTINF:186,Gin Blossoms - Not Only Numb
/pub/mp3/G/Gin Blossoms - Not Only Numb.mp3
#EXTINF:271,Counting Crows - Anna Begins
/pub/mp3/C/Counting Crows - Anna Begins.mp3
#EXTINF:318,Counting Crows - Goodnight Elizabeth
/pub/mp3/C/Counting Crows - Goodnight Elizabeth.mp3
#EXTINF:224,Iguanas - 9 Volt Heart
/pub/mp3/H-I/Iguanas, The - 9 Volt Heart.mp3
#EXTINF:341,Bruce Springsteen - Thunder Road
/pub/mp3/B/Bruce Springsteen & The E Street Band - Thunder Road.mp3
#EXTINF:463,Bob Dylan - Standing In The Doorway (Album Version)
/pub/mp3/B/Bob Dylan - Standing In The Doorway (Album Version).mp3
#EXTINF:145,Mary Lou Lord - Cold Kilburn Rain
/pub/mp3/M/Mary Lou Lord - Cold Kilburn Rain.mp3
#EXTINF:264,Groove Armada - Hands Of Time
/pub/mp3/G/Groove Armada - Hands Of Time.mp3
#EXTINF:303,James Dunn - Sunday Morning (Eyes of Blue)
/pub/mp3/J-K/James Dunn - Sunday Morning (Eyes of Blue).mp3
#EXTINF:290,Robert Plant - 29 Palms (2006 Remastered LP Version)
/pub/mp3/Q-R/Robert Plant - 29 Palms (2006 Remastered LP Version).mp3
#EXTINF:269,Fleetwood Mac - Silver Springs
/pub/mp3/F/Fleetwood Mac - Silver Springs.mp3
#EXTINF:214,Van Morrison - Everyone (Album Version)
/pub/mp3/U-Z/Van Morrison - Everyone (Album Version).mp3
#EXTINF:246,Paul Westerberg - These Days
/pub/mp3/P/Paul Westerberg - These Days.mp3
#EXTINF:295,Counting Crows - A Long December
/pub/mp3/C/Counting Crows - A Long December.mp3
#EXTINF:197,Liz Phair - Go West [Explicit]
/pub/mp3/L/Liz Phair - Go West.mp3
#EXTINF:136,Sundays - I Kicked A Boy
/pub/mp3/Sm-Sz/Sundays - I Kicked A Boy.mp3
#EXTINF:384,U2 - Elvis Presley and America
/pub/mp3/U-Z/U2 - Elvis Presley And America.mp3
#EXTINF:300,Mary Lou Lord - Thunder Road
/pub/mp3/M/Mary Lou Lord - Thunder Road.mp3
#EXTINF:75,Mark Mothersbaugh - 2000)
/pub/mp3/M/Mark Mothersbaugh - Rachel Evans Tenenbaum (1965-2000).mp3
#EXTINF:260,Peter Gabriel - Solsbury Hill
/pub/mp3/P/Peter Gabriel - Solsbury Hill.mp3
#EXTINF:279,Kate Bush - Love And Anger (Album Version)
/pub/mp3/J-K/Kate Bush - Love And Anger (Album Version).mp3
#EXTINF:372,Bryan Ferry - Dance With Life (The Brilliant Light)
/pub/mp3/B/Bryan Ferry - Dance With Life (The Brilliant Light).mp3
#EXTINF:233,Eric Clapton - Change The World
/pub/mp3/E/Eric Clapton - Change The World.mp3
#EXTINF:216,R.E.M. - Texarkana
/pub/mp3/Q-R/R.E.M. - Texarkana.mp3
#EXTINF:222,I Nine - Same In Any Language
/pub/mp3/H-I/I Nine - Same In Any Language.mp3
#EXTINF:246,Nico - The Fairest Of The Seasons
/pub/mp3/N-O/Nico - The Fairest Of The Seasons.mp3
#EXTINF:309,Tori Amos - Cooling
/pub/mp3/T/Tori Amos - Cooling.mp3
#EXTINF:216,Smiths, The - Half A Person
/pub/mp3/Sm-Sz/Smiths, The - Half A Person.mp3
#EXTINF:282,Peter Gabriel - Mercy Street
/pub/mp3/P/Peter Gabriel - Mercy Street.mp3
#EXTINF:370,Bliss - Song For Alabi
/pub/mp3/B/Bliss - Song For Alabi.mp3
#EXTINF:427,Peter Gabriel - Come Talk To Me
/pub/mp3/P/Peter Gabriel - Come Talk To Me.mp3
#EXTINF:208,Rolling Stones, The - Angie
/pub/mp3/Q-R/Rolling Stones, The - Angie.mp3
#EXTINF:201,Blake Hazard - Come Undone
/pub/mp3/B/Blake Hazard - Come Undone.mp3
#EXTINF:210,Nico - These Days
/pub/mp3/N-O/Nico - These Days.mp3
#EXTINF:259,U2 - Running To Stand Still
/pub/mp3/U-Z/U2 - Running To Stand Still.mp3
#EXTINF:197,Nico - I'll Keep It With Mine
/pub/mp3/N-O/Nico - I'll Keep It With Mine.mp3
#EXTINF:243,Tori Amos - Glory Of The 80's
/pub/mp3/T/Tori Amos - Glory Of The 80's.mp3
#EXTINF:283,Ruckus - Same In Any Language
/pub/mp3/Q-R/Ruckus - Same In Any Language.mp3
"""

    _TRACKS = [
        ('M:\\G\\Gin Blossoms - Not Only Numb.mp3', (186,'Gin Blossoms - Not Only Numb')),
        ('M:\\C\\Counting Crows - Anna Begins.mp3', (271,'Counting Crows - Anna Begins')),
        ('M:\\C\\Counting Crows - Goodnight Elizabeth.mp3', (318,'Counting Crows - Goodnight Elizabeth')),
        ('M:\\H-I\\Iguanas, The - 9 Volt Heart.mp3', (224,'Iguanas - 9 Volt Heart')),
        ('M:\\B\\Bruce Springsteen & The E Street Band - Thunder Road.mp3', (341,'Bruce Springsteen - Thunder Road')),
        ('M:\\B\\Bob Dylan - Standing In The Doorway (Album Version).mp3', (463,'Bob Dylan - Standing In The Doorway (Album Version)')),
        ('M:\\M\\Mary Lou Lord - Cold Kilburn Rain.mp3', (145,'Mary Lou Lord - Cold Kilburn Rain')),
        ('M:\\G\\Groove Armada - Hands Of Time.mp3', (264,'Groove Armada - Hands Of Time')),
        ('M:\\J-K\\James Dunn - Sunday Morning (Eyes of Blue).mp3', (303,'James Dunn - Sunday Morning (Eyes of Blue)')),
        ('M:\\Q-R\\Robert Plant - 29 Palms (2006 Remastered LP Version).mp3', (290,'Robert Plant - 29 Palms (2006 Remastered LP Version)')),
        ('M:\\F\\Fleetwood Mac - Silver Springs.mp3', (269,'Fleetwood Mac - Silver Springs')),
        ('M:\\U-Z\\Van Morrison - Everyone (Album Version).mp3', (214,'Van Morrison - Everyone (Album Version)')),
        ('M:\\P\\Paul Westerberg - These Days.mp3', (246,'Paul Westerberg - These Days')),
        ('M:\\C\\Counting Crows - A Long December.mp3', (295,'Counting Crows - A Long December')),
        ('M:\\L\\Liz Phair - Go West.mp3', (197,'Liz Phair - Go West [Explicit]')),
        ('M:\\Sm-Sz\\Sundays - I Kicked A Boy.mp3', (136,'Sundays - I Kicked A Boy')),
        ('M:\\U-Z\\U2 - Elvis Presley And America.mp3', (384,'U2 - Elvis Presley and America')),
        ('M:\\M\\Mary Lou Lord - Thunder Road.mp3', (300,'Mary Lou Lord - Thunder Road')),
        ('M:\\M\\Mark Mothersbaugh - Rachel Evans Tenenbaum (1965-2000).mp3', (75,'Mark Mothersbaugh - 2000)')),
        ('M:\\P\\Peter Gabriel - Solsbury Hill.mp3', (260,'Peter Gabriel - Solsbury Hill')),
        ('M:\\J-K\\Kate Bush - Love And Anger (Album Version).mp3', (279,'Kate Bush - Love And Anger (Album Version)')),
        ('M:\\B\\Bryan Ferry - Dance With Life (The Brilliant Light).mp3', (372,'Bryan Ferry - Dance With Life (The Brilliant Light)')),
        ('M:\\E\\Eric Clapton - Change The World.mp3', (233,'Eric Clapton - Change The World')),
        ('M:\\Q-R\\R.E.M. - Texarkana.mp3', (216,'R.E.M. - Texarkana')),
        ('M:\\H-I\\I Nine - Same In Any Language.mp3', (222,'I Nine - Same In Any Language')),
        ('M:\\N-O\\Nico - The Fairest Of The Seasons.mp3', (246,'Nico - The Fairest Of The Seasons')),
        ('M:\\T\\Tori Amos - Cooling.mp3', (309,'Tori Amos - Cooling')),
        ('M:\\Sm-Sz\\Smiths, The - Half A Person.mp3', (216,'Smiths, The - Half A Person')),
        ('M:\\P\\Peter Gabriel - Mercy Street.mp3', (282,'Peter Gabriel - Mercy Street')),
        ('M:\\B\\Bliss - Song For Alabi.mp3', (370,'Bliss - Song For Alabi')),
        ('M:\\P\\Peter Gabriel - Come Talk To Me.mp3', (427,'Peter Gabriel - Come Talk To Me')),
        ('M:\\Q-R\\Rolling Stones, The - Angie.mp3', (208,'Rolling Stones, The - Angie')),
        ('M:\\B\\Blake Hazard - Come Undone.mp3', (201,'Blake Hazard - Come Undone')),
        ('M:\\N-O\\Nico - These Days.mp3', (210,'Nico - These Days')),
        ('M:\\U-Z\\U2 - Running To Stand Still.mp3', (259,'U2 - Running To Stand Still')),
        ('M:\\N-O\\Nico - I\'ll Keep It With Mine.mp3', (197,'Nico - I\'ll Keep It With Mine')),
        ('M:\\T\\Tori Amos - Glory Of The 80\'s.mp3', (243,'Tori Amos - Glory Of The 80\'s')),
        ('M:\\Q-R\\Ruckus - Same In Any Language.mp3', (283,'Ruckus - Same In Any Language')),
    ]

    def setUp(self):
        self._tmp = tempfile.mkdtemp()
        self._pls1B2B = os.path.join(self._tmp, 'plf1B2B.m3u8')
        with open(self._pls1B2B, 'wb') as fh:
            fh.write(bytes(self._SRC_1B2B, 'UTF-8'))

    def tearDown(self):
        shutil.rmtree(self._tmp)

    def test_normalize(self):
        """Exercise rubepl.m3u.normalize_m3u_playlist"""

        replacements = rubepl.m3u.Replacements(['\\\\\\\\=>/', 'M:/=>/pub/mp3/'])

        self.assertRaises(Exception, rubepl.m3u.normalize_m3u_playlist,
                          ('Summer 2008', self._pls1B2B, 'lk', replacements,
                           True, True, 'cp1252', self._tmp))

        rubepl.m3u.normalize_m3u_playlist('Summer 2008', self._pls1B2B, 'l-', replacements,
                                          utf8=True, use_bom=True, output=self._tmp)

        with open(os.path.join(self._tmp, 'summer-2008.m3u8'), 'rb') as fh:
            text = fh.read()
            assert text == self._JIN_1B2B

    def test_normalize_cmd(self):
        """Exercise the normalize-m3u sub-command"""

        args = ['normalize-m3u', '-c', 'cp1252',
                '-o', self._tmp,
                '-r', 'l-',
                '-p' '\\\\\\\\=>/', '-p', 'M:/=>/pub/mp3/',
                '-u', '-b']
        with captured_output() as (out, err):
            status = rubepl.main(args)
        output = out.getvalue().strip()
        assert '' == output
        errors = err.getvalue().strip()
        assert 'usage:' == errors[0:6]

        args.append(self._pls1B2B)
        with captured_output() as (out, err):
            status = rubepl.main(args)
        output = out.getvalue().strip()
        assert '"plf1B2B"=>"plf1b2b"' == output
        errors = err.getvalue().strip()
        assert '' == errors

        with open(os.path.join(self._tmp, 'plf1b2b.m3u8'), 'rb') as fh:
            text = fh.read()
            assert text == self._JIN_1B2B

    def test_get_tracks(self):
        """Test rubepl.m3u.get_tracks_from_m3u"""

        tracks = [x for x in rubepl.m3u.get_tracks_from_m3u(self._pls1B2B)]
        assert tracks == self._TRACKS

    def test_get_tracks_cmd(self):
        """Exercise the get-tracks sub-command"""

        args = ['get-tracks', '-c', 'cp1252', self._pls1B2B]
        with captured_output() as (out, err):
            status = rubepl.main(args)
        output = set(filter(lambda x: 0 != len(x), out.getvalue().split('\n')))
        assert output == set(map(lambda x: x[0], self._TRACKS))
        errors = err.getvalue().strip()
        assert '' == errors

if '__main__' == __name__:
    unittest.main()
