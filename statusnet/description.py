# -*- Mode: python; Coding: utf-8 -*-

DESC_SHORT = """<p>StatusNet is the open source microblogging platform
that helps you share and connect in real-time within your own
domain. With StatusNet you can encourage collaboration, build and
engage your community, and be in command of your brand.</p>
"""

DESC_LONG = """<p>StatusNet is an Open Source microblogging
platform. It helps people in a community, company or group to exchange
short (140 characters, by default) messages over the Web. Users can
choose which people to "follow" and receive only their friends' or
colleagues' status messages. It provides a similar service to sites
like Twitter, Google Buzz, or Yammer.</p>

<p>With a little work, status messages can be sent to mobile phones,
instant messenger programs (GTalk/Jabber), and specially-designed
desktop clients that support the Twitter API. StatusNet supports an
open standard called OStatus that lets users in different networks
follow each other. It enables a distributed social network spread all
across the Web.</p>
"""

software = {
 'id':          'statusnet',
 'name':        'StatusNet',
 'version':     '0.9.7',
 'author':      'StatusNet Community',
 'URL':         'http://status.net/',
 'icon_small':  'statusnet_x96.png',
 'icon_big':    'statusnet_x144.png',
 'screenshots': ('shots_407.png', 'shots_408.png', 'shots_409.png', 'shots_410.png'),
 'desc_short':  DESC_SHORT,
 'desc_long':   DESC_LONG,
 'category':    'Web Applications',
 'score':       5,
}

installation = {
  'modes': ('vserver', 'webdir'),
  'OS':    ('linux', 'macosx', 'freebsd'),
  'DB':    ('mysql', 'postgresql')
}

maintainer = {
 'name':  None,
 'email': None,
}
