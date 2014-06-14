#!/usr/bin/env python
# -*- mode: python; coding: utf-8 -*-
# Copyright (c) Valentin Fedulov <vasnake@gmail.com>
# See COPYING for details.

from setuptools import setup

with open('README.md', 'r') as infile:
    long_description = infile.read()

setup(
    name = 'fb2tools',
    description = "fb2 files processing tools",
    long_description = long_description,
    keywords = "fb2 files tools",
    url = 'https://github.com/vasnake/fb2tools',
    download_url = 'https://github.com/vasnake/fb2tools/archive/master.zip',
    version = "0.0.1",
    license = 'GPLv3',
    author = "Valentin Fedulov",
    author_email='vasnake@gmail.com',
    packages = ['fb2tools'],
    scripts = [],
    install_requires = ['trans', 'baker'],
    classifiers = [ # https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Operating System :: OS Independent',
        'Environment :: Console',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'License :: Freeware',
        'Topic :: Utilities',
        'Topic :: Text Processing :: Markup :: XML',
        'Natural Language :: Russian'
    ],
    zip_safe = False
)
