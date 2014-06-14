fb2tools
========

Python scripts for prepare FB2 files easily

Пакет Python собранный из fb2desc.py by Con Radchenko
и нескольких дополнительных фунций.

``fb2tools.zipname.zipToFullname`` решает следующую задачу:
найти в папке все книги ``*.fb2``;
выяснить имя автора и название книги из содержимого файла;
запаковать каждую книгу в zip-файл с именем, составленными из автора и названия книги.

``fb2tools.zipname.booksNameStays`` это решение другой задачи:
после того как книги разложены по каталогам - именам авторов,
можно удалить из имен файлов слеши и двоеточия (``\/:``) и имена авторов
(до разделителя " - ").

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
