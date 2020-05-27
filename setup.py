from os import path
from setuptools import setup, find_packages


# Parse the version from the shapely module
for line in open('wsi_grasstools/__init__.py', 'r'):
    if line.find("__version__") >= 0:
        version = line.split("=")[1].strip()
        version = version.strip('"')
        version = version.strip("'")
        continue

with open('VERSION.txt', 'w') as fp:
    fp.write(version)

current_directory = path.abspath(path.dirname(__file__))
with open(path.join(current_directory, 'README.rst'), 'r') as f:
    long_description = f.read()


setup(name='wsi-grasstools',
      version=version,
      author='Michael Rahnis',
      author_email='mike@topomatrix.com',
      description='GRASS GIS scripts, with Click CLI, for hydologic flowline mapping.',
      long_description=long_description,
      long_description_content_type='text/x-rst',
      url='http://github.com/mrahnis/wsi-grasstools',
      license='BSD',
      packages=find_packages(exclude=['examples']),
      include_package_data=True,
      install_requires=[
          'click',
          'click-plugins'
      ],
      entry_points='''
          [console_scripts]
          grasstool=wsi_grasstools.cli.grasstool:cli

          [wsi_grasstools.subcommands]
          hydrolines=wsi_grasstools.cli.hydrolines:hydrolines
          paths=wsi_grasstools.cli.paths:paths
          sinks=wsi_grasstools.cli.sinks:sinks
      ''',
      keywords='gis, hydrology, mapping',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Topic :: Scientific/Engineering :: GIS'
      ])
