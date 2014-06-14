#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
# (c) Valik mailto:vasnake@gmail.com

'''
zipToFullname это решение следующей задачи:
найти в папке все книги (*.fb2); выяснить имя автора и название книги из содержимого файла;
запаковать каждую книгу в zip-файл с именем, составленными из автора и названия книги.

Задача решается используя fb2desc (http://pybookreader.narod.ru/fb2desc.tgz http://pybookreader.narod.ru/misc.html)
для получения имени автора книги и названия книги.

booksNameStays это решение другой задачи:
после того как книги разложены по каталогам - именам авторов,
можно удалить из имен файлов слеши и двоеточия (\/:) и имена авторов
(до разделителя " - ").

Предполагается, что имена файлов приходят в скрипт в UTF-8
что не позволит скрипту работать в MS Windows.
'''

import sys, os
import zipfile
import subprocess
import trans
import random, string


def randomword(length):
    return ''.join(random.choice(string.lowercase) for i in range(length))


def normalize(fn, translit=False):
    ''' Убрать лишнее из строки, представляющей собой имя файла
    '''
    if translit: res = fn.decode('utf8').encode('trans').strip()
    else: res = fn

    res = res.decode('utf8')
    if not translit:
        #~ print 'before [%s]' % res.encode('utf8')
        res = res.replace(u'fb2', u''
            ).replace(u'Либрусек', u''
            ).replace(u' (The International Bestseller 2901)', u''
            ).replace(u' (Отцы-основатели. Весь Саймак', u''
            ).replace(u': Фантастические романы', u''
            ).replace(u': Фантастические рассказы', u'')
        #~ print 'after [%s]' % res.encode('utf8')

    res = res.encode('cp1251')
    res = res.translate(None, u'*"\'?«!»|\\/:'.encode('cp1251'))
    #~ res = res.translate(None, '*"\'?«!»()|\\/:'.decode('utf8').encode('cp1251'))
    res = res.strip()
    if len(res) > 128:
        parts = res.split(' - ', 1)
        auth = parts[0][:40]
        bname = parts[1][:80]
        res = ' - '.join([auth, bname])
    return res.decode('cp1251').encode('utf8')


def zipToFullname(workdir, scandir):
    '''Решение задачи:
    найти в папке все книги (*.fb2); выяснить имя автора и название книги из содержимого файла;
    запаковать каждую книгу в zip-файл с именем, составленными из автора и названия книги.

    Задача решается используя fb2desc (http://pybookreader.narod.ru/fb2desc.tgz http://pybookreader.narod.ru/misc.html)
    для получения имени автора книги и названия книги.
    '''
    fb2desc = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fb2desc.py')
    os.chdir(workdir)

    lstFiles = []
    for root, dirs, files in os.walk(scandir):
        for f in files:
            fn = os.path.join(root, f)
            if fn.endswith('.fb2'):
                lstFiles.append(fn)
            else: print 'not FB2: [%s]' % fn

    for f in sorted(lstFiles):
        print f
        res = subprocess.Popen(['python', fb2desc, '-l', r'%s' % f], stdout=subprocess.PIPE).communicate()[0]
        res = normalize(res)
        print '    [%s]' % res
        zipfn = '%s.fb2.zip' % res
        if os.path.isfile(zipfn):
            print '    already exists: [%s]' % zipfn
            zipfn = '%s.%s.fb2.zip' % (res, randomword(3))
            print '    new name: [%s]' % zipfn

        zf = zipfile.ZipFile(zipfn, 'w', zipfile.ZIP_DEFLATED)
        zf.write(f, normalize(os.path.basename(f), True))
        zf.close()
        del zf


def booksNameStays(workdir):
    '''После того как книги разложены по каталогам - именам авторов,
    можно удалить из имен файлов слеши и двоеточия (\/:) и имена авторов
    (до разделителя " - ")
    '''
    lstFiles = []
    for root, dirs, files in os.walk(workdir):
        for f in files:
            fn = os.path.join(root, f)
            if fn.endswith('.zip'):
                lstFiles.append(fn)
            else: print 'not zip: [%s]' % fn

    for f in sorted(lstFiles):
        print f
        bn = os.path.basename(f)
        bn = bn.decode('utf8').encode('cp1251').translate(None, u'\\/:'.encode('cp1251'))
        bn = bn.decode('cp1251').encode('utf8')
        parts = bn.split(' - ', 1)
        if len (parts) > 1:
            bn = parts[1].replace(' - ', '-')
        fn = os.path.join(os.path.dirname(f), bn)
        print '    %s' % fn
        if os.path.isfile(fn):
            print '    already exists: [%s]' % fn
        else: os.rename(f, fn)
