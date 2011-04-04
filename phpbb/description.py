# -*- Mode: python; Coding: utf-8 -*-

DESC_SHORT = """PHPBB is a high-powered, fully scalable, and highly
customizable open-source bulletin board package. It has a
user-friendly interface, simple and straightforward administration
panel. It is the ideal, free community solution for all sites.
"""

DESC_LONG = """<p>phpBB is one of the oldest, and without any possible
doubts, the most used forum software around the world. This is so true
that many users think that phpBB is the official definition of a forum
community on Internet. phpBB 2 is massively used around the world, and
phpBB 3 is an improvement in every possible way. It works with PHP and
your choice of MySQL, MS SQL, PostgreSQL, or Access/ODBC database
servers.</p>

<p>Posts in phpBB 3 are really well managed. The posting form is
really complete and well designed. You will only see the most used
features (smileys, formatting buttons,...) on the main part of the
screen, while optional features are more hidden in sub-tabs (polls,
attachments,...). It's really difficult to find a better designed form
in the forum software world.</p>

<p>Users management and additional features are a very good points of
phpBB 3. You can configure really precisely who sees what and what can
be modified by who.</p>

<p>In short: if you are looking for a solution to create an online
community, this open-source bulletin board package is for you. Give it
a try. You won't regret it.</p>
"""

software = {
 'id':          'phpbb',
 'name':        'phpBB',
 'version':     '3.0.7-PL1',
 'author':      'phpBB Community',
 'URL':         'http://www.phpbb.com/',
 'icon_small':  'phpbb_x96.png',
 'icon_big':    'phpbb_x144.png',
 'screenshots': ('shots_434.png', 'shots_436.png', 'shots_437.png', 'shots_438.png'),
 'desc_short':  DESC_SHORT,
 'desc_long':   DESC_LONG,
 'category':    'Web Applications',
 'score':       5,
}

installation = {
  'modes': ('vserver',),
  'OS':    ('linux', 'macosx'),
  'DB':    ('mysql', 'postgresql')
}

maintainer = {
 'name':  None,
 'email': None
}
