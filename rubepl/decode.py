"""Assorted utilities for decoding playlists."""


__author__     = "Michael Herstine <sp1ff@pobox.com>"
__copyright__  = "Copyright (C) 2015-2016 Michael Herstine"
__credits__    = ["Michael Herstine"]
__license__    = "GPL"
__version__    = "$Revision: $"
__maintainer__ = "Michael Herstine <sp1ff@pobox.com>"
__email__      = "sp1ff@pobox.com"
__status__     = "Prototype"


import codecs
import html.parser
import logging
import os
import urllib.parse


def decode_track_location(name):
    """iTunes & Rhythmbox encode the locations of audio files as XML-encoded
    URIs. This method will decode them.

    :param str name: an XML-encoded URI
    :return:
    """

    # Even tho I've used library code to do all this, I want to explain what's
    # going on. 'name' will be text from an XML file, and XML reserves the
    # following characters & requires them to be encoded as follows:

    # <  &lt;
    # >  &gt;
    # &  &amp;
    # "  &quot;
    # '  &apos;

    # XML also seems to permit 'numeric character references' of the form
    # &#nnnn; or &#xnnnn; (the former being decimal & the latter hex).

    # So let's un-escape the XML, first:
    # TODO: name = html.parser.HTMLParser().unescape(name)
    name = html.unescape(name)

    # Now, since the location is a URI, it will, in general, be URI-encoded
    # (AKA %-encoded). For instance, ' ' is represented as %20 (%-encoding is
    # always in hex). ASCII characters are represented using their ASCII values
    # (in hex, of course) and non-ASCII characters are represented by their
    # UTF-8 values, each byte being separately encoded (e.g. Combining Acute
    # Accent, UTF-8 value 0xcc81, would be encoded as %cc%81).

    # So, let's parse 'name' as a URI...
    split = urllib.parse.urlsplit(name)
    # 'split.path' will contain the file path, which needs to be unquoted...
    return urllib.parse.unquote(split.path)

def handle_decode_err_by_fb_cp1252(ex):
    """codecs-compliant error handler.

    I've encountered files that claim to be UTF-8 encoded (i.e. they end in
    '.m3u8' and/or contain the UTF-8 BOM 0xef, 0xbb, 0xbf), but contain
    single-byte characters that in fact come from the Microsoft Windows code
    page 1252 (Windows Latin 1). Maybe the encoder erroneously assumed the
    input was ASCII, and so translation to UTF-8 was trivial?
    """

    bad = ex.object[ex.start:ex.end]
    if 1 == len(bad):
        try:
            text = codecs.decode(bad,'cp1252')
        except:
            raise ex
        return (text, ex.end)
    raise ex

def maybe_remove_bom(line):
    """Check 'line' for a UTF-8 BOM & remove it if it's there. Return the result."""

    binary = line.encode('utf-8')
    if len(binary) > 2 and 239 == binary[0] and \
       187 == binary[1] and 191 == binary[2]:
        binary = binary[3:]

    return binary.decode('utf-8')

def decode_file(filename, codepage=None):
    """Read 'filename', strip the BOM if present, strip any leading or trailing
    whitespace, return a list of Python strings.

    In order to read the file, we need to know the file's encoding (i.e. how
    the writer represented the characters contained therein-- ASCII, UTF-8, or
    whatever).  The caller can specify the file encoding explicitly, or set
    'codepage' to None to have this function try to deduce the file encoding.

    TODO: Document in more detail exactly what is returned-- i.e. what exactly
    does readlines return when the file is opened with an 'encoding' parameter?
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

    with open(filename, 'r', -1, incp, errs) as fh:
        lines = fh.readlines();
    lines[0] = maybe_remove_bom(lines[0])

    return lines
