#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
# (c) Valik mailto:vasnake@gmail.com

'''
zipToFullname это решение такой задачи:
найти в папке все книги (*.fb2); выяснить имя автора и название книги из содержимого файла;
запаковать каждую книгу в zip-файл с именем, составленными из автора и названия книги.

Задача решается используя fb2desc
для получения имени автора книги и названия книги.
    http://pybookreader.narod.ru/fb2desc.tgz
    http://pybookreader.narod.ru/misc.html

booksNameStays это решение другой задачи:
после того как книги разложены по каталогам - именам авторов,
можно удалить из имен файлов слеши и двоеточия (\/:) и имена авторов
(до разделителя " - ").
'''

import sys, os
import zipfile
import subprocess
import random, string
import locale
import trans

forRemove = (u'fb2',
    u'Либрусек',
    u' (The International Bestseller 2901)',
    u' (Отцы-основатели. Весь Саймак',
    u': Фантастические романы',
    u': Фантастические рассказы')

def removeBadSymbols(uStr, badSymbols=u'*"\'?«!»|\\/:'):
    '''Remove from unicode string uStr every bad symbol mentioned in badSymbols
    '''
    frm = badSymbols
    to = [None] * len(frm)
    tab = dict((ord(a), b) for a, b in zip(frm, to))

    return uStr.translate(tab)


def normalize(fn, translit=False):
    '''Returns normalized filename as unicode string.

    Normalize filename 'fn' by removing bad symbols like '*, /, \, ?' and so on.
    Also remove substrings noted in given list.
    And truncate result if it's length > 128.
    If 'translit' is True encode filename to latin alphabet using 'trans' package.

    fn is a unicode string
    '''
    if translit: res = fn.encode('trans').strip()
    else:
        res = fn.strip()
        for x in forRemove:
            res = res.replace(x, u'')

    res = removeBadSymbols(res, u'*"\'?«!»|\\/:')

    if len(res) > 128:
        parts = res.split(' - ', 1)
        auth = parts[0][:40]
        bname = parts[1][:80]
        res = u' - '.join([auth, bname])

    return res.strip()


def randomword(length):
    '''Returns random string with given length
    '''
    return ''.join(random.choice(string.lowercase) for i in range(length))


def findFiles(scandir, ext):
    '''Returns list of file names with extension 'ext'
    recursively finded inside 'scandir'

    scandir, ext is a unicode strings
    '''
    lstFiles = []
    for root, dirs, files in os.walk(scandir):
        for f in files:
            fn = os.path.join(root, f)
            if fn.endswith(u'.' + ext):
                lstFiles.append(unicode(fn))
            else: print u"extra file: '%s'" % fn
    return lstFiles


def getFb2descModPath():
    '''Returns full name/path for fb2desc.py module
    '''
    pkgdir = os.path.dirname(os.path.abspath(__file__))
    if not os.path.exists(pkgdir):
        for dirname in sys.path:
            abspath = os.path.join(dirname, __file__)
            if os.path.exists(abspath):
                pkgdir = os.path.dirname(abspath)
                break

    return os.path.join(pkgdir, 'fb2desc.py')


def u2b(us):
    return us.encode('UTF-8')

def b2u(bs):
    return bs.decode('UTF-8')


def callFb2desc(fname):
    '''Returns unicode string, book info from fb2desc.py output

    fname is a unicode string, FB2 book filename
    '''
    fb2desc = unicode(getFb2descModPath())
    uparams = [u'python', fb2desc, u'-l', fname]

    if sys.platform == "win32":
        bparams = map(u2b, uparams[:3] + [u'--charset', u'UTF-8'] + uparams[3:])
        res = subprocess.Popen(bparams, stdout=subprocess.PIPE).communicate()[0]
        #~ print res
        return b2u(res)

    # posix works OK with unicode
    res = subprocess.Popen(uparams, stdout=subprocess.PIPE).communicate()[0]
    return unicode(res, locale.getpreferredencoding())


def zipToFullname(workdir, scandir):
    '''Решение задачи:
    найти в папке scandir все книги (*.fb2); выяснить имя автора и название книги из содержимого файла;
    запаковать каждую книгу в workdir/zip-файл с именем, составленными из автора и названия книги.

    Задача решается используя fb2desc (http://pybookreader.narod.ru/fb2desc.tgz http://pybookreader.narod.ru/misc.html)
    для получения имени автора книги и названия книги.

    workdir, scandir is a unicode strings
    '''
    os.chdir(workdir)

    lstFiles = findFiles(scandir, u'fb2')
    for f in sorted(lstFiles):
        print u"Input filename: '%s'" % f
        res = callFb2desc(f)
        print u"fb2desc output: '%s'" % res
        res = normalize(res)
        print u"normalized filename '%s'" % res

        zipfn = u'%s.fb2.zip' % res
        if os.path.isfile(zipfn):
            print u"file already exists: '%s'" % zipfn
            zipfn = u'%s.%s.fb2.zip' % (res, randomword(3))
            print u"new name with random suffix: '%s'" % zipfn

        zf = zipfile.ZipFile(zipfn, 'w', zipfile.ZIP_DEFLATED)
        zf.write(f, normalize(os.path.basename(f), True))
        zf.close()
        del zf


def booksNameStays(workdir):
    '''После того как книги разложены по каталогам - именам авторов,
    можно удалить из имен файлов слеши и двоеточия (\/:) и имена авторов
    (до разделителя " - ")

    workdir is a unicode string
    '''

    lstFiles = findFiles(workdir, u'zip')
    for f in sorted(lstFiles):
        print u"Input filename: '%s'" % f
        bn = os.path.basename(f)
        bn = removeBadSymbols(bn, u'\\/:')

        parts = bn.split(' - ', 1)
        if len (parts) > 1:
            bn = parts[1].replace(' - ', '-')

        fn = os.path.join(os.path.dirname(f), bn)
        print u"output filename: '%s'" % fn
        if os.path.isfile(fn):
            print u"file exists already, do nothing: '%s'" % fn
        else:
            os.rename(f, fn)
