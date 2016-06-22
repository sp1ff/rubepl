"""rubepl -- A collection of utilities for working with playlists"""


__author__     = "Michael Herstine <sp1ff@pobox.com>"
__copyright__  = "Copyright (C) 2015-2016 Michael Herstine"
__credits__    = ["Michael Herstine"]
__license__    = "GPL"
__version__    = "$Revision: $"
__maintainer__ = "Michael Herstine <sp1ff@pobox.com>"
__email__      = "sp1ff@pobox.com"
__status__     = "Prototype"
__all__        = ['decode', 'encode', 'm3u', 'winamp']


import argparse
import logging
import os.path
import sys

from rubepl.winamp import build_subparser as build_winamp_subparser
from rubepl.m3u import build_normalize_subparser as build_normalize_subparser
from rubepl.m3u import build_get_tracks_subparser as build_get_tracks_subparser
from rubepl.rhythmbox import build_subparser as build_rhythmbox_subparser
from rubepl.itunes import build_subparser as build_itunes_subparser

def process_playlist_name(title, rename):
    """Compute the new name of a playlist.

    title: Playlist title
    rename: Encoding of how the title shall be processed to produce
            a playlist filename (on which more below)

    This function will take a playlist title, process it, and return a
    name suitable for use as an output file.  'title' is assumed to be
    the playlist title as listed in 'playlists.xml'. 'rename' is a
    textual string where each character represents a given
    transformation to be performed on the title. The following
    characters are supported:

        'l': Convert the title to lower case
        '-': Replace whitespace with '-'s

    """

    if not rename:
        return title

    new_name = title

    while len(rename) != 0:
        if rename[0] == 'l':
            new_name = new_name.lower()
        elif rename[0] == '-':
            new_name = new_name.replace(' ', '-')
        else:
            raise Exception("unknown rename code '{}'".
                            format(rename[0]))
        rename = rename[1:]

    return new_name

def build_parser():
    """Build an argparse.ArgumentParser containing the command-line options for the
    'rubepl' program.

    :return: an ArgumentParser instances configured for the rubepl options &
    sub-commands

    Cf. `here <https://docs.python.org/2/library/argparse.html#module-argparse>`_.
    """

    parser = argparse.ArgumentParser(description='Work with playlists in '
                                     + 'various ways')
    parser.add_argument('-d', '--debug', help='Turn on debug output',
                        action='store_true')

    subparsers = parser.add_subparsers()
    build_winamp_subparser(subparsers)
    build_normalize_subparser(subparsers)
    build_get_tracks_subparser(subparsers)
    build_rhythmbox_subparser(subparsers)
    build_itunes_subparser(subparsers)

    return parser

def configure_logging(debug=None, logfile=None):
    """Configure logging for the rubepl program.

    :param boolean debug: If non-None, enable logging at level logging.DEBUG
    :param str logfile: If non-None, log to this file as well as stdout

    Log to stdout at level logging.INFO or logging.DEBUG (according to
    parameter debug). Optionally log to file at level logging.DEBUG.
    """

    level = logging.DEBUG if debug else logging.INFO

    logger = logging.getLogger('')
    logger.setLevel(level)

    console = logging.StreamHandler(sys.stdout)
    console.setLevel(level)
    console.setFormatter(logging.Formatter('%(message)s'))

    logger.addHandler(console)

    if logfile:
        filehand = logging.FileHandler(logfile)
        filehand.setLevel(logging.DEBUG)
        filehand.setFormatter(
            logging.Formatter('%(asctime)-15s %(message)s'))
        logger.addHandler(filehand)

def main(args=None):
    """rubepl entry point"""
    try:
        args = build_parser().parse_args(args)
        configure_logging(args.debug)
        args.func(args)
    except SystemExit:
        pass


# __init__.py ends here.
