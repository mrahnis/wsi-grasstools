# for some conventions see:
# https://grasswiki.osgeo.org/wiki/Working_with_GRASS_without_starting_it_explicitly

from __future__ import print_function

import sys
import os
import uuid
# import binascii
import shutil


def time_diff(t0, t1):
    m, s = divmod(t1 - t0, 60)
    h, m = divmod(m, 60)

    return '%d:%02d:%02d' % (h, m, s)


def initialize(gisdbdir=None, location=None, mapset=None):
    if gisdbdir is None:
        # determine platform-specific grassdata location
        if sys.platform.startswith('linux'):
            gisdbdir = os.path.join(os.path.expanduser('~'), 'grassdata')
        elif sys.platform.startswith('win'):
            gisdbdir = os.path.join(os.path.expanduser('~'), 'Documents', 'grassdata')
        else:
            OSError('Platform not configured.')

    if location is None:
        # string_length = 16
        # location = binascii.hexlify(os.urandom(string_length))
        location = uuid.uuid4().hex

    if mapset is None:
        mapset = 'PERMANENT'

    return gisdbdir, location, mapset


def clean(location_path):
    print('Removing location {}'.format(location_path))
    shutil.rmtree(location_path)
