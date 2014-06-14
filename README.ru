                                      -*- mode: text; coding: utf-8; -*-

fb2desc.py - консольная утилита для работы с fb2 файлами.

Опции.
=====

  -w  --raw-format           Вывод description в "сыром" виде (по умолчанию)
  -p  --pretty               Вывод description в человекопонятном виде
  -l  --single               Однострочный вывод
      --output format        output in format (raw, pretty, single, filename)
  -o  --contents             Оглавление
  -t  --tree                 Показать xml дерево
  -v  --cover                Обложка
  -c  --charset <charset>    Кодировка вывода
  -z  --zip-charset <charset> Кодировка имен файлов в zip-архивах
  -r  --replace              Заменять некоторые символы (кавычки-ёлочки и т.д.)
  -e  --elements <elements>  Показывать только указанные <elements>
  -R  --rename               Режим переименования
  -S  --slink                Создавать softlinks вместо переименования
  -C  --copy                 Копировать вместо переименования
      --dest-dir             Каталог для переименования
      --image-viewer         Программа просмотра обложки
  -q  --quiet                Не выводить имена файлов
  -h  --help                 display this help

Примеры использования
=====================

По умолчанию:
~~~~~~~~~~~~~
$ fb2desc.py example.fb2

filename: /home/user/example.fb2
/description/title-info/genre: history_russia
/description/title-info/genre: romance_historical
/description/title-info/genre: literature_classics
/description/title-info/genre: literature_history
/description/title-info/genre: literature_war
/description/title-info/genre: literature_rus_classsic
/description/title-info/genre: computers
/description/title-info/author/first-name: Лев
/description/title-info/author/middle-name: Николаевич
/description/title-info/author/last-name: Толстой
/description/title-info/book-title: Война и мир
[...]

Показать человекопонятный description, оглавление и обложку:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
$ fb2desc.py -pov example.fb2

File         : /home/user/example.fb2
Size         : 98 kb
Author(s)    : Толстой Лев Николаевич
Title        : Война и мир
Genres       : history_russia, romance_historical, literature_classics, literature_history, literature_war, literature_rus_classsic, computers
Sequence     : Детство, Отрочество, Юность (2)
Annotation   :
  Это тестовый файл FictionBook 2.0. Создан Грибовым Дмитрием в
демонстрационных целях и для экспериментов с библиотекой FIctionBook.lib.
К сожалению сам роман я в FB2 пока не перевел.
[...]

Название стиха
ТОМ 1
  ЧАСТЬ ПЕРВАЯ
    I
    Это пример глубоко вложенных частей
      Рыба (1.I)
      Рыба (1.II)
      Рыба (1.III)
      Рыба (1.IV)
        Рыба (1.IV.a)
        Рыба (1.IV.б)
        Рыба (1.IV.в)
[...]

Показать только указанные <elements>
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
$ fb2desc.py -e /description/title-info/author/first-name,/description/title-info/author/last-name,/description/title-info/book-title,/description/title-info/genre example.fb2

filename: /home/user/example.fb2
/description/title-info/genre: history_russia
/description/title-info/genre: romance_historical
/description/title-info/genre: literature_classics
/description/title-info/genre: literature_history
/description/title-info/genre: literature_war
/description/title-info/genre: literature_rus_classsic
/description/title-info/genre: computers
/description/title-info/author/first-name: Лев
/description/title-info/author/last-name: Толстой
/description/title-info/book-title: Война и мир


Рекурсивный обход каталогов
~~~~~~~~~~~~~~~~~~~~~~~~~~~
$ fb2desc.py dir

Режим переименования
~~~~~~~~~~~~~~~~~~~~
Программа может переименовывать fb2-файлы по предопределенным шаблонам.
Команда fb2desc -R example.fb2 переименует example.fb2 в
tolstoy_lev_nikolaevich_voyna_i_mir_detstvo_otrochestvo_junost_2.fb2

Можно указать шаблон переименования:
    1 - "полные имена авторов, разделенные запятой - название (серия #номер)"
    2 - тоже, но преобразованное в транслит и с заменой пробелов
    3 - "фамилии авторов, разделенные запятой - название"
    4 - тоже, но преобразованное в транслит и с заменой пробелов
    5 - "первая буква автора в нижнем регистре/авторы, разделенные запятой, в нижнем регистре/авторы, разделенные запятой - название (серия #номер)"
    6 - тоже, но преобразованное в транслит и с заменой пробелов
По умолчанию используется #2.

Пример использования шаблонов:
$ fb2desc -R --fn-format 6 example.fb2
создаст каталог t/tolstoy_lev_nikolaevich/ и переименует файл в
t/tolstoy_lev_nikolaevich/tolstoy_lev_nikolaevich_voyna_i_mir_detstvo_otrochestvo_junost_2.fb2
Вместо переименования можно копировать файл:
$ fb2desc -C --fn-format 6 example.fb2
или создавать softlink:
$ fb2desc -S example.fb2

Если вместо имени файла указать каталог, то программа рекурсивно обойдет
каталоги и переименует все найденные файлы.

В режиме переименования можно указать целевой каталог.

Пример: обойти все каталоги в dir, найти fb2-файлы и создать символьные
ссылки на них в каталоге ~/books
$ fb2desc -S --dest-dir ~/books dir
