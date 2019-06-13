#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='tap-liveperson',
      version='0.0.2',
      description='Singer.io tap for extracting data from the LivePerson API',
      author='Fishtown Analytics',
      url='http://fishtownanalytics.com',
      classifiers=['Programming Language :: Python :: 3 :: Only'],
      py_modules=['tap_liveperson'],
      install_requires=[
          'tap-framework==0.0.4',
      ],
      entry_points='''
          [console_scripts]
          tap-liveperson=tap_liveperson:main
      ''',
      packages=find_packages(),
      package_data={
          'tap_liveperson': [
              'schemas/*.json'
          ]
      })
