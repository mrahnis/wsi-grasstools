# for some conventions see:
# https://grasswiki.osgeo.org/wiki/Working_with_GRASS_without_starting_it_explicitly

from __future__ import print_function

import sys
import os
import subprocess
import uuid
# import binascii
import shutil

sys.path.append(os.path.join(os.environ['GISBASE'], 'etc', 'python'))
import grass.script as g
import grass.script.setup as gsetup


def time_diff(t0, t1):
    m, s = divmod(t1 - t0, 60)
    h, m = divmod(m, 60)

    return '%d:%02d:%02d' % (h, m, s)


def setup_env():
    # determine platform-specific grassdata location
    if sys.platform.startswith('linux'):
        gisdbdir = os.path.join(os.path.expanduser('~'), 'grassdata')
    elif sys.platform.startswith('win'):
        gisdbdir = os.path.join(os.path.expanduser('~'), 'Documents', 'grassdata')
    else:
        OSError('Platform not configured.')

    # set environment variables
    gisbase = os.environ['GISBASE']
    os.environ['GISRC'] = os.path.join(os.path.expanduser('~'), '.grass74')
    os.environ['LD_LIBRARY_PATH'] = os.path.join(gisbase, 'lib')

    # update the path for the current environment
    sys.path.append(os.path.join(gisbase, 'bin'))
    # sys.path.append(os.path.join(gisbase, "etc", "python"))
    sys.path.append(os.path.join(gisbase, 'scripts'))

    return gisbase, gisdbdir


def initialize(gisbase, gisdbdir,
               location=None, mapset=None,
               infile=None, epsg=None):

    # determine the platform-specific startup script
    if sys.platform.startswith('linux'):
        executable = os.path.join(gisbase, 'grass74')
    elif sys.platform.startswith('win'):
        executable = os.path.join(gisbase, 'grass74.bat')
    else:
        OSError('Platform not configured.')

    if location is None:
        # string_length = 16
        # location = binascii.hexlify(os.urandom(string_length))
        location = uuid.uuid4().hex

    location_path = os.path.join(gisdbdir, location)

    if epsg:
        startcmd = '"{0}" -c epsg:{1} -e {2}'.format(executable, epsg, location_path)
    else:
        startcmd = '"{0}" -c {1} -e {2}'.format(executable, infile, location_path)

    p = subprocess.Popen(startcmd, shell=True,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if p.returncode != 0:
        print('ERROR: %s' % err, file=sys.stderr)
        print('ERROR: Cannot generate location (%s)' % startcmd, file=sys.stderr)
        sys.exit(-1)
    else:
        print('Created location %s' % location_path)

    gsetup.init(gisbase, gisdbdir, location, 'PERMANENT')

    if mapset is None:
        mapset = 'PERMANENT'
    else:
        print('create mapset...')
        g.run_command('g.mapset', flags='c', mapset=mapset, location=location, dbase=gisdbdir)
        gsetup.init(gisbase, gisdbdir, location, mapset)

    #vg.run_command('g.mapsets', mapset=mapset, operation='set')
    # os.environ['MAPSET'] = mapset

    return location, mapset


def clean(location_path):
    print('Removing location {}'.format(location_path))
    shutil.rmtree(location_path)
