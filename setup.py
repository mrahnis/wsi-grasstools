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

setup(name='wsi-grasstools',
    version=version,
    author='Michael Rahnis',
    author_email='michael.rahnis@fandm.edu',
    description='GRASS GIS scripts, with Click CLI, for hydologic flowline mapping.',
    url='http://github.com/mrahnis/wsi-grasstools',
    license='BSD',
    packages=find_packages(exclude=['examples']),
    include_package_data=True,
    install_requires=[
        'click',
        'click-plugins',
        'gdal'
    ],
    entry_points='''
        [console_scripts]
        grasstool=wsi_grasstools.cli.grasstool:cli

        [wsi_grasstools.subcommands]
        sinks=wsi_grasstools.cli.sinks:sinks
        hydrolines=wsi_grasstools.cli.hydrolines:hydrolines
    ''',
    keywords='gis, hydrology, mapping',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Topic :: Scientific/Engineering :: GIS'
    ]
)
