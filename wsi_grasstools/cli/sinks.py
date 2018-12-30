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
@click.option('--min-depth', nargs=1, default=0.2,
              help="Depth threshold below which sinks will be ignored.")
@click.option('--mask-depth', nargs=1, default=5.0,
              help="Depth above which sinks will be added to the sink mask.")
@click.option('--passes', nargs=1, default=1,
              help="Number of passes to fill depressions.")
@click.pass_context
def sinks(ctx, infile, dst, min_depth, mask_depth, passes):
    """Create sink mask and breach locations

    References:
        https://pubs.usgs.gov/sir/2010/5059/pdf/SIR2010_5059.pdf

    Parameters:
        min_depth (float) : write only sinks above the minimum depth
        max_depth (float) : maximum depth of sink to fill; depths greater than sinks_max are added to a sink mask

    """

    t0 = clock()

    location, mapset = initialize(gisbase, gisdbdir,
                                  location=ctx.obj['location'],
                                  mapset=ctx.obj['mapset'],
                                  infile=infile,
                                  epsg=ctx.obj['epsg'])

    fname = os.path.basename(infile).split('.')[0]

    click.echo(click.style('Loading DEM', fg='cyan'))
    click.echo(click.style('GRASS layer: {}'.format(fname), fg='cyan'))
    g.run_command('r.in.gdal', input=infile,
                  output=fname, overwrite=True)

    # takes long to fill sinks if there are many and does not fill completely
    """click.echo(click.style('Identifying sinks', fg='cyan'))
    i = 0
    while i < passes:
        if i == 0:
            indem = fname
        else:
            indem = 'fill_pass_{}'.format(i-1)
        if i < passes - 1:
            outdem = 'fill_pass_{}'.format(i)
        else:
            outdem = 'filled_dem'
        click.echo(click.style('Executing fill pass {}'.format(i), fg='cyan'))
        g.run_command('r.fill.dir', overwrite=True,
                      input=indem,
                      output=outdem,
                      direction='dir')
        i += 1
      """

    # takes long to fill sinks if there are many and does not fill completely
    click.echo(click.style('Identifying sinks', fg='cyan'))
    for i in range(passes):
        if i == 0:
            indem = fname
        else:
            indem = 'fill_pass_{}'.format(i-1)
        outdem = 'fill_pass_{}'.format(i)

        click.echo(click.style('Executing fill pass {}'.format(i), fg='cyan'))
        g.run_command('r.fill.dir', overwrite=True,
                      input=indem,
                      output=outdem,
                      direction='dir')

    # calculate the difference between filled and unfilled elevation rasters
    expr = '$diff = $indem1 - $indem2'
    g.mapcalc(expr, overwrite=True,
              diff='diff',
              indem1=outdem,
              indem2=fname)

    expr = '$sinks = if($diff > 0.0, 1, null() )'
    g.mapcalc(expr, overwrite=True,
              sinks='sinks',
              diff='diff')

    g.run_command('r.clump', overwrite=True,
                  input='sinks',
                  output='sink_clump',
                  flags='d')

    # assign the max depth to each clump; sink_max carries the depth value
    g.run_command('r.stats.zonal', overwrite=True,
                  base='sink_clump',
                  cover='diff',
                  method='max',
                  output='sink_max')

    # ignore sinks that are not very deep; sink_target carries the clump value
    expr = '$sink_target = if($sink_max > {0}, $sink_clump, null() )'.format(min_depth)
    g.mapcalc(expr, overwrite=True,
              sink_target='sink_target',
              sink_clump='sink_clump',
              sink_max='sink_max')

    # very deep sinks are most likely quarries to mask
    expr = '$sink_mask = if($sink_max > {0}, $sink_clump, null() )'.format(mask_depth)
    g.mapcalc(expr, overwrite=True,
              sink_mask='sink_mask',
              sink_clump='sink_clump',
              sink_max='sink_max')

    """
    RUN EXPORTS
    """
    click.echo(click.style('Converting to vector', fg='green'))
    g.run_command('r.to.vect',
                  input='sink_target',
                  output='sinks_vec',
                  type='area')

    g.run_command('r.to.vect',
                  input='sink_mask',
                  output='sinks_mask_vec',
                  type='area')

    click.echo(click.style('Exporting', fg='green'))
    g.run_command('v.out.ogr', overwrite=True,
                  input='sinks_vec',
                  output=os.path.join(dst, 'sinks.shp'),
                  format='ESRI_Shapefile',
                  type='area')

    g.run_command('v.out.ogr', overwrite=True,
                  input='sinks_mask_vec',
                  output=os.path.join(dst, 'sinks_mask.shp'),
                  format='ESRI_Shapefile',
                  type='area')

    """
    g.run_command('r.out.gdal', overwrite=True,
                  input='sink_target', type='Float64',
                  output=os.path.join(dst, 'sink_target.tif'),
                  format='GTiff', createopt='TFW=YES,COMPRESS=LZW')

    g.run_command('r.out.gdal', overwrite=True,
                  input='sink_mask', type='Float64',
                  output=os.path.join(dst, 'sink_mask.tif'),
                  format='GTiff', createopt='TFW=YES,COMPRESS=LZW')
    """

    elapsed = time_diff(t0, clock())
    click.echo(click.style('Finished in:', fg='green'))
    click.echo(click.style(elapsed, fg='green'))
