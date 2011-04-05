# -*- Mode: python; Coding: utf-8 -*-

DESC_SHORT = """<p>phpMyAdmin is a PHP tool intended to handle the
administration of MySQL over the Web. Currently it can create/drop
databases, modify tables and fields, and execute any SQL statement,
and manage keys on fields. This is an English-only version.</p>
"""

DESC_LONG = """<p>phpMyAdmin is one of the most popular tools written
in PHP which allows you to handle the administration of MySQL over the
Web.</p>

<p>You can use it to create and drop databases, create/drop/alter
tables, delete/edit/add fields, execute SQL, manage user privileges
and export data into various formats. Although it's a remarkably
simple SQL database, it's obviously still beyond the grasp of most
novices users, especially those that have no SQL database
experience. However, the success of phpMyAdmin has been so great that
the developers have even written a book about it!</p>

<p>If you are just starting in php however and can't handle the
complexities of the book, then the developers have also written an
easy to use tutorial aimed at programmers, designers and analysts of
dynamic websites that want to learn the basics of SQL. Of course,
before you start anything you'll need access to a MySQL server which
you can host on any major web hosting platform.</p>

<p>phpMyAdmin is one of the benchmark programs for learning about PHP
and SQL programming and it remains a popular choice with beginners and
experts alike.</p>
"""

software = {
 'id':          'phpmyadmin',
 'name':        'phpMyAdmin',
 'version':     '3.3.10',
 'author':      'phpMyAdmin Community',
 'URL':         'http://www.phpmyadmin.net/',
 'icon_small':  'phpmyadmin_x96.png',
 'icon_big':    'phpmyadmin_x144.png',
 'screenshots': ('shots_447.png', 'shots_448.png', 'shots_449.png', 'shots_450.png', 'shots_451.png',),
 'desc_short':  DESC_SHORT,
 'desc_long':   DESC_LONG,
 'category':    'Development',
 'score':       5,
}

installation = {
  'modes': ('vserver', 'webdir'),
  'OS':    ('linux', 'macosx', 'freebsd'),
  'DB':    ('mysql',)
}

maintainer = {
 'name':  None,
 'email': None,
}
