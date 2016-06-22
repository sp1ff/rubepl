import os
import shutil
import tempfile
import unittest

import rubepl.m3u
import rubepl.winamp

class ExtractPlaylists(unittest.TestCase):

    _PLAYLISTS = os.path.join(os.getcwd(), 'test/resources/Winamp/Plugins/ml/playlists/playlists.xml')

    def setUp(self):
        self._tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self._tmp)

    def test_extract_playlists(self):

        replacements = rubepl.m3u.Replacements(['\\\\\\\\=>/', 'M:/=>/pub/mp3/'])

        rubepl.winamp.extract_playlists(self._PLAYLISTS, 'l-', replacements,
                                        utf8=True, output=self._tmp, use_bom=True,
                                        exclude=['Lifting Mix #1', 'Lifting Mix #2'])

        replacements.add(['H(\\xfc)E=>H\\1s', 'D(\\xfc)E=>D\\1'])
        rubepl.winamp.extract_playlists(self._PLAYLISTS, 'l-', replacements,
                                        utf8=True, output=self._tmp, use_bom=True,
                                        codepage='cp437',
                                        only=['Lifting Mix #1', 'Lifting Mix #2'])

        # TODO: This really lame, but I don't want to write more tests until I
        # get better data...
        assert 81 == len(os.listdir(self._tmp))
