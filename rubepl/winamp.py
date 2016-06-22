"""winamp.py -- Assorted utilities for working with Winamp playlists

Cf. the `Unofficial M3U & PLS Specification <http://forums.winamp.com/showthread.php?threadid=65772>`_.
"""


__author__     = "Michael Herstine <sp1ff@pobox.com>"
__copyright__  = "Copyright (C) 2015, 2016 Michael Herstine"
__credits__    = ["Michael Herstine"]
__license__    = "GPL"
__version__    = "$Revision: $"
__maintainer__ = "Michael Herstine <sp1ff@pobox.com>"
__email__      = "sp1ff@pobox.com"
__status__     = "Prototype"

import os

import rubepl.decode
import rubepl.encode

import xml.etree.ElementTree as ET

from rubepl.m3u import normalize_m3u_playlist


def extract_playlists(playlists, rename, replacements,
                      utf8=False, only=None, exclude=None,
                      output=None, use_bom=None,
                      codepage=None):
    """Extract some or all playlists from a Winamp Music Library & export them to
    M3U format.

    :param string playlists: Location of the 'playlists.xml' file Winamp uses
    to record all ML playlists
    :param string rename: An encoding of how the title shall be processed to
    produce a playlist filename (on which more below)
    :param list m3u.Replacemens replacements: A (possibly empty) collection of
    transformations to be performed on the tracks in every extracted playlist
    :param bool utf8: If true, use UTF-8 format for output: the exported M3U
    files shall have an 'm3u8' extension and their contents shall be encoded in
    UTF-8
    :param list only: If non-None, this is assumed to be a list of playlist
    titles; only playlists in this list shall be processed
    :param list exclude: If non-None, this is assumed to be a list of playlist
    titles; playlists in this list shall not be processed
    :param string output: Output directory for generated files; if None, the
    present working directory will be used
    :param bool use_bom: If True, add a UTF-8 byte order marker to the output
    playlists files, regardless of their encoding or suffix
    :param str codepage: If non-None, this shall be the name of the code page
    in which the input files are encoded; if None, the input codepage shall be
    deduced ('utf_8' if the file extension is '.m3u8', 'cp1252' otherwise)

    'rename' is a textual string where each character represents a given
    transformation to be performed on the title. The following characters are
    supported:

        'l': Convert the title to lower case
        '-': Replace whitespace with '-'s

    """

    dirname = os.path.dirname(playlists)
    root = ET.parse(playlists).getroot()

    for child in root:
        title = child.attrib['title']
        if only and not title in only:
            continue
        if exclude and title in exclude:
            continue

        normalize_m3u_playlist(title, os.path.join(dirname, child.attrib['filename']),
                               rename, replacements, utf8, use_bom,
                               codepage, output)

def _get_playlists(args):
    """Handler for the'get-winamp-ml' command.

    :param Namespace args: Presumably the result of calling parse_args on the
    rubepl ArgumentParser.

    This function will extract parsed arguments from the caller-provided
    Namespace & pass them on to the implementation.
    """

    extract_playlists(args.playlists, args.rename,
                      rubepl.m3u.Replacements(args.replace),
                      args.utf8, args.only, args.exclude, args.output,
                      args.use_bom, args.codepage)

def build_subparser(subparsers, name='get-winamp-ml'):
    """Build a sub-parser for a command that will extract all playlists from a
    Winamp Music Library.

    :param subparsers: "special action object" returned from argparse.ArgumentParser.add_subparsers
    """

    get = subparsers.add_parser(name=name, help='Retrieve playlists from a'
                                + ' Winamp Music Library & convert them to'
                                + ' M3U format (the specifics of the output'
                                + ' format are configurable).')
    get.add_argument('-c', '--codepage', help='specify the input codepage (e.g.'
                     + ' "cp1252", or "utf_8", cf. https://docs.python.org/3/library/codecs.html#standard-encodings'
                     + ' for a complete list); if not specified, the'
                     + ' implementation will attempt to deduce the input'
                     + ' encoding automatically')
    get.add_argument('-x', '--exclude', help='exclude a particular'
                    + ' playlist by title', action='append')
    get.add_argument('-o', '--output', help='output directory')
    get.add_argument('-y', '--only', help='Only this playlist',
                     action='append')
    get.add_argument('-p', '--replace', help='Specify a replacement '
                     + 'string to be applied to all text within the file; use'
                     + ' REGEX=>REPLACEMENT where REGEX is a Python regular'
                     + ' expression and REPLACEMENT is the text with which to'
                     + ' replace any matches (REPLACEMENT may include'
                     + ' sub-expressions)', action='append')
    get.add_argument('-r', '--rename', help='Rename code: a sequence of'
                     + ' characters indicating transformations to be applied'
                     + ' to the playlist title: "l" will convert all characters'
                     + ' to lowercase, "-" will replace whitespace with a dash')
    get.add_argument('-u', '--utf8', help='Use UTF-8 encoding '
                    + 'on output', action='store_true')
    get.add_argument('-b', '--use-bom', help='Use the UTF-8 '
                    + 'byte order mark on output (in UTF8)',
                    action='store_true')
    get.add_argument('playlists', help='location of the '
                    + 'playlists.xml file to be processed')
    get.set_defaults(func=_get_playlists)
