# -*- Mode: python; Coding: utf-8 -*-

DESC_SHORT = """<p>SilverStripe CMS is a content management system
used by governments, businesses, and non-profit organisations around
the world. It is a power tool for web development teams, and the first
open source web app to become Microsoft Certified.</p>"""

DESC_LONG = """<p>As a platform, SilverStripe CMS is used to build
websites, intranets, and web applications. The modern architecture of
SilverStripe CMS allows organisations to keep pace with innovation on
the web. SilverStripe CMS enables websites and applications to contain
stunning design, great content, and compelling interactive and social
functions.</p>

<p>Besides a powerful and intuitive content authoring application,
SilverStripe CMS contains a powerful PHP5-based programming framework,
Sapphire. Sapphire brings immense flexibility and ease in customising
your site and provides fundamentals such as security models, workflow,
caching, and multiple language and subsite support.</p>

<p>SilverStripe CMS is open source, underpinned by public
documentation, free code, and a developer community. It is based on
open standards and supports multiple technology platforms.</p>
"""

software = {
 'id':          'silverstripe',
 'name':        'SilverStripe',
 'version':     '2.4.5',
 'author':      'SilverStripe',
 'URL':         'http://www.silverstripe.org/',
 'icon_small':  'silverstripe_x96.png',
 'icon_big':    'silverstripe_x144.png',
 'screenshots': ('shots_439.png', 'shots_440.png', 'shots_441.png',),
 'desc_short':  DESC_SHORT,
 'desc_long':   DESC_LONG,
 'category':    'Content Management',
 'score':       5,
}

installation = {
  'modes': ('vserver', 'webdir'),
  'OS':    ('linux', 'macosx', 'freebsd'),
  'DB':    ('mysql')
}

maintainer = {
 'name':  None,
 'email': None,
}
