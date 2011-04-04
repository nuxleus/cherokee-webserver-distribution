# -*- Mode: python; Coding: utf-8 -*-

DESC_SHORT = """<p>MoinMoin is an advanced, easy to use and extensible
WikiEngine with a large community of users. Said in a few words. it is
about collaboration on easily editable web pages.</p>
"""

DESC_LONG = """<p>It is also an excellent way to rapidly collect
information in a connected, but non-linear manner.</p>

<p>MoinMoin is licensed under the GPL - living from lots of people
contributing.</p>

<ul>
<li>If you want to learn more about wiki in general, first read about WikiWikiWeb, then about WhyWikiWorks and the WikiNature.</li>
<li>If you want to play with it, please use the WikiSandBox.</li>
<li> MoinMoinFeatures documents why you really want to use MoinMoin rather than another wiki engine.</li>
<li>MoinMoinScreenShots shows how it looks like. You can also browse this wiki or visit some other MoinMoinWikis.</li>
</ul>

<p>MoinMoin is Python-based and does not rely on an external database
to work. Installing it and using it is so easy a caveman user could do
it.</p>

<p>If you know what a wiki is you don't need much more information
than this to convince you that I enjoyed using MoinMoin. Its use of
Python, its ease of installation and ease of use makes it almost a
no-brainer. </p>

<p>Give it a shot. Your ideas will thank you.</p>
"""

software = {
 'id':          'moin',
 'name':        'MoinMoin',
 'version':     '1.9.3',
 'author':      'MoinMoin Community',
 'URL':         'http://moinmo.in/',
 'icon_small':  'moin_x96.png',
 'icon_big':    'moin_x144.png',
 'screenshots': ('shots_177.png', 'shots_178.png', 'shots_179.png', 'shots_180.png', 'shots_181.png', 'shots_182.png', 'shots_183.png', 'shots_184.png', 'shots_185.png',),
 'desc_short':  DESC_SHORT,
 'desc_long':   DESC_LONG,
 'category':    'Wiki',
 'score':       5,
}

installation = {
  'modes': ('vserver'),
  'OS':    ('linux', 'macosx', 'freebsd'),
  'DB':    ()
}

maintainer = {
 'name':  None,
 'email': None
}
