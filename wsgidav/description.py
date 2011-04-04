# -*- Mode: python; Coding: utf-8 -*-

DESC_SHORT = """<p>WsgiDAV is a generic WebDAV server written in
Python and based on WSGI.  WsgiDAV comes with a standalone server, to
run out of the box. And it runs with all WSGI servers, for which uWSGI
is bundled in this package.</p>
"""

DESC_LONG = """<p>Note that WsgiDAV is still in its early development
stages, but basically supports all WebDAV clients on all
platforms. Some of them might show odd behaviours as noted by the
project's website.</p>
"""

software = {
 'id':          'wsgidav',
 'name':        'WsgiDAV',
 'version':     '0.4.0b2',
 'author':      'WsgiDAV',
 'URL':         'http://wsgidav.googlecode.com/',
 'icon_small':  'wsgidav_x96.png',
 'icon_big':    'wsgidav_x144.png',
 'screenshots': (),
 'desc_short':  DESC_SHORT,
 'desc_long':   DESC_LONG,
 'category':    'Development',
 'score':       5,
}

installation = {
  'modes': ('vserver', 'webdir'),
  'OS':    ('linux', 'macosx', 'freebsd'),
  'DB':    ()
}

maintainer = {
 'name':  None,
 'email': None
}
