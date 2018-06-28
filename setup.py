#!/usr/bin/env python

#from distutils.core import setup
from setuptools import setup, find_packages
setup(name='hkvfewspy',
      version='0.3.1',
      description='HKV tools voor operationeel waterbeheer',
      author='Mattijn van Hoek',
      author_email='mattijn.vanhoek@hkv.nl',
      packages=find_packages(),
      install_requires=[
          'zeep',
          'pytz',
          'numpy',
          'pandas'
      ],
      dependency_links=[
        'http://www.lfd.uci.edu/~gohlke/pythonlibs/#fiona',
        'http://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal',
        'http://geopandas.org/install.html'
        ]
     )