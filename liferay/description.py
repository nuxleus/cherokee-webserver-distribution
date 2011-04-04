# -*- Mode: python; Coding: utf-8 -*-

DESC_SHORT = """<p>Liferay Portal is an enterprise web platform for
building business solutions that deliver immediate results and
long-term value. Get the benefits of packaged applications and an
enterprise application framework in a single solution. </p>
"""

DESC_LONG = """<p>Liferay Portal ships with broad product capabilities
to provide immediate return on investment:</p>

<ul><li>Content & Document Management with Microsoft Office integration</li>
<li>Web Publishing and Shared Workspaces</li>
<li>Enterprise Collaboration</li>
<li>Social Networking and Mashups</li>
<li>Enterprise Portals and Identity Management</li>
</ul>
"""

software = {
 'id':          'liferay',
 'name':        'Liferay CE',
 'version':     '6.0.6',
 'author':      'Liferay Community',
 'URL':         'http://www.liferay.com/community',
 'icon_small':  'liferay_x96.png',
 'icon_big':    'liferay_x144.png',
 'screenshots': ('shots_411.png', 'shots_412.png', 'shots_413.png', 'shots_414.png'),
 'desc_short':  DESC_SHORT,
 'desc_long':   DESC_LONG,
 'category':    'Business',
 'score':       5,
}

installation = {
  'modes': ('vserver', 'webdir'),
  'OS':    ('linux', 'macosx', 'solaris'),
  'DB':    ('mysql', 'postgresql')
}

maintainer = {
 'name':  None,
 'email': None,
}
