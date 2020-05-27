from __future__ import print_function

import os
from time import clock

import click

from wsi_grasstools.manage_session import time_diff


@click.command(options_metavar='<options>')
@click.argument('infile', nargs=1, type=click.Path(exists=True))
@click.argument('headfile', nargs=1, type=click.Path(exists=True))
@click.argument('dst', nargs=1, type=click.Path(exists=True))
@click.option('--threshold', nargs=1, default=5000,
              help="r.watershed threshold parameter")
@click.pass_context
def paths(ctx, infile, headfile, dst, threshold):
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

    fname = os.path.basename(infile).split('.')[0]
    hname = os.path.basename(headfile).split('.')[0]

    from grass_session import Session
    import grass.script as g
    from grass.script import core as gcore
    import grass.script.setup as gsetup

    PERMANENT = Session()
    PERMANENT.open(gisdb=ctx.obj['dbdir'],
                   location=ctx.obj['location'],
                   create_opts=ctx.obj['epsg'])
    PERMANENT.close()

    user = Session()
    user.open(gisdb=ctx.obj['dbdir'],
              location=ctx.obj['location'],
              mapset=ctx.obj['mapset'],
              create_opts='')

    click.echo(click.style('Loading DEM', fg='green'))
    click.echo(click.style('GRASS layer: {}'.format(fname), fg='green'))
    g.run_command('r.in.gdal', input=infile,
                  output=fname, overwrite=True)

    g.run_command('v.in.ogr', input=headfile,
                  output=hname, overwrite=True)

    click.echo(click.style('Running watershed directions', fg='green'))
    g.run_command('r.watershed', flags='ams', overwrite=True,
                  elevation='fname',
                  threshold=threshold,
                  drainage='dirs')

    """
    click.echo(click.style('Running watershed accumulation', fg='green'))
    g.run_command('r.watershed', flags='ams', overwrite=True,
                  elevation='fname',
                  threshold=threshold,
                  accumulation='acc')
    """

    click.echo(click.style('Running path tracing', fg='green'))
    g.run_command('r.path', overwrite=True,
                  input='dirs',
                  start_points='hname',
                  raster_path='dem_stream',
                  vector_path='dem_stream_vec')

    g.run_command('r.stream.order', overwrite=True,
                  stream_rast='dem_stream',
                  direction='dirs',
                  strahler='strahler')

    g.run_command('r.to.vect', overwrite=True,
                  input='strahler',
                  output='dem_strahler_vec',
                  type='line')

    g.run_command('r.stream.distance', overwrite=True,
                  stream_rast='dem_stream',
                  direction='dirs',
                  elevation=fname,
                  method='downstream',
                  difference='above_stream')

    click.echo(click.style('Exporting...', fg='green'))
    g.run_command('v.out.ogr', overwrite=True,
                  input='dem_streams_vec',
                  output=os.path.join(dst, 'stream_ln.shp'),
                  format='ESRI_Shapefile',
                  type='line')

    g.run_command('v.out.ogr', overwrite=True,
                  input='strahler_vec',
                  output=os.path.join(dst, 'strahler_ln.shp'),
                  format='ESRI_Shapefile',
                  type='line')

    g.run_command('r.out.gdal', overwrite=True,
                  input='above_stream', type='Float64',
                  output=os.path.join(dst, 'hand.tif'),
                  format='GTiff', createopt='TFW=YES,COMPRESS=LZW')

    user.close()

    elapsed = time_diff(t0, clock())
    click.echo(click.style('Finished in:', fg='green'))
    click.echo(click.style(elapsed, fg='green'))
