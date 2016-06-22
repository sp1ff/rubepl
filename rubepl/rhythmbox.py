"""Utilities for working with playlists in the Rhythmbox player.

E.g. the following command will grab 'Fall 2013' out of Rhythmbox & export it to M3U:

rubepl --debug get-playlists-xml --only 'Fall 2013' -ub ~/.local/share/rhythmbox/rhythmdb.xml ~/.local/share/rhythmbox/playlists.xml

"""

__author__     = "Michael Herstine <sp1ff@pobox.com>"
__copyright__  = "Copyright (C) 2015, 2016 Michael Herstine"
__credits__    = ["Michael Herstine"]
__license__    = "GPL"
__version__    = "$Revision: $"
__maintainer__ = "Michael Herstine <sp1ff@pobox.com>"
__email__      = "sp1ff@pobox.com"
__status__     = "Prototype"

import logging
import os
import xml.etree.ElementTree as ET

import rubepl

from rubepl.decode import decode_track_location
from rubepl.m3u import convert_tracks_to_m3u, Replacements

DEFAULT_DB = os.path.expanduser('~/.local/share/rhythmbox/rhythmdb.xml')
DEFAULT_PL = os.path.expanduser('~/.local/share/rhythmbox/playlists.xml')

log = logging.getLogger(__name__)

def build_db(dbpath=DEFAULT_DB):
    """Walk the Rhythmbox database, building a mapping from file location to track
    information.

    :param str dbpath: path to the XML file containing the Rhythmbox database;
    defaults to ~/.local/share/rhythmbox/rhythmdb.xml)
    :return: a dictionary mapping track location to a (duration, artist, title) triplet
    """

    log.debug("parsing '{0}'...".format(dbpath))
    root = ET.parse(dbpath).getroot()
    log.debug("parsing '{0}'...done.".format(dbpath))

    # 'child' should be a node of type 'entry'
    db = { }
    for child in root:
        if 'song' != child.attrib['type']: continue
        title = None
        artist = None
        duration = None
        location = None
        for attr in child.getchildren():
            if 'title' == attr.tag:
                title = attr.text
            elif 'artist' == attr.tag:
                artist = attr.text
            elif 'duration' == attr.tag:
                duration = int(attr.text)
            elif 'location' == attr.tag:
                location = decode_track_location(attr.text)
        if not location: continue
        db[location] = (duration, artist, title)

    return db

def get_playlists(playlists=DEFAULT_PL, only=None, exclude=None):
    """Extract a set of playlists from playlists.xml

    :param str playlists: Location of the 'playlists.xml' file to be parsed
    (defaults to ~/.local/share/rhythmbox/playlists.xml')
    :param sequence only: An optional sequence of titles; if non-None, only the
    playlists contained herein will be exported
    :param sequence exclude: An optional sequence of titles; if non-None, the
    playlists contained herein will not be exported
    :return: A list of two tuples [(playlist title, [track,...]),...]
    """

    root = ET.parse(playlists).getroot()

    out = [ ]
    for child in root:
        name = child.attrib['name']
        kind = child.attrib['type']
        if 'static' != kind:
            continue
        if only and not name in only:
            continue
        if exclude and name in exclude:
            continue

        tracks = [ ]
        for location in child:
            tracks.append(decode_track_location(location.text))

        out.append((name, tracks))

    return out

def playlists_xml_to_m3u(playlists=DEFAULT_PL, dbpath=DEFAULT_DB,
                         rename=None, replacements=None, utf8=None, only=None,
                         exclude=None, output=None, use_bom=None):
    """Extract playlists from a Rhythmbox-style 'playlists.xml' & convert them to
    M3U format.

    :param string playlists: Location of the 'playlists.xml' file to be parsed
    (defaults to ~/.local/share/rhythmbox/playlists.xml')
    :param string dbpath: path to the XML file containing the Rhythmbox
    database; defaults to ~/.local/share/rhythmbox/rhythmdb.xml)
    :param string rename: Encoding of how the title shall be processed to
    produce a playlist filename (on which more below)
    :param Replacements replacements: A Replacements instance representing a
    list of replacements to be made on the contents of the input playlist
    :param bool utf8: If the caller sets this to true, the output file shall be
    encoded in UTF-8 & have an '.m3u8' extension; else it shall be encoded as
    CP1252 and have an '.m3u' extension
    :param bool use_bom: If the caller sets this to true, and if the caller set
    utf8 to true, the UTF-8 BOM shall be added to the first line of the output
    file
    :param sequence only: An optional sequence of titles; if non-None, only the
    playlists contained herein will be exported
    :param sequence exclude: An optional sequence of titles; if non-None, the
    playlists contained herein will not be exported

    'rename' is a textual string where each character represents a
    given transformation to be performed on the title. The following
    characters are supported:

        - 'l': Convert the title to lower case
        - '-': Replace whitespace with '-'s

    """

    # [(playlist,[location...]),...]
    out = get_playlists(playlists, only, exclude)
    if 0 == len(out):
        log.warn("No playlists selected for output.")
        return

    # {location=>(duration,artist,title)...}
    db = build_db(dbpath)

    # For each playlist...
    for pl in out:

        new_name = rubepl.process_playlist_name(pl[0], rename)
        log.info(pl[0] + ' => ' + new_name)

        if utf8:
            outf = new_name + ".m3u8"
            outcp = 'utf_8'
        else:
            outf = new_name + ".m3u"
            outcp = 'cp1252'

        tracks = [ ]
        locations = pl[1] # [location,...]
        for location in locations:
            if location in db:
                duration, artist, title = db[location]
                # log.debug('{0} => ({1}, {2}, {3})'.format(location, duration, artist, title))
                if not duration: duration = -1
                if artist:
                    display = '{0} - {1}'.format(artist, title)
                else:
                    display = title
                tracks.append((location, (duration,display)))
            else:
                tracks.append((location, None))

        lines = convert_tracks_to_m3u(tracks, use_bom)
        if replacements:
            lines = replacements.process(lines)
        log.debug(lines)

        if output: outf = os.path.join(output, outf)

        with open(outf, 'w', -1, outcp) as fd:
            for x in map(lambda line: line + os.linesep, lines):
                fd.write(x)

def _entry(args):
    """Handler for the 'get-playlists-xml' command.

    Extract one or more playlists from a 'playlists.xml' file & convert them to
    another format.

    This function will extract parsed arguments from the caller-provided
    Namespace & pass them on to the implementation.

    """

    playlists_xml_to_m3u(args.playlists, args.dbpath, args.rename,
                         Replacements(args.replace), args.utf8, args.only,
                         args.exclude, args.output, args.use_bom)

def build_subparser(subparsers, name='get-playlists-xml'):
    """Build a parser for a sub-command that will retrieve playlists from a
    Rhythmbox-style 'playlists.xml' file.

    :param subparsers: "special action object" returned from argparse.ArgumentParser.add_subparsers
    """

    gp = subparsers.add_parser(name=name, help='Retrieve playlists from a'
                               + ' Rhythmbox-style "playlists.xml" &'
                               + ' associated DB and  convert them to another'
                               + ' format.')
    gp.add_argument('-x', '--exclude', help='exclude a particular playlist '
                    + 'by title', action='append')
    gp.add_argument('-o', '--output', help='output directory')
    gp.add_argument('-y', '--only', help='Only this playlist', action='append')
    gp.add_argument('-p', '--replace', help='Specify a replacement'
                    + ' string to be applied to all text within the file; use'
                    + ' REGEX=>REPLACEMENT where REGEX is a Python regular'
                    + ' expression and REPLACEMENT is the text with which to'
                    + ' replace any matches (REPLACEMENT may include'
                    + ' sub-expressions)', action='append')
    gp.add_argument('-r', '--rename', help='Rename code: a sequence of'
                    + ' characters indicating transformations to be applied'
                    + ' to the playlist title: "l" will convert all characters'
                    + ' to lowercase, "-" will replace whitespace with a dash')
    gp.add_argument('-u', '--utf8', help='Use UTF-8 encoding '
                    + 'on output', action='store_true')
    gp.add_argument('-b', '--use-bom', help='Use the UTF-8 '
                    + 'byte order mark on output (in UTF8)',
                    action='store_true')
    gp.add_argument('dbpath', help='location of the Rhythmbox DB file (typically '
                    + DEFAULT_DB + ')')
    gp.add_argument('playlists', help='location of the playlists XML file '
                    + 'to be processed (typically ' + DEFAULT_PL + ')')
    gp.set_defaults(func=_entry)
