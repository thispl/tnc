# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in tnc/__init__.py
from tnc import __version__ as version

setup(
	name='tnc',
	version=version,
	description='tnc customer',
	author='frappe',
	author_email='sarumathy.d@groupteampro.com',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
