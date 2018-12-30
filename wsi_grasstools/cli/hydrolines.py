from __future__ import print_function

import os
from time import clock

import click

from wsi_grasstools.manage import initialize, setup_env, time_diff
gisbase, gisdbdir = setup_env()

import grass.script as g


@click.command(options_metavar='<options>')
@click.argument('infile', nargs=1, type=click.Path(exists=True))
@click.argument('dst', nargs=1, type=click.Path(exists=True))
@click.option('--mod', nargs=1, default=10, help="r.hydrodem mod parameter")
@click.option('--size', nargs=1, default=40, help="r.hydrodem size parameter")
@click.option('--threshold', nargs=1, default=5000,
              help="r.watershed threshold parameter")
@click.option('--d8cut', nargs=1, default=1000000,
              help="r.stream.extract d8cut parameter")
@click.option('--mexp', nargs=1, default=1.2,
              help="r.stream.extract mexp parameter")
@click.option('--stream-length', nargs=1, default=100,
              help="r.stream.extract stream_length parameter")
@click.pass_context
def hydrolines(ctx, infile, dst, mod, size, threshold, d8cut, mexp, stream_length):
    """Create stream centerlines and other products

    Parameters:
        mod : r.hydrodem mod
        size : r. hydrodem size
        threshold : r.watershed threshold
        d8cut : r.stream.extract d8cut
        mexp : r.stream.extract mexp
        stream_length : r.stream.extract stream_length
    """

    t0 = clock()

    location, mapset = initialize(gisbase, gisdbdir,
                                  location=ctx.obj['location'],
                                  mapset=ctx.obj['mapset'],
                                  infile=infile,
                                  epsg=ctx.obj['epsg'])

    fname = os.path.basename(infile).split('.')[0]

    click.echo(click.style('Loading DEM', fg='green'))
    click.echo(click.style('GRASS layer: {}'.format(fname), fg='green'))
    g.run_command('r.in.gdal', input=infile,
                  output=fname, overwrite=True)

    click.echo(click.style('Running hydrodem', fg='green'))
    g.run_command('r.hydrodem', input=fname, overwrite=True,
                  output='hydem',
                  mod=mod,
                  size=size)

    click.echo(click.style('Running watershed directions', fg='green'))
    g.run_command('r.watershed', flags='am', overwrite=True,
                  elevation='hydem',
                  threshold=threshold,
                  drainage='dirs')

    click.echo(click.style('Running watershed accumulation', fg='green'))
    g.run_command('r.watershed', flags='am', overwrite=True,
                  elevation='hydem',
                  threshold=threshold,
                  accumulation='acc')

    click.echo(click.style('Running stream extract', fg='green'))
    g.run_command('r.stream.extract', overwrite=True,
                  elevation='hydem',
                  accumulation='acc',
                  direction='dirs_',
                  threshold=threshold,
                  d8cut=d8cut,
                  mexp=mexp,
                  stream_length=stream_length,
                  stream_rast='hydem_streams',
                  stream_vect='hydem_streams_vec')

    g.run_command('r.stream.order', overwrite=True,
                  stream_rast='hydem_streams',
                  direction='dirs_',
                  strahler='strahler')

    g.run_command('r.to.vect', overwrite=True,
                  input='strahler',
                  output='strahler_vec',
                  type='line')

    g.run_command('r.stream.basins', overwrite=True,
                  dir='dirs',
                  stream='hydem_streams',
                  basins='basins_elem')

    g.run_command('r.stream.basins', overwrite=True,
                  flags='l',
                  dir='dirs',
                  stream='hydem_streams',
                  basins='basins_last')

    g.run_command('r.to.vect', overwrite=True,
                  input='basins_elem',
                  output='basin_elem_vec',
                  type='area')

    g.run_command('r.to.vect', overwrite=True,
                  input='basins_last',
                  output='basin_last_vec',
                  type='area')

    g.run_command('r.stream.distance', overwrite=True,
                  stream_rast='hydem_streams',
                  direction='dirs',
                  elevation=fname,
                  method='downstream',
                  difference='above_stream')

    click.echo(click.style('Exporting', fg='green'))
    g.run_command('r.out.gdal', overwrite=True,
                  input='acc', type='Float64',
                  output=os.path.join(dst, 'fac.tif'),
                  format='GTiff', createopt='TFW=YES,COMPRESS=LZW')

    g.run_command('r.out.gdal', overwrite=True,
                  input="dirs", type='Float64',
                  output=os.path.join(dst, 'dirs.tif'),
                  format='GTiff', createopt='TFW=YES,COMPRESS=LZW')

    g.run_command('v.out.ogr', overwrite=True,
                  input='hydem_streams_vec',
                  output=os.path.join(dst, 'stream_ln.shp'),
                  format='ESRI_Shapefile',
                  type='line')

    g.run_command('v.out.ogr', overwrite=True,
                  input='strahler_vec',
                  output=os.path.join(dst, 'strahler_ln.shp'),
                  format='ESRI_Shapefile',
                  type='line')

    g.run_command('v.out.ogr', overwrite=True,
                  input='basin_last_vec',
                  output=os.path.join(dst, 'basin_last_ply.shp'),
                  format='ESRI_Shapefile',
                  type='area')

    g.run_command('v.out.ogr', overwrite=True,
                  input='basin_elem_vec',
                  output=os.path.join(dst, 'basin_elem_ply.shp'),
                  format='ESRI_Shapefile',
                  type='area')

    g.run_command('r.out.gdal', overwrite=True,
                  input='above_stream', type='Float64',
                  output=os.path.join(dst, 'hand.tif'),
                  format='GTiff', createopt='TFW=YES,COMPRESS=LZW')

    elapsed = time_diff(t0, clock())
    click.echo(click.style('Finished in:', fg='green'))
    click.echo(click.style(elapsed, fg='green'))
