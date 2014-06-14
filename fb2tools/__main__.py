#!/usr/bin/env python
# -*- mode: python; coding: utf-8 -*-

# Copyright (c) Valentin Fedulov <vasnake@gmail.com>
# See COPYING for details.

''' fb2tools main module
for using from console type commands like:
    python -m fb2tools namezip --workdir /path/to/write/zip --scandir /path/where/search/fb2
    python -m fb2tools stripauthor --workdir /path/where/search/zip

Tested for Linux only. UTF-8 file names.

Command line opts helpers:
    https://bitbucket.org/mchaput/baker/wiki/Home
    https://github.com/docopt/docopt
    https://pythonhosted.org/pyCLI/
'''

import os
import baker

@baker.command
def namezip(workdir='', scandir=''):
    '''Search *.fb2 files inside scandir, extract Author and Book Name from it, pack each fb2 file
    to workdir/Author - Book Name.zip

    :param workdir: /path/to/write/zip
    :param scandir: /path/where/search/fb2
    '''
    if workdir == '':
        print 'set workdir to current dir'
        workdir = os.getcwd()
    if scandir == '':
        print 'set scandir to current dir'
        scandir = os.getcwd()
    print "workdir is '{workdir}', scandir is '{scandir}'".format(workdir=workdir, scandir=scandir)

    from fb2tools.zipname import zipToFullname
    zipToFullname(workdir, scandir)


@baker.command
def stripauthor(workdir=''):
    '''Search *.zip files inside workdir, rename them stripping Author part

    :param workdir: /path/where/search/zip
    '''
    if workdir == '':
        print 'set workdir to current dir'
        workdir = os.getcwd()
    print "workdir is '{workdir}'".format(workdir=workdir)

    from fb2tools.zipname import booksNameStays
    booksNameStays(workdir)


baker.run()
