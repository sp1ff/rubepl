"""Assorted utilities for working with iTunes"""

__author__     = "Michael Herstine <sp1ff@pobox.com>"
__copyright__  = "Copyright (C) 2015, 2016 Michael Herstine"
__license__    = "GPL"
__version__    = "$Revision: $"
__email__      = "sp1ff@pobox.com"
__status__     = "Prototype"

import logging
import os.path
import re
import xml.etree.ElementTree as ET

from rubepl.encode import encode_line
from rubepl.decode import decode_file, decode_track_location

ITUNES_XML = os.path.expanduser('~/Music/iTunes/iTunes Music Library.xml')

log = logging.getLogger(__name__)

def build_track_map(itunes_xml=ITUNES_XML):
    """Build a map of iTunes tracks mapping (artist,title) pairs to
    (location,duration) pairs.

    iTunes stores an index of all it's files in a file named 'iTunes Music
    Library.xml'. Each track in the library is represented as a bag of
    attributes, including Artist, Name (i.e. the track name), Duration (in
    milliseconds) and Location (i.e. the filesystem path to to the audio
    file). This function will walk that file and build a dictionary mapping
    tracks in the form of (Artst, Title) to Locations & Durations in the iTunes
    library.

    I chose this datastructure to support a two-phase approach to mapping M3U entries
    to iTunes tracks. Try to simply use the artist & title, and if that fails, walk
    the entire map looking for likely matches.

    N.B. Sometimes iTunes stores the artist in the 'Artist' key, and sometimes it
    stores the entire track name in the 'Name' key

    """

    elts = ET.parse(itunes_xml).getroot().getchildren()[0].getchildren()

    # Find the key named 'Tracks'; the next one will be the dictionary we're
    # looking for.
    D = dict()
    for i in range(0, int(len(elts)/2)):
        D[elts[2*i].text] = elts[2*i+1]

    tracks = D['Tracks'].getchildren()[1::2]

    out = dict()
    for track in tracks:
        D = dict()
        children = track.getchildren()
        for i in range(0, int(len(children)/2)):
            D[children[2*i].text] = children[2*i+1].text
        if not 'Location' in D:
            log.warning("'{0}' contains no Location attribute".format(D));
        else:
            artist = None
            name = None
            time = None
            if 'Artist' in D:
                artist = D['Artist']
            if 'Name' in D:
                name = D['Name']
            if 'Total Time' in D:
                time = int(round(float(D['Total Time']) / 1000.0))

            if None != artist or None != name:
                location = decode_track_location(D['Location'])
                log.debug('build_file_map: ({0},{1}) => ({2},{3})'.
                          format(artist, name, location, time))
                out[(artist, name)] = (location,time)

    return out

def levenshtein(s, t):
    """Compute the Levenshtein distance between two strings.

    Compute the edit distance between two strings. I copied the implementation
    from Wikipedia article; Iterative with two matrix rows.

    Retrieved from http://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Levenshtein_distance#Python
    """

    if s == t: return 0
    elif len(s) == 0: return len(t)
    elif len(t) == 0: return len(s)
    v0 = [None] * (len(t) + 1)
    v1 = [None] * (len(t) + 1)
    for i in range(len(v0)):
        v0[i] = i
    for i in range(len(s)):
        v1[0] = i + 1
        for j in range(len(t)):
            cost = 0 if s[i] == t[j] else 1
            v1[j + 1] = min(v1[j] + 1, v0[j + 1] + 1, v0[j] + cost)
        for j in range(len(v0)):
            v0[j] = v1[j]

    return v1[len(t)]

def _try_to_make_extinf(text):
    """Take a line of text & try to interpret it as M3U extended track
    information. If such an interpretation is possible, return the
    corresponding ExtInfo instance. Else, return None.
    """

    regex = re.compile('^\\s*#\\s*EXTINF:\\s*([0-9]+),(.*)');
    what = regex.match(text)
    if not what:
        return None

    return ExtInf(int(what.group(1)), what.group(2))

class ExtInf(object):
    """Representation of track extended info convenient for matching iTunes
    tracks.

    Cf. http://tools.ietf.org/html/draft-pantos-http-live-streaming-08#page-6
    """

    REGEX = re.compile('^([^-]+)-(.*)')

    def __init__(self, duration, title):
        """Construct with the track duration & title.

        EXTM3U format playlists will provide the duration & title. My
        (personal) convention is to title tracks "$artist - $title"-- if the
        give title conforms to that convention, we parse the artist & title, as
        well.

        TODO: Get the artist & title from ID3 tags, as well.
        """

        self._duration = duration
        self._title = title
        # Attempt to parse the track title as $artist - $title
        match = self.REGEX.match(title)
        if match:
            self._artist = match.group(1).strip()
            self._track = match.group(2).strip()
        else:
            self._artist = self._track = None

    def __str__(self):
        if self._artist and self._track:
            return '{{{0}, "{1}", "{2}", "{3}"}}'.format(self._duration, self._title,
                                                         self._artist, self._track)
        else:
            return '{{{0}, "{1}", nil, nil}}'.format(self._duration, self._title)

    def get_duration(self):
        return self._duration

    def parsed_artist_and_track(self):
        return None != self._artist or None != self._track

    def get_artist(self):
        return self._artist

    def get_track(self):
        return self._track

    def get_title(self):
        return self._title

    def writeln(self, out):
        out.write('{0}\n'.format(
            encode_line('#EXTINF:{0},{1} - {2}'.
                        format(self._duration, self._artist, self._title))))

class M3UTrack(object):
    """Representation of a single track in a format convenient for matching iTunes
    tracks."""

    def __init__(self, text, extinfo=None):
        """Initialize a track from an M3U or EXTM3U playlist.

        :param ExtInf extinf: Extended track information parsed from an EXTINF
        entry
        :param string text: File path
        """
        self._extinfo = extinfo
        name = os.path.splitext(os.path.basename(text))[0]
        regex = re.compile('^([^-]+)-(.*)')
        what = regex.match(name)
        if what:
            self._artist = what.group(1).strip()
            self._title = what.group(2).strip()
        elif self._extinfo:
            self._artist = self._extinfo.get_artist()
            self._title = self._extinfo.get_title()
        else:
            self._artist = self._title = None

    def get_extinfo(self):
        return self._extinfo

    def get_artist(self):
        return self._artist

    def get_title(self):
        return self._title

def find_best_match(D, artist, title, duration=None, max_distance=None):
    """Find the best match for 'artist', 'title' and 'duration' within a local
    iTunes library as represented by 'D' (a mapping of (artist,title) to
    (location,duration).

    :param dict D: a mapping built from the local iTunes library of
    (artist,title) pairs to (location,duration) pairs
    :param string artist: Artist name
    :param string title: Track title
    :param int duration: Track duration, in seconds
    :param int max_distance: the maximum edit distance between 'artist - title'
    and the best fit in D; recommended values are on the order of 6-12 (None
    implies unlimited)
    :ret: the location of the "best' match to artist, title & duration, or None
    if none could be found

    If we're here, we've given up on finding an exact match and have fallen back to looking
    for the closest.
    """

    log.debug('best match: {0}/{1}/{2} ='.
              format(artist, title, duration if duration else 'nil'))

    text = artist + " - " + title
    best_distance = -1
    best_locations = []
    best_match = None
    for key in D.keys():
        value = D[key]
        test = None
        artist = key[0]
        title = key[1]
        if artist and title:
            test = artist + " - " + title
        elif artist:
            test = artist
        else:
            test = title

        distance = levenshtein(text, test)
        if duration:
            track_duration = 0 if value[1] is None else value[1]
            distance = distance + abs(duration - track_duration)

        if -1 == best_distance or distance <= best_distance:
            if distance == best_distance:
                best_locations.append(value[0])
            else:
                best_distance = distance
                best_locations = [value[0],]
            best_match = test

    log.debug('    = {0} => {1}/{2}'.format(best_distance, best_match, best_locations))

    if max_distance and best_distance > max_distance:
        log.warning(('The best match to "{0}"/"{1}"/{2} was "{3}"/"{4}", which has an edit'
                     + ' distance of {5}, greater than the maximum ({6})... skipping.').
                    format(artist, title, duration if duration else 'nil', best_match,
                           best_locations, best_distance, max_distance))
        return None
    else:
        best_locations.sort()
        return best_locations[0]

def match_itunes_track(track, D, max_distance=None):
    """Attempt to match a track as defined in an M3U file to one in a local iTunes
    library.

    :param M3UTrack track: The M3U track to be matched with an iTunes track
    :param dict D: A dictionary mapping (artist,title) information to
    (location,duration). Duration shall be in seconds, expressed as a int.
    :param int max_distance: The maximum edit distance for a match to be found

    :ret: (ExtInfo,string): M3U Extended Track information, if any, and the
    location of the track in the local iTunes library if a match was found;
    None else
    """

    log.debug('Track {{{0},"{1}","{2}"}} =>'.format(track.get_extinfo(),
                                                    track.get_artist(),
                                                    track.get_title()))

    # First, try a simple lookup based on track information
    artist = track.get_artist()
    title = track.get_title()
    log.debug('looking for ("{0}","{1}") in the map...'.format(artist, title))
    if (artist, title) in D:
        (location, duration) = D[(artist, title)]
        log.debug('    ({0},{1}) (track info)'.format(track.get_extinfo(), location))
        return (track.get_extinfo(), location)

    # Next, try to update our "best guess" as to the artist & track
    extinfo = track.get_extinfo()
    if extinfo and extinfo.parsed_artist_and_track():
        artist = extinfo.get_artist()
        title = extinfo.get_track()
        log.debug('artist/track now "{0}"/"{1}"...'.format(artist, title))
        # & try again:
        if (artist, title) in D:
            (location, duration) = D[(artist, title)]
            log.debug('    ({0},{1}) (extinfo artist & track)'.format(extinfo, location))
            return (extinfo, location)

    # Next, if we have Extended Info, look for the best match using artist, track & duration
    if extinfo:
        location = find_best_match(D, artist, title, extinfo.get_duration(),
                                   max_distance)
        if location:
            log.debug('    ({0},{1}) (extinfo duration)'.format(extinfo, location))
            return (extinfo, location)

    # Finally, just look for the best match using artist & track
    location = find_best_match(D, artist, title, None, max_distance)
    if location:
        log.debug('    ({0},{1}) (fallback)'.format(extinfo, location))
        return (extinfo, location)
    else:
        log.debug('    None')
        return None

def m3u_to_itunes(m3u, outfile, itunes_xml=ITUNES_XML,
                  codepage=None, max_distance=None):

    """Convert an arbitrary M3U (or EXTM3U) playlist to one suitable for importing
    into a local iTunes library.

    :param string m3u: path to the input M3U file to be transformed
    :param string outfile: path to the output file
    :param string codepage: codepage (e.g. 'cp1252') to be used to read the
    input file; defaults to 'cp1252'

    This function will attempt to match each track in the input M3U file to a
    track in the local iTunes library and produce an M3U playlist containing
    the same tracks in the same order but referencing their location in the
    local iTunes library.

    This means identifying each track in the same way iTunes identifies it,
    locating that track's location in the iTunes library & writing a new .m3u8
    file.

    Notes
    -----
    The problem here is to take an entry in the input M3U file & map it to an
    entry in the iTunes library.

    On the input side, we'll have:

    - a path to the .mp3 file, we'll definitely have the .mp3 file path, which by
      *my* convention will be 'artist name - track title.mp3'
    - we will likely have an EXTINF entry for it, which technically gives a
      duration (in seconds) and a display title, but empirically, the latter
      contains a more reliable version of the artist name & track title, unless
      one or both contain dashes.

    On the iTunes side, we'll have:

    - Name & generally speaking, Artist tags
    - a Location; the latter will take the form 'track-# track title' (XML encoded),
      I guess from tag information
    - a duration which empirically is in milliseconds

    So the best solution, I think, is to read the ID3 tags of the original
    files, use the artist & title fields to index into the iTunes library to
    get the file's location in iTunes, but I can't do that right now.

    My fallback solution is:

    - guess the artist & title from track path in the input M3U file & attempt
      to map them into the iTunes library. If that works, we're done
    - else if we have extended track information, and if it contains a title,
      and if that title contains a single '-', update our guess for the artist
      & track title & re-try. If *that* works, we're done.
    - else if we have extended track information, use our best guess for artist
      & track along with the duration, and walk the iTunes library looking for
      the "best" match & use that.
    - else walk the iTunes library looking for the "best" match to artist name
      & track title as as we have them & use that.

    That, of course, begs the question of what the "best" match is in terms of
    (artist, title) or (artist,title,duration). This is TBD. The obvious
    candidate for artist & title would be edit distance, but I wonder if that
    is really what we want. The failures I'm seeing involve the dropping of
    assorted suffxies, e.g.  'Dixie Chicks - Travelin' Soldier (Album Version)
    ' ~ 'Dixie Chicks - Travelin' Soldier (Album Version) [Clean]', so prefix
    matching might be better.

    TODO: Document the algorithm I ultimately choose.
    """

    # TODO: Debugging only!
    for hand in logging.getLogger(None).handlers:
        hand.setLevel(logging.DEBUG)

    # D will map (artist,title) => (location,duration in sec.)
    D = build_track_map(itunes_xml)

    # For each track in 'm3u', build a representation that includes:
    #   * the extended information, if any
    #   * our best guess as to the artist name & track title
    tracks = list()
    lines = decode_file(m3u, codepage)

    state = 0
    extinf = None
    for i in range(1, len(lines)):
        log.debug('{0}/{1}: {2}'.format(i, state, lines[i].strip()))
        if 0 == state:
            # Next line may be #EXTINF, or it may just be a track
            extinf = _try_to_make_extinf(lines[i])
            if extinf:
                state = 1
            else:
                tracks.append(M3UTrack(lines[i]))
        else:
            state = 0
            tracks.append(M3UTrack(lines[i], extinf))
            extinf = None

    log.debug(tracks)

    # Then, we'll walk that ordered list, and for each track, make our best
    # guess, based on 'D', as to what the corresponding track is in iTunes (if
    # any)
    matches = list()
    for i in range(0, len(tracks)):
        match = match_itunes_track(tracks[i], D, max_distance)
        if match:
            matches.append(match)

    log.debug(matches)

    # Finally, we'll walk the remaining list, writing the tracks to the output
    # file.
    with open(outfile, 'w') as out:
        out.write('{0}\n'.format(encode_line(lines[0])))
        for (extinfo, location) in matches:
            if extinfo:
                extinfo.writeln(out)
            out.write('{0}\n'.format(encode_line(location)))

def _itunify_m3u(args):
    """Convert a playlist in M3U format to one suitable for importing into iTunes.

    This function will extract parsed arguments from the caller-provided
    Namespace & pass them on to the implementation.

    """

    m3u_to_itunes(args.file, args.output, itunes_xml=args.itunes_db,
                  codepage=args.codepage, max_distance=args.max_edit_distance)

def build_subparser(subparsers, name='itunify-m3u'):

    itunify = subparsers.add_parser(
        name=name, help='Convert a playlist in M3U format to one suitable '
        + 'for importing into iTunes. This mostly consists of mapping the files '
        + 'in the input M3U playlist to their location in the iTunes library & '
        + 'writing a new .m3u8 file.')
    itunify.add_argument('-c', '--codepage', help='specify the input codepage')
    itunify.add_argument('-o', '--output', help='output file')
    itunify.add_argument('-m', '--max-edit-distance', type=int,
                           help='Maximum edit distance for a match')
    itunify.add_argument('-i', '--itunes-db', help='path to the iTunes XML file'
                         + ' containing the music library (defaults to'
                         + ' ~/Music/iTunes/iTunes Music Library.xml)',
                         default=ITUNES_XML)
    itunify.add_argument('file', help='Playlist to be converted')

    itunify.set_defaults(func=_itunify_m3u)
