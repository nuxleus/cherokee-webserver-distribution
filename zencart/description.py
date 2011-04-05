# -*- Mode: python; Coding: utf-8 -*-

DESC_SHORT = """<p>Zen Cart is an online software designed solely for
e-commerce businesses. It is an open source project that was developed
by a community of shop owners, programmers, designers, and consultants
who just wanted a simple e-commerce solution.</p>
"""

DESC_LONG = """<p>The code is based on the popular osCommerce shopping
cart. The goal of the Zen Cart project is essentially to make an
easier to use version of osCommerce which can be installed more
quickly, modified more easily and have a more usable configuration out
of the box</p>
"""

software = {
 'id':          'zencart',
 'name':        'Zen Cart',
 'version':     '1.3.9',
 'author':      'Zen Cart Team',
 'URL':         'http://www.zen-cart.com/',
 'icon_small':  'zencart_x96.png',
 'icon_big':    'zencart_x144.png',
 'screenshots': ('shots_399.png', 'shots_400.png', 'shots_401.png', 'shots_402.png',),
 'desc_short':  DESC_SHORT,
 'desc_long':   DESC_LONG,
 'category':    'Business',
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
