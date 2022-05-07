# -*- coding: utf-8 -*-
"""
Created on Wed Apr  8 11:40:48 2020

@author: Konstantinos Risvas (krisvas@ece.upatras.gr)
"""

# !/usr/bin/env python
from setuptools import setup

setup(name='febio_exporter',
      version='1.0.0',
      description='create .feb models for FEBio suite',
      author='Dimitar Stanev',
      license='GPL v3',
      packages=['febio_exporter'],
      package_data={'febio_exporter': ['__init__.py',
                                       'model.py']},
      include_package_data=True)
