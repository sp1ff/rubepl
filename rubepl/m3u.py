"""m3u.py -- Assorted utilities for working with playlists in M3U format.

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


import codecs
import logging
import os
import re

import rubepl

from rubepl.decode import decode_file, maybe_remove_bom
from rubepl.encode import encode_line, maybe_add_utf8_bom


COMMENT_REGEX = re.compile('^\s*#')
EXTINFO_REGEX = re.compile('^\s*#\s*EXTINF\s*:\s*([-0-9]+)?\s*,\s*(.*)?')

log = logging.getLogger(__name__)


class Replacements(object):

    def __init__(self, args):

        self._regexes = []
        self.add(args)

    def add(self, args):
        if args is None:
            return
        for arg in args:
            self._regexes.append(self.process_replacement_string(arg))

    def process_replacement_string(self, text):
        """Process a configuration-specified replacement string into a
        (regex,replacement string) tuple.

        This function will take strings in the form "A=>B" and return a regular
        expression built on 'A' together with a string formed from 'B'. In the
        unlikely event that the caller wants to include the text '=>' in either
        the regex or the replacement string, he can escape either character;
        e.g. '\=>=>X' will replace the text '=>' with 'X'. To replace all
        backslashes, use the unfortunate '\\\\=>/'.
        """

        INIT = 0
        SAW_BACKSLASH = 1
        SAW_EQUALS = 2

        state = INIT
        regex = ""

        idx = 0
        while idx < len(text):

            c = text[idx]
            idx = idx + 1
            if state == INIT:
                if '\\' == c:
                    state = SAW_BACKSLASH
                elif '=' == c:
                    state = SAW_EQUALS
                else:
                    regex += c
            elif state == SAW_BACKSLASH:
                if '=' == c:
                    regex += c
                    state = INIT
                elif '\\' == c:
                    regex += '\\'
                    state = INIT
                else:
                    regex += '\\'
                    regex += c
                    state = INIT
            else:
                if '>' == c:
                    break
                else:
                    regex += '='
                    regex += c
                    state = INIT

        regex = re.compile(regex)
        repl  = text[idx:]

        return (regex,repl)

    def process(self, lines):
        """Apply our regexes to every line in 'lines', return the result."""

        outlines = []
        for line in lines:
            out = line
            for regex in self._regexes:
                out = re.sub(regex[0], regex[1], out)
            outlines.append(out)
        return outlines


def normalize_m3u_playlist(title, filename, rename, replacements,
                           utf8=None, use_bom=None, codepage=None,
                           output=None):
    """Transform an M3U playlist in various ways.

    :param str title: The playlist title
    :param str filename: The file containing the input playlist
    :param str rename: Encoding of how the title shall be processed to produce
    a playlist filename (on which more below)
    :param Replacements replacements: A Replacements instance representing a
    list of replacements to be made on the contents of the input playlist
    :param bool utf8: If the caller sets this to true, the output file shall be
    encoded in UTF-8 & have an '.m3u8' extension; else it shall be encoded as
    CP1252 and have an '.m3u' extension
    :param bool use_bom: If the caller sets this to true, and if the caller set
    utf8 to true, the UTF-8 BOM shall be added to the first line of the output
    file
    :param str codepage: The encoding of the input file; the caller can specify
    this explicitly
    (cf. `here<https://docs.python.org/3.3/library/codecs.html#standard-encodings>`_)
    or decline to provide it, in which case the implementation will try to
    deduce it.
    :param str output: If specified, the directory to which output files shall
    be written; if not specified, the present working directory shall be used.

    This method will transform an M3U playlist according to 'replacements',
    rename it according to 'rename', and write out the result according to
    'output', 'use_bom', and 'utf8'.

    'rename' is a textual string where each character represents a given
    transformation to be performed on the title. The following characters are
    supported:

        'l': Convert the title to lower case
        '-': Replace whitespace with '-'s

    """

    # Not my normal approach (try & let it fail), but this is a common enough
    # failure that I want to check explicitly.
    if not os.path.isfile(filename):
        log.error('{0} (for {1}) does not appear to exist!'.format(filename, title))
        return

    new_name = rubepl.process_playlist_name(title, rename)
    log.info('"{0}"=>"{1}"'.format(title, new_name))

    if utf8:
        outf = new_name + ".m3u8"
        outcp = 'utf_8'
    else:
        outf = new_name + ".m3u"
        outcp = 'cp1252'

    encoded = [x for x in map(lambda x: encode_line(x), decode_file(filename, codepage))]
    outlines = replacements.process(encoded)

    if output:
        outf = os.path.join(output, outf)

    if utf8 and use_bom:
        outlines[0] = maybe_add_utf8_bom(outlines[0])

    with open(outf, 'w', -1, outcp) as fd:
        for x in map(lambda line: line + os.linesep, outlines):
            fd.write(x)

def get_tracks_from_m3u(filename, codepage=None):
    """Read a playlist in M3U format & return the contents.

    :param str filename: path to the M3U playlist of interest
    :param str codepage: The encoding of the input file; the caller can specify
    this explicitly
    (cf. `here<https://docs.python.org/3.3/library/codecs.html#standard-encodings>`_)
    or decline to provide it, in which case the implementation will try to
    deduce it.

    For each track in 'filename' a two-tuple of (path, extinfo) will be
    returned, where 'path' is the path to the actual file, and 'extinfo' is the
    optional extended information (if non-None, then it shall be a two-tuple
    (duration, title), either of which may be None. If non-None, duration shall
    be an integer.

    """

    lines = decode_file(filename, codepage)
    lines[0] = maybe_remove_bom(lines[0])
    lines = map(lambda x: x.strip(), lines)

    tracks = []

    INIT = 0
    PARSING = 1
    SAW_EXTINF = 2
    state = INIT
    for line in lines:
        if INIT == state:
            if '#EXTM3U' != line:
                raise Exception('{0} is not in M3U format'.format(filename))
            state = PARSING
        elif PARSING == state:
            what = EXTINFO_REGEX.match(line)
            if what is None:
                tracks.append((line, None))
            else:
                duration = what.group(1)
                display = what.group(2)
                if duration:
                    duration = int(duration)
                state = SAW_EXTINF
                extinf = (duration, display)
        elif SAW_EXTINF == state:
            tracks.append((line, extinf))
            state = PARSING

    return tracks

def convert_tracks_to_m3u(tracks, use_bom=None):
    """Convert a collection of tracks with optional extended information to M3U
    format.

    :param sequence tracks: a sequence of tracks; each 'track' is a two-tuple
    (path, extinfo) where 'path' is the path to the actual file, and 'extinfo'
    is optional extended information (if not None, it shall be a three-tuple
    (duration, title), either of which may be null, 'duration' shall be an
    integer)

    :return: A sequence of strings containing the given tracks in M3U format

    """

    header = encode_line("#EXTM3U")
    if use_bom:
        header = maybe_add_utf8_bom(header)

    encoded = [ header ]
    for track in tracks:
        if None != track[1]:
            duration = track[1][0]
            title = track[1][1]
            if None != duration or None != title:
                if None == duration: duration = -1
                if None == title: title = ""
                text = "#EXTINF:{0},{1}".format(duration, title)
                encoded.append(encode_line(text))

        encoded.append(encode_line(track[0]))

    return encoded

def _normalize_m3u_pls(args):
    """Handler for the 'normalize-m3u' command.

    :param Namespace args: Presumably the result of calling parse_args on the
    rubepl ArgumentParser.

    This function will extract parsed arguments from the caller-provided
    Namespace & pass them on to the implementation.
    """

    replacements = Replacements(args.replace)
    for f in args.files:
        title = os.path.splitext(os.path.split(f)[-1])[0]
        normalize_m3u_playlist(title, f, args.rename, replacements,
                           args.utf8, args.use_bom, args.codepage,
                           args.output)

def _get_tracks_from_m3us(args):
    """Given a list of playlists in M3U format, print out the set of all distinct
    tracks in those playlists.

    :param argparse.Namespace args: argparse Namespace (on which more below)

    The Namespace is assumed to contain the following entries:

        - files: List of playlist to be converted
        - codepage: The input code page for all playlists
        - check-missing: If true, just print tracks that are missing on
          the source side

    This can be used to copy them to another host like so:

        rubepl get-tracks athens.m3u8 | xargs -d '\n' -I {} scp {} 192.168.0.99:doc/import

    """

    S = set()
    for f in args.files:
        tracks = map(lambda x: x[0], get_tracks_from_m3u(f, args.codepage))
        S = S.union(set(tracks))

    if args.check_missing:
        S = filter(lambda x: not os.path.exists(x), S)

    print('\n'.join(S))

def build_normalize_subparser(subparsers, name='normalize-m3u'):
    """Build a sub-parser for a command that will transform one or more M3U
playlists in various ways.

    :param subparsers: "special action object" returned from argparse.ArgumentParser.add_subparsers
    """

    m3u = subparsers.add_parser(name=name, help='Transform M3U playlists in by'
                                + ' changing the title, processing the'
                                + ' contents, or changing the encoding in'
                                + ' various ways (depending on the parameters'
                                + ' given).')

    m3u.add_argument('files', help='Playlist to be converted',
                      nargs='+')
    m3u.add_argument('-c', '--codepage', help='specify the input codepage (e.g.'
                     + ' "cp1252", or "utf_8", cf. https://docs.python.org/3/library/codecs.html#standard-encodings'
                     + ' for a complete list); if not specified, the'
                     + ' implementation will attempt to deduce the input'
                     + ' encoding automatically')
    m3u.add_argument('-o', '--output', help='output directory')
    m3u.add_argument('-p', '--replace', help='Specify a replacement'
                     + ' string to be applied to all text within the file; use'
                     + ' REGEX=>REPLACEMENT where REGEX is a Python regular'
                     + ' expression and REPLACEMENT is the text with which to'
                     + ' replace any matches (REPLACEMENT may include'
                     + ' sub-expressions)', action='append')
    m3u.add_argument('-r', '--rename', help='Rename code: a sequence of'
                     + ' characters indicating transformations to be applied'
                     + ' to the playlist title: "l" will convert all characters'
                     + ' to lowercase, "-" will replace whitespace with a dash')
    m3u.add_argument('-u', '--utf8', help='Use UTF-8 encoding '
                      + 'on output', action='store_true')
    m3u.add_argument('-b', '--use-bom', help='Use the UTF-8 '
                      + 'byte order mark on output (in UTF8)',
                      action='store_true')
    m3u.set_defaults(func=_normalize_m3u_pls)

def build_get_tracks_subparser(subparsers, name='get-tracks'):
    """Build the sub-parser for the 'get-tracks' command."""

    gt = subparsers.add_parser(name=name, help='Print the list of '
                               + 'tracks for one or more .m3u playlists.')
    gt.add_argument('files', help='Playlist to be converted',
                    nargs='+')
    gt.add_argument('-c', '--codepage', help='specify the input codepage')
    gt.add_argument('-m', '--check-missing', help='Just print tracks that are '
                    + 'missing on the source side',
                    action='store_true')
    gt.set_defaults(func=_get_tracks_from_m3us)
