=======================================================
rubepl -- assorted utilities for working with playlists
=======================================================

Introduction
============

rubepl is a collection of utilities for working with playlists. For
all the popularity of Pandora, Amazon Prime Stations, and other
"personalized radio" services, I think there's still a place for music
I actually own, organized into playlists I curate by hand. This
package grew out of some coding I did in the course of that curation.

Examples
========

**TODO**: Write some examples, for instance:

  - how to generate an scp command to copy all files in a playlist


Discussion
==========

This is very much a work in progress-- I wouldn't even call it an
alpha release at this point.

Implementation Notes
--------------------

The Name
~~~~~~~~

I had trouble picking a name (playlist-utilities was a bit too
generic), and the project name generator at
http://mrsharpoblunto.github.io/foswig.js/ came up with "rubepl". I
liked the fact that it ended in "pl", and since I'm writing it at my
cabin in the Santa Cruz Mountains, the "rube" part seemed vaugely
apropos, too.

In Progress
-----------

Removed from decode.py until I know why I need it:

def decode_file(filename, codepage=None):
    """Read 'filename', strip the BOM if present, strip any leading or trailing
    whitespace, return a list of Python strings.

    In order to read the file, we need to know the file's encoding.  The caller
    can specify the file encoding explicitly, or set 'encoding' to None to have
    this function try to deduce the file encoding.

    """

    codecs.register_error('fb_cp1252', handle_decode_err_by_fb_cp1252)

    ext = (os.path.splitext(filename))[1];
    if codepage:
        incp = codepage
        errs = 'strict'
    elif '.m3u8' == ext:
        incp = 'utf_8'
        errs = 'fb_cp1252'
    else:
        incp = 'cp1252'
        errs = 'strict'

    lines = open(filename, 'r', -1, incp, errs).readlines();
    lines[0] = maybe_remove_bom(lines[0])

    return lines


    regexes = []
    if replacements:
        for replacement in replacements:
            regexes.append(
                rubepl.process_replacement_string(replacement))

old m3u.normalize_m3u_playlist:

def normalize_m3u_playlist(title, filename, rename, regexes,
                           utf8=None, use_bom=None, codepage=None,
                           output=None):
    """Transform an M3U playlist in various ways.

    Parameters
    ----------
    title: string
        the playlist title
    filename: string
        The file containing the input playlist
    rename: string
        Encoding of how the title shall be processed to produce a playlist
        filename (on which more below)
    replacements: sequence
        A sequence of strings of the form A=>B where 'A' is a Python regex and
        'B' the corresponding replacement string; track locations will be run
        through these
    utf8: boolean
        An optional boolean indicating whether UTF-8 encoding shall be used
    only: sequence
        An optional sequence of titles; if non-None, only the playlists
        contained herein will be exported
    execlude: sequence
        An optional sequence of titles; if non-None, the playlists
        contained herein will not be exported

    'rename' is a textual string where each character represents a
    given transformation to be performed on the title. The following
    characters are supported:

        'l': Convert the title to lower case
        '-': Replace whitespace with '-'s

    """

    log = logging.getLogger(__name__)

    if not os.path.isfile(filename):
        log.error(filename + " (for " + title + ") does not appear to exist!")
        return

    # Discard the header
    lines = decode_file(filename, codepage)[1:]

    tracks = []
    extinfo = None
    # Walk the lines, parsing out extended info if it's there
    for line in lines:
        m = EXTINF_REGEX.match(line)
        if None != m:
            extinfo = (m.group(1), m.group(2))
        else:
            extinfo = None
            tracks.append((line,extinfo))

    # Encode tracks
    lines = convert_tracks_to_m3u(tracks, use_bom)

    # Process replacement strings
    outlines = process_replacements(lines, regexes)

    # OK-- 'outlines' is the actual output
    new_name = rubepl.process_playlist_name(title, rename)
    log.info(title + ' => ' + new_name)

    if utf8:
        outf = new_name + ".m3u8"
        outcp = 'utf_8'
    else:
        outf = new_name + ".m3u"
        outcp = 'cp1252'

    if output: outf = os.path.join(output, outf)

    open(outf, 'w', -1, outcp).writelines(outlines)


**Old Call Tree**:

  + _get_winamp_ml_pls: Retreive playlists from a Winamp ML & convert
    them to another format.
    |
    +- winamp.extract_winamp_ml_playlists
      |
      +- regexes_for_replacements
      |
      +- convert.normalize_m3u_playlist: Take a playlist as input,
       	 perhaps rename it, decode the file to Unicode, apply a series
       	 of replacements to each line, and write it out in another
       	 encoding. The replacments are created like so:

       	    regexes = []
       	    if replacements:
       	        for replacement in replacements:
       	            regexes.append(
       	                rubepl.process_replacement_string(replacement))


        |
        +- process.process_playlist_name: Transforma playlist name
        |
        +- process.process_replacement_string: Process a
           configuration-specified replacement string into a
           (regex,replacement string) tuple

        |
        +- decode.decode_file: Take the path of a playlist, decode
         according to a given CP

        |
        +- encode.encode_line: Encode arbitrary text to UTF-8 & strip
         WS

        |
        +- encode.maybe_add_utf8_bom: Add UTF-8 BOM to a line if it's
         not already there


  + _get_playlists_xml_pls: Retrieve playlists from a "playlists.xml"
    & convert them to another format. I think I wrote this because
    Rhythmbox stores all it's playlists in one big file named
    "playlists.xml".
    |
    +- rhythmbox.extract_playlists_xml_playlists: Extract playlists
       from a Rhythmbox-style 'playlists.xml' & convert them to M3U
       format
       |
       +- process.process_playlist_name: Transforma playlist name
       |
       +- m3u.convert_tracks_to_m3u: Convert a collection of tracks
          with optional extended information to M3U format
          |
          +- encode.encode_line
          |
          +- encode.maybe_add_utf8_bom

       |
       +- m3u.process_replacements: Apply a set of regexes &
        replacement strings to textlines
  


  + _normalize_m3u_pls: Convert one or more playlists from one format
    to nother, or from one title to another
    |
    +- regexes_for_replacements
    |
    +- convert.normalize_m3u_playlist: Take a playlist as input,
       perhaps rename it, decode the file to Unicode, apply a series
       of replacements to each line, and write it out in another
       encoding


  + _get_tracks_from_m3us: Print the list of racks for one or more
    .m3u playlists.
    |

    +- m3u.get_tracks_from_m3u: Read a playlist in M3U format & dump
       the path to each file therein.
       |
       +- decode.decode_file
       |
       +- decode.maybe_remove_bom


  + _itunify_m3u: Convert a playlist in M3U format to one suitable for
    importing into iTunes. This mostly consists of mapping the files n
    the input M3U playlist to their location in the iTunes library &
    riting a new .m3u8 file.
    |
    +- itunes.m3u_to_itunes: Convert an arbitrary M3U (or EXTM3U) playlist to one suitable for importing
       into a local iTunes library.
       |
       +- decode.decode_file


