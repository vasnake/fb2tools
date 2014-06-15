fb2tools
========

Python scripts for prepare FB2 files easily

This Python package make use of fb2desc.py by [Con Radchenko] and contains some useful functions.
In the beginning it was [Prelude].

Function

    fb2tools.zipname.zipToFullname
    or console command
    python -u -m fb2tools namezip --workdir /path/to/write/zip --scandir /path/where/search/fb2

Search for all ``*.fb2`` files in ``scandir`` folder recursively and for each file:
- extract Author name and Book name;
- pack book to ``workdir/Authorname - Bookname.fb2.zip`` file.

Function

    fb2tools.zipname.booksNameStays
    or console command
    python -u -m fb2tools stripauthor --workdir /path/where/search/zip

Search for all ``*.zip`` files in ``workdir`` folder recursively and for each file:
- rename file from ``Authorname - Bookname.fb2.zip`` to ``Bookname.fb2.zip``;
- remove non alphabetic symbols from filename.

Usage
-----

Install package using setuptools and virtualenv

    python setup.py develop
    or
    pip install git+git://github.com/vasnake/fb2tools.git@master
    or
    pip install /path/to/sdist/distribution/fb2tools-0.0.1.zip

Call a function

    python -u -m fb2tools namezip --workdir /path/to/write/zip --scandir /path/where/search/fb2
    python -u -m fb2tools stripauthor --workdir /path/where/search/zip

[Prelude]:http://vasnake.blogspot.ru/2011/04/blog-post_18.html
[Con Radchenko]:http://pybookreader.narod.ru/misc.html
