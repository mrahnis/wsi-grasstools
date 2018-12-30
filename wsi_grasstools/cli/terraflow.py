from __future__ import print_function

import sys
import os
from time import clock

import click

from wsi_grasstools.manage import initialize, setup_env, time_diff
gisbase, gisdbdir = setup_env()

import grass.script as g


@click.command(options_metavar='<options>')
@click.argument('infile', nargs=1, type=click.Path(exists=True))
@click.argument('dst', nargs=1, type=click.Path(exists=True))
@click.option('--threshold', nargs=1, default=1500, help="r.watershed threshold parameter")
@click.pass_context
def terraflow(ctx, infile, dst, threshold):
    """Create first order raster hydrography products including basins

    Writes output files:

        <fname>_outlets.tif
        <fname>_fsc.tif
        <fname>_fdr.tif
        <fname>_basins.tif

    Parameters:
        threshold : r.watershed threshold

    Returns:
        None

    """

    t0 = clock()

    location, mapset = initialize(gisbase, gisdbdir, location=ctx.obj['location'],
                                  mapset=ctx.obj['mapset'], infile=infile, epsg=ctx.obj['epsg'])

    fname = os.path.basename(infile).split('.')[0]

    click.echo(click.style('Loading DEM', fg='green'))
    click.echo(click.style('GRASS layer: {}'.format(fname), fg='green'))
    g.run_command('r.in.gdal', input=infile,
                  output=fname, overwrite=True)

    g.run_command('r.watershed', flags='am', overwrite=True,
                  elevation=fname,
                  threshold=threshold,
                  accumulation='acc',
                  drainage='dra')

    print('Identify outlets by negative flow direction')
    g.run_command('r.mapcalc', overwrite=True,
                  expression='outlets = if(dra >= 0,null(),1)')

    print('Convert outlet raster to vector')
    g.run_command('r.to.vect', overwrite=True,
                  input='outlets', output='outlets_vec',
                  type='point')

    print('Delineate basins according to outlets')
    g.run_command('r.stream.basins', overwrite=True,
                  direction='dra', points='outlets_vec',
                  basins='bas')

    # Save the outputs as TIFs
    outlets_fname = fname + '_outlets.tif'
    g.run_command('r.out.gdal', overwrite=True,
                  input='outlets', type='Float32',
                  output=os.path.join(dst, outlets_fname),
                  format='GTiff')

    fac_fname = fname + '_fac.tif'
    g.run_command('r.out.gdal', overwrite=True,
                  input='acc', type='Float64',
                  output=os.path.join(dst, fac_fname),
                  format='GTiff')

    fdr_fname = fname + '_fdr.tif'
    g.run_command('r.out.gdal', overwrite=True,
                  input='dra', type='Float64',
                  output=os.path.join(dst, fdr_fname),
                  format='GTiff')

    bas_fname = fname + '_basins.tif'
    g.run_command('r.out.gdal', overwrite=True,
                  input='bas', type='Int16',
                  output=os.path.join(dst, bas_fname),
                  format='GTiff')

    elapsed = time_diff(t0, clock())
    click.echo(click.style('Finished in:', fg='green'))
    click.echo(click.style(elapsed, fg='green'))
