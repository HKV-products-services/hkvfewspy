#!/usr/bin/env python

# from distutils.core import setup
from setuptools import setup, find_packages

setup(name='hkvfewspy',
      version='0.5.0',
      description='HKV tools voor operationeel waterbeheer',
      author='Mattijn van Hoek',
      author_email='mattijn.vanhoek@hkv.nl',
      packages=find_packages(),
      install_requires=[
          'zeep >=3.0.0',
          'pytz',
          'numpy',
          'pandas',
          'geopandas',
          'fire',
          'shapely',
          'requests'
      ],
      dependency_links=[
          'http://www.lfd.uci.edu/~gohlke/pythonlibs/#fiona',
          'http://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal',
          'http://geopandas.org/install.html'
      ]
      )
