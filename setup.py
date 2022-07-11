#
# This file is part of Python Library for Patches Creator.
# Copyright (C) 2021 INPE.
#
# Python Library for Patches Creator is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Python Library for Patches Creator."""

import os

from setuptools import find_packages, setup

readme = open('README.rst').read()

history = open('CHANGES.rst').read()

docs_require = [
    'Sphinx>=2.2',
    'sphinx_rtd_theme',
    'sphinx-copybutton',
]

tests_require = [
    'coverage>=4.5',
    'coveralls>=1.8',
    'pytest>=5.2',
    'pytest-cov>=2.8',
    'pytest-pep8>=1.0',
    'pydocstyle>=4.0',
    'isort>4.3',
    'check-manifest>=0.40',
]

examples_require = [
]

extras_require = {
    'docs': docs_require,
    'examples': examples_require,
    'tests': tests_require,
}

extras_require['all'] = [req for _, reqs in extras_require.items() for req in reqs]

setup_requires = [
    'pytest-runner>=5.2',
]

install_requires = [
    'Click>=7.0',
    'stac.py>=0.9.0.post6',
    'jsonpath-rw>=1.4',
    'jsonpath-rw-ext>=1.2.2',
    'rasterio>=1.2.9'
]

packages = find_packages()

g = {}
with open(os.path.join('patch_builder', 'version.py'), 'rt') as fp:
    exec(fp.read(), g)
    version = g['__version__']

setup(
    name='patch_builder',
    version=version,
    description=__doc__,
    long_description=readme + '\n\n' + history,
    long_description_content_type = 'text/x-rst',
    keywords=['Time series', 'Earth Observations'],
    license='MIT',
    author='Marcos Rodrigues',
    author_email='marcos.rodrigues@inpe.br',
    url='https://github.com/marcosmlr/patch-builder',
    project_urls={
        'Repository': 'https://github.com/marcosmlr/patch-builder',
        'Issues': 'https://github.com/marcosmlr/patch-builder/issues',
        'Documentation': 'https://patch_builder.readthedocs.io/en/latest/'
    },
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    entry_points={
         'console_scripts': [
            'patch-builder = patch_builder.cli:cli',
        ],
    },
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Web Environment',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: GIS',
    ],
)
