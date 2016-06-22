"""Utilities for encoding text for output"""


__author__     = "Michael Herstine <sp1ff@pobox.com>"
__copyright__  = "Copyright (C) 2015-2016 Michael Herstine"
__credits__    = ["Michael Herstine"]
__license__    = "GPL"
__version__    = "$Revision: $"
__maintainer__ = "Michael Herstine <sp1ff@pobox.com>"
__email__      = "sp1ff@pobox.com"
__status__     = "Prototype"


def encode_line(line):
    """Encode a line of arbitrary text to UTF-8. Remove any trailing whitespace."""

    binary = line.encode('utf-8')
    while 0 < len(binary) and (32 == binary[-1] or # ' '
                                9 == binary[-1] or # tab
                               13 == binary[-1] or # CR
                               10 == binary[-1]):  # NL
        binary = binary[:-1]

    return binary.decode()

def maybe_add_utf8_bom(line):
    """Add a UTF-8 BOM to 'line' if it's not already there."""

    binary = line.encode('utf-8')
    if len(binary) > 2 and 239 == binary[0] and \
       187 == binary[1] and 191 == binary[2]:
        return line

    binary = bytearray(binary)
    binary.insert(0, 191)
    binary.insert(0, 187)
    binary.insert(0, 239)

    return binary.decode()
