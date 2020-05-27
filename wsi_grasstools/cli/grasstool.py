import sys
import logging
from pkg_resources import iter_entry_points

import click
from click_plugins import with_plugins

import wsi_grasstools
from wsi_grasstools.manage_session import initialize

logger = logging.getLogger(__name__)


@with_plugins(iter_entry_points('wsi_grasstools.subcommands'))
@click.group()
@click.option('--dbdir', 'dbdir', nargs=1, default=None)
@click.option('--location', 'location', nargs=1, default=None)
@click.option('--mapset', 'mapset', nargs=1, default=None)
@click.option('--epsg', 'epsg', nargs=1, default=None)
@click.option('-v', '--verbose', default=False, is_flag=True, help="Enables verbose mode")
@click.version_option(version=wsi_grasstools.__version__, message='%(version)s')
@click.pass_context
def cli(ctx, dbdir, location, mapset, epsg, verbose):
    ctx.obj = {}
    ctx.obj['verbose'] = verbose
    if verbose:
        logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    else:
        logging.basicConfig(stream=sys.stderr, level=logging.ERROR)

    dbdir, location, mapset = initialize(dbdir, location, mapset)

    ctx.obj['dbdir'] = dbdir
    ctx.obj['location'] = location
    ctx.obj['mapset'] = mapset
    ctx.obj['epsg'] = epsg
