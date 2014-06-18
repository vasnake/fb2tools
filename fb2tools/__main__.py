#!/usr/bin/env python
# -*- mode: python; coding: utf-8 -*-

# Copyright (c) Valentin Fedulov <vasnake@gmail.com>
# See COPYING for details.

''' fb2tools main module
for using from console type commands like:
    python -m fb2tools namezip --workdir /path/to/write/zip --scandir /path/where/search/fb2
    python -m fb2tools stripauthor --workdir /path/where/search/zip

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
    to workdir/Author - Book Name.fb2.zip

    :param workdir: /path/to/write/zip
    :param scandir: /path/where/search/fb2
    '''
    if workdir == '':
        print u'set workdir to current dir'
        workdir = os.getcwdu()
    if scandir == '':
        print u'set scandir to current dir'
        scandir = os.getcwdu()
    print u"workdir is '{workdir}', scandir is '{scandir}'".format(workdir=workdir, scandir=scandir)

    from fb2tools.zipname import zipToFullname
    zipToFullname(unicode(workdir), unicode(scandir))


@baker.command
def stripauthor(workdir=''):
    '''Search *.zip files inside workdir, rename them stripping out Author part

    :param workdir: /path/where/search/zip
    '''
    if workdir == '':
        print u'set workdir to current dir'
        workdir = os.getcwdu()
    print u"workdir is '{workdir}'".format(workdir=workdir)

    from fb2tools.zipname import booksNameStays
    booksNameStays(unicode(workdir))


baker.run()
