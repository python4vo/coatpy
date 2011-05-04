#!/usr/bin/env python

from distutils.core import setup

try: # Python 3.x
    from distutils.command.build_py import build_py_2to3 as build_py
except ImportError: # Python 2.x
    from distutils.command.build_py import build_py


setup(name='COATpy',
      version='0.1.0.0',
      description='Collection of Online Astronomy Tools in Python',
      author='anonymouse',
      author_email='onlineastronomy@gmail.com',
      url='',
      packages=['coatpy','coatpy.volib',
          'coatpy.volib.volib','coatpy.volib.votable',
          'coatpy.volib.xparser','coatpy.volib.utils'],
      cmdclass = {'build_py':build_py},
     )
