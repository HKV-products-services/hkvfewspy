#!/usr/bin/env python

# from distutils.core import setup
from setuptools import setup, find_packages

setup(
    name="hkvfewspy",
    version="1.0.2",
    description="HKV tools voor operationeel waterbeheer",
    author="Mattijn van Hoek",
    author_email="mattijn.vanhoek@hkv.nl",
    packages=find_packages(),
    install_requires=[
        "zeep >=3.0.0",
        "pytz",
        "numpy",
        "pandas",
        "fire",
        "requests",
    ],
    dependency_links=[
        "http://www.lfd.uci.edu/~gohlke/pythonlibs/#fiona",
        "http://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal",
    ],
)
