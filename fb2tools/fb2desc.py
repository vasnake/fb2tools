#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
# (c) Con Radchenko mailto:lankier@gmail.com
#
# $Id: fb2desc.py,v 1.10 2008/09/15 04:18:45 con Exp con $
#

import sys, os
import locale
import getopt
import codecs
import zipfile
from cStringIO import StringIO
import xml.sax
import shutil
import traceback


def get_filename(authors_list, sequence_name, sequence_number, title):
    '''Форматы:
    1 - "полные имена авторов, разделенные запятой - название (серия #номер)"
    2 - тоже, но преобразованное в транслит и с заменой пробелов
    3 - "фамилии авторов, разделенные запятой - название"
    4 - тоже, но преобразованное в транслит и с заменой пробелов
    5 - "первая буква автора в нижнем регистре/авторы, разделенные запятой, в нижнем регистре/авторы, разделенные запятой - название (серия #номер)"
    6 - тоже, но преобразованное в транслит и с заменой пробелов

    '''
    format = options['fn-format']
    out = []

    authors = []
    full_authors = []
    for a in authors_list:
        if a[0]:
            authors.append(a[0])
        fa = ' '.join(i for i in a if i)
        if fa:
            full_authors.append(fa)
    authors = ', '.join(authors)
    if not authors:
        authors = 'unknown'
    full_authors = ', '.join(full_authors)
    if not full_authors:
        full_authors = 'unknown'
    if not title:
        title = 'unknown'

    seq = ''
    if sequence_name:
        if sequence_number:
            seq = '(%s #%s)' % (sequence_name, sequence_number)
        else:
            seq = '(%s)' % sequence_name

    if format == 3:
        out.append(authors)
        out.append('-')
        out.append(title)
        out = ' '.join(out)
    else:
        out.append(full_authors)
        out.append('-')
        out.append(title)
        if seq:
            out.append(seq)
        out = ' '.join(out)

    if format in (2, 4, 6):
        out = translit(out)
        full_authors = translit(full_authors)

    #out = out.replace('/', '%').replace('\0', '').replace('?', '')
    for c in '|\\?*<":>+[]/':           # invalid chars in VFAT
        out = out.replace(c, '')
        if format in (4, 5):
            full_authors = full_authors.replace(c, '')

    fn_max = 240
    if format in (5, 6):
        fl = full_authors[0]
        if not fl.isalpha():
            fl = full_authors[1] # FIXME
        out = os.path.join(
            fl.lower().encode(options['charset']),
            full_authors.lower().encode(options['charset'])[:fn_max],
            out.encode(options['charset'])[:fn_max])
    else:
        out = out.encode(options['charset'])[:fn_max]

    return out

##----------------------------------------------------------------------

options = {
    'format'       : '',
    'charset'      : 'utf-8',
    'zip-charset'  : 'cp866',
    'elements'     : [],
    'replace'      : False,
    'rename'       : False,
    'slink'        : False,
    'copy'         : False,
    'fn-format'    : 2,
    'show-cover'   : False,
    'show-content' : False,
    'show-tree'    : False,
    'image-viewer' : 'xv',
    'quiet'        : False,
    'dest-dir'     : None,
    #
    'suffix'       : None,
    }

##----------------------------------------------------------------------

class StopParsing(Exception):
    pass

##----------------------------------------------------------------------

# u'\u2013' -> '--'
# u'\u2014' -> '---'
# u'\xa0'   -> неразрывный пробел
# u'\u2026' -> dots...
# u'\xab'   -> '<<'
# u'\xbb'   -> '>>'
# u'\u201c' -> ``
# u'\u201d' -> ''
# u'\u201e' -> ,,
def replace_chars(s):
    return (s
            .replace(u'\u2013', u'--')
            .replace(u'\u2014', u'---')
            .replace(u'\xa0'  , u' ')
            .replace(u'\u2026', u'...')
            .replace(u'\xab'  , u'<<')
            .replace(u'\xbb'  , u'>>')
            .replace(u'\u201c', u'``')
            .replace(u'\u201d', u'\'\'')
            .replace(u'\u201e', u',,')
            )

def translit(s):
    trans_tbl = {
        u'\u0430': 'a', #а
        u'\u0431': 'b', #б
        u'\u0432': 'v', #в
        u'\u0433': 'g', #г
        u'\u0434': 'd', #д
        u'\u0435': 'e', #е
        u'\u0451': 'yo', #ё
        u'\u0436': 'zh', #ж
        u'\u0437': 'z', #з
        u'\u0438': 'i', #и
        u'\u0439': 'y', #й
        u'\u043a': 'k', #к
        u'\u043b': 'l', #л
        u'\u043c': 'm', #м
        u'\u043d': 'n', #н
        u'\u043e': 'o', #о
        u'\u043f': 'p', #п
        u'\u0440': 'r', #р
        u'\u0441': 's', #с
        u'\u0442': 't', #т
        u'\u0443': 'u', #у
        u'\u0444': 'f', #ф
        u'\u0445': 'h', #х
        u'\u0446': 'c', #ц
        u'\u0447': 'ch', #ч
        u'\u0448': 'sh', #ш
        u'\u0449': 'sh', #щ
        u'\u044a': '', #ъ
        u'\u044b': 'y', #ы
        u'\u044c': '', #ь
        u'\u044d': 'e', #э
        u'\u044e': 'ju', #ю
        u'\u044f': 'ya', #я
    }
    alnum = 'abcdefghijklmnopqrstuvwxyz0123456789'
    out = []
    out_s = ''
    for i in s.lower():
        if i.isalnum():
            if i in trans_tbl:
                out_s += trans_tbl[i]
            elif i in alnum:
                out_s += i
        else:
            if out_s: out.append(out_s)
            out_s = ''
    if out_s: out.append(out_s)
    return '_'.join(out)

def wrap_line(s):
    if len(s) <= 70:
        return u'  '+s
    ss = u' '
    sl = []
    for word in s.split():
        if len(ss+word) > 72:
            sl.append(ss)
            ss = word
        elif ss:
            ss += u' ' + word
        else:
            ss = word
    sl.append(ss)
    return '\n'.join(sl)

##----------------------------------------------------------------------

def show_cover(filename, data, content_type):
    if not data:
        print >> sys.stderr, '%s: sorry, cover not found' % filename
        return
    import base64, tempfile
    data = base64.decodestring(data)
    if content_type and content_type.startswith('image/'):
        suffix = '.'+content_type[6:]
    else:
        suffix = ''
    tmp_id, tmp_file = tempfile.mkstemp(suffix)
    try:
        open(tmp_file, 'w').write(data)
        os.system(options['image-viewer']+' '+tmp_file)
    finally:
        os.close(tmp_id)
        os.remove(tmp_file)

def show_content(filename, titles):
    for secttion_level, data in titles:
        if options['replace']: data = replace_chars(data)
        print '  '*secttion_level+data.encode(options['charset'], 'replace')
    print

def rename(filename, zipfilename, desc, data):
    to = pretty_format(filename, zipfilename, len(data), desc, 'filename')
    ##filename = os.path.abspath(filename)
    to += options['suffix']
    if options['dest-dir']:
        to = os.path.join(options['dest-dir'], to)
    to = os.path.abspath(to)
    if os.path.exists(to):
        print >> sys.stderr, 'file %s already exists' % to
        return
    dir_name = os.path.dirname(to)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    if options['slink']:
        os.symlink(filename, to)
        return
    elif options['copy']:
        shutil.copy(filename, to)
        return
    os.rename(filename, to)

def pretty_format(filename, zipfilename, filesize, desc, format='pretty'):
    ann = []
    title = ''
    authors_list = []
    # [last-name, first-name, middle-name, nick-name]
    author_name = [None, None, None, None]
    genres = []
    sequence_name = ''
    sequence_number = ''
    for elem, data in desc:
##         data = data.strip()
##         if not data:
##             continue
        if elem.startswith('/description/title-info/annotation/'):
            if not elem.endswith('href'):
                ann.append(data) #wrap_line(data))
            if elem.endswith('/p'):
                ann.append('\n')
        elif elem == '/description/title-info/book-title':
            title = data
        elif elem == '/description/title-info/author/first-name':
            author_name[1] = data
        elif elem == '/description/title-info/author/middle-name':
            author_name[2] = data
        elif elem == '/description/title-info/author/last-name':
            author_name[0] = data
            authors_list.append(author_name)
            author_name = [None, None, None, None]
        elif elem == '/description/title-info/author/nick-name':
            #author_name[3] = data
            if not author_name[0]:
                author_name[0] = data
            else:
                author_name[3] = data
            authors_list.append(author_name)
            author_name = [None, None, None, None]
        elif elem == '/description/title-info/genre':
            genres.append(data)
        elif elem == '/description/title-info/sequence/name':
            sequence_name = data
        elif elem == '/description/title-info/sequence/number':
            sequence_number = data

    ##authors_list.sort()
    authors = u', '.join(' '.join(n for n in a if n) for a in authors_list if a)

    annotation = []
    ann = ''.join(ann).split('\n')
    for s in ann:
        annotation.append(wrap_line(s))
    annotation = '\n'.join(annotation)

    if format == 'single':
        if sequence_name and sequence_number:
            out = u'%s - %s (%s %s)' % (authors, title,
                                        sequence_name, sequence_number)
        elif sequence_name:
            out = u'%s - %s (%s)' % (authors, title, sequence_name)
        else:
            out = u'%s - %s' % (authors, title)
        #out = '%s: %s' % (filename, out)
        if options['replace']: out = replace_chars(out)
        return out.encode(options['charset'], 'replace')

    elif format == 'pretty':
        out = u'''\
File         : %s
''' % filename
        if zipfilename:
            out += u'''\
Zip Filename : %s
''' % zipfilename
        out += u'''\
Size         : %d kb
''' % int(filesize/1024)

        out += u'''\
Author(s)    : %s
Title        : %s
Genres       : %s
''' % (authors, title, u', '.join(genres))
        if sequence_name:
            if sequence_number:
                sequence = u'%s (%s)' % (sequence_name, sequence_number)
            else:
                sequence = sequence_name
            out += u'''\
Sequence     : %s
''' % sequence
        if annotation:
            out += u'''\
Annotation   :
%s
''' % annotation
        if options['replace']: out = replace_chars(out)
        return out.encode(options['charset'], 'replace')

    elif format == 'filename':
        return get_filename(authors_list, sequence_name, sequence_number, title)


def raw_format(filename, zipfilename, desc):
    if options['quiet']:
        out = u''
    else:
        out = u'filename: %s\n' % filename
        if zipfilename:
            out += u'zipfilename: %s\n' % zipfilename
    for elem, data in desc:
        if not data:
            continue
        t = filter(elem.startswith, options['elements'])
        #t = [x for x in options['elements'] if elem.startswith(x)]
        if options['elements'] == [] or t:
            out += u'%s: %s\n' % (elem, data)
    if options['replace']: out = replace_chars(out)
    return out.encode(options['charset'], 'replace')

##----------------------------------------------------------------------

class ContentHandler(xml.sax.handler.ContentHandler):
    def __init__(self):
        self.elem_stack = []
        self.is_desc = False
        self.is_cover = False
        self.cur_data = ''
        self.desc = []
        self.cover = ''
        self.cover_name = ''
        self.cover_content_type = ''
        self.is_title = False
        self.cur_title = []
        self.titles = []
        self.section_level = 0
        self.tree = []

    def startElement(self, name, attrs):
        if name == 'description': self.is_desc = True
        if name == 'section': self.section_level += 1

        if self.is_desc or options['show-tree']:
            self.elem_stack.append(name)
            elem = '/'+'/'.join(self.elem_stack)
            if options['show-tree']:
                if self.tree and self.tree[-1][0] == elem:
                    #print self.tree[-1]
                    self.tree[-1][1] += 1
                else:
                #if not elem.endswith('/p') and not elem.endswith('/v'):
                    self.tree.append([elem, 1])
            for atr in attrs.getNames():
                #t = (elem+u'/'+atr, attrs.getValue(atr))
                self.desc.append((elem+u'/'+atr, attrs.getValue(atr)))
                if elem == '/description/title-info/coverpage/image' and \
                   atr.endswith('href'):
                    self.cover_name = attrs.getValue(atr)[1:]


        self.is_cover = False
        if options['show-cover'] and name == 'binary':
            content_type = ''
            for atr in attrs.getNames():
                if atr == 'id' and attrs.getValue(atr) == self.cover_name:
                    self.is_cover = True
                elif atr == 'content-type':
                    content_type = attrs.getValue(atr)
            if self.is_cover and content_type:
                self.cover_content_type = content_type

        if options['show-content'] and name == 'title':
            self.is_title = True
            self.cur_title = []


    def endElement(self, name):
        if self.is_desc and self.cur_data:
            elem_name = '/'+'/'.join(self.elem_stack)
            self.desc.append((elem_name, self.cur_data.strip()))
            self.cur_data = ''

        if self.is_desc or options['show-tree']:
            del self.elem_stack[-1]

        if name == 'description':
            if not options['show-cover'] \
                   and not options['show-content'] \
                   and not options['show-tree']:
                raise StopParsing
            else:
                self.is_desc = False

        if options['show-content'] and name == 'title':
            self.is_title = False
            self.titles.append((self.section_level, ' '.join(self.cur_title)))

        self.cur_data = ''
        if name == 'section': self.section_level -= 1

    def characters(self, data):
        if self.is_desc:
            #data = data.strip()
            data = data.replace('\n', ' ')
            if self.cur_data:
                self.cur_data += data
            else:
                self.cur_data = data
        if options['show-cover'] and self.is_cover:
            self.cover += data
        if options['show-content'] and self.is_title:
            data = data.strip()
            if data: self.cur_title.append(data)

class ErrorHandler(xml.sax.handler.ErrorHandler): pass
class EntityResolver(xml.sax.handler.EntityResolver): pass
class DTDHandler(xml.sax.handler.DTDHandler): pass

##----------------------------------------------------------------------

def fb2parse(filename, zipfilename, data):

    if not data.startswith('<?xml') and not data.startswith('\xef\xbb\xbf<?xml'):
        print >> sys.stderr, \
              'Warning: file %s is not an XML file. Skipped.' % filename
        print repr(data[:5])
        #shutil.copy(filename, '/home/con/t/')
        return

    chandler = ContentHandler()
    input_source = xml.sax.InputSource()
    input_source.setByteStream(StringIO(data))
    xml_reader = xml.sax.make_parser()
    xml_reader.setContentHandler(chandler)
    xml_reader.setErrorHandler(ErrorHandler())
    xml_reader.setEntityResolver(EntityResolver())
    xml_reader.setDTDHandler(DTDHandler())
    try:
        xml_reader.parse(input_source)
    except StopParsing:
        pass
    if options['rename']:
        rename(filename, zipfilename, chandler.desc, data)
        return
    if options['show-tree']:
        for e, n in chandler.tree:
            if n > 1:
                print '%s [%d]' % (e, n)
            else:
                print e
        return

    if options['format'] == 'pretty':
        print pretty_format(filename, zipfilename, len(data), chandler.desc, 'pretty')
    elif options['format'] == 'filename':
        print pretty_format(filename, zipfilename, len(data), chandler.desc, 'filename')
    elif options['format'] == 'single':
        print pretty_format(filename, zipfilename, len(data), chandler.desc, 'single')
    elif options['format'] == '' \
             and not options['show-cover'] \
             and not options['show-content']:
        print raw_format(filename, zipfilename, chandler.desc)
    if options['show-cover'] or options['show-content']:
        if options['format'] == 'raw':
            print raw_format(filename, zipfilename, chandler.desc)
        if options['show-content']:
            show_content(filename, chandler.titles)
        if options['show-cover']:
            show_cover(filename, chandler.cover, chandler.cover_content_type)

##----------------------------------------------------------------------

def main():

    #locale.setlocale(locale.LC_ALL, '')
    default_charset = locale.getdefaultlocale()[1]
    if default_charset:
        options['charset'] = default_charset
    prog_name = os.path.basename(sys.argv[0])

    try:
        optlist, args = getopt.getopt(sys.argv[1:], 'c:Ce:f:hlopqrRStvwz:',
                                      ['raw', 'pretty',
                                       'single',
                                       'output=',
                                       'rename', 'copy', 'slink',
                                       'fn-format=',
                                       'cover', 'contents', 'tree',
                                       'charset=', 'zip-charset=',
                                       'elements=',
                                       'dest-dir=',
                                       'image-viewer=',
                                       'replace', 'quiet', 'help'])
    except getopt.GetoptError, err:
        sys.exit('%s: %s\ntry %s --help for more information'
                 % (prog_name, err, prog_name))

    help_msg = '''fb2desc -- show description of FB2 file(s)
Usage: %s [options] files|dir
  -w  --raw-format           output in raw format (default)
  -p  --pretty               output in pretty format
  -l  --single               output in single format
      --output format        output in format (raw, pretty, single, filename)
  -o  --contents             show contents
  -t  --tree
  -v  --cover                show cover
  -c  --charset <charset>    specify output charset (default: %s)
  -z  --zip-charset <charset>
  -r  --replace              replace any chars
  -e  --elements <elements>  show only this elements (comma separeted)
  -R  --rename               rename mode
  -S  --slink                create softlinks
  -C  --copy                 copy files
      --fn-format <format>   rename pattern (1, 2, 3, 4, 5, 6)
      --dest-dir
      --image-viewer
  -q  --quiet                suppress output filename
  -h  --help                 display this help''' \
    % (prog_name, default_charset)

    for i in optlist:
        if i[0] == '--help' or i[0] == '-h':
            print help_msg
            sys.exit()
        elif i[0] in ('--charset', '-c'):
            charset = i[1]
            try:
                codecs.lookup(charset)
            except LookupError, err:
                sys.exit('%s: %s' % (prog_name, err))
            options['charset'] = charset
        elif i[0] in ('-z', '--zip-charset'):
            charset = i[1]
            try:
                codecs.lookup(charset)
            except LookupError, err:
                sys.exit('%s: %s' % (prog_name, err))
            options['zip-charset'] = charset
        elif i[0] == '--elements' or i[0] == '-e':
            options['elements'] = i[1].split(',')
        elif i[0] == '--output':
            f = i[1]
            if f not in ('raw', 'pretty', 'single', 'filename'):
                sys.exit('''bad option for --output
must be raw, pretty, single, filename
''')
            options['format'] = f
        elif i[0] == '--raw' or i[0] == '-w':
            options['format'] = 'raw'
        elif i[0] == '--single' or i[0] == '-l':
            options['format'] = 'single'
        elif i[0] == '--pretty-format' or i[0] == '-p':
            options['format'] = 'pretty'
        elif i[0] == '--replace' or i[0] == '-r':
            options['replace'] = True
        elif i[0] == '--rename' or i[0] == '-R':
            options['rename'] = True
        elif i[0] == '--slink' or i[0] == '-S':
            options['rename'] = True
            options['slink'] = True
        elif i[0] == '--copy' or i[0] == '-C':
            options['rename'] = True
            options['copy'] = True
        elif i[0] in ('--fn-format', '-f'):
            f = i[1]
            if f not in ('1', '2', '3', '4', '5', '6'):
                sys.exit('''bad option for --fn-format
must be 1, 2, 3, 4, 5, 6
''')
            options['fn-format'] = int(f)
        elif i[0] == '--contents' or i[0] == '-o':
            options['show-content'] = True
        elif i[0] == '--cover' or i[0] == '-v':
            options['show-cover'] = True
        elif i[0] == '--tree' or i[0] == '-t':
            options['show-tree'] = True
        elif i[0] == '--quiet' or i[0] == '-q':
            options['quiet'] = True
        elif i[0] == '--dest-dir':
            options['dest-dir'] = i[1]
        elif i[0] == '--image-viewer':
            options['image-viewer'] = i[1]

    if len(args) == 0:
        sys.exit('%s: missing filename\ntry %s --help for more information'
                 % (prog_name, prog_name))

    in_files = []
    for fn in args:
        if os.path.isdir(fn):
            for root, dirs, files in os.walk(fn):
                for f in files:
                    in_files.append(os.path.join(root, f))
        else:
            in_files.append(fn)

    #print in_files
    #return

    for raw_filename in in_files:
        try:
            filename = os.path.abspath(raw_filename)
            filename = unicode(filename, options['charset'])
        except UnicodeDecodeError, err:
            #raise
            #print >> sys.stderr, 'WARNING: decode filename:', str(err)
            #continue
            filename = ''               # fixme
            pass

        if zipfile.is_zipfile(raw_filename):
            options['suffix'] = '.fb2.zip'
            zf = zipfile.ZipFile(raw_filename)
            for zip_filename in zf.namelist():
                data = zf.read(zip_filename)
                try:
                    ##zip_filename = unicode(zip_filename, options['charset'])
                    zip_filename = unicode(zip_filename, options['zip-charset'])
                except UnicodeDecodeError, err:
                    print >> sys.stderr, 'WARNING: decode zip filename:', str(err)
                    zip_filename = ''
                try:
                    fb2parse(filename, zip_filename, data)
                except:
                    traceback.print_exc()
                    ##shutil.copy(raw_filename, '/home/con/t/')
                else:
                    if options['rename']:
                        continue
        else:
            options['suffix'] = '.fb2'
            data = open(raw_filename).read()
            if data.startswith('BZh'):
                import bz2
                options['suffix'] = '.fb2.bz2'
                data = bz2.decompress(data)
            elif data.startswith('\x1f\x8b'):
                import gzip
                options['suffix'] = '.fb2.gz'
                data = gzip.GzipFile(fileobj=StringIO(data)).read()
            try:
                fb2parse(filename, '', data)
            except:
                traceback.print_exc()


if __name__ == '__main__':
    main()

