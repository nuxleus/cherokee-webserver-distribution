# -*- Mode: python; Coding: utf-8 -*-

DESC_SHORT = """<p>Magnolia powers the websites of government as well
as leading Fortune 500 enterprises in more than 100 countries on all
continents of the world. It is a leading Content Management System
favored for its ease-of-use and availability under an Open Source
license.</p>
"""

DESC_LONG = """<p>The page editing interface enables authors to lay
out content exactly as it would appear to the website visitor. Under
the hood, Magnolia contains best-of-breed Java technology based on
open standards to allow for tailor-made solutions. Enterprise-grade
support and services are available by the vendor and partners
world-wide.</p>

<p>Magnolia 4.3 introduces enterprise-grade templating features for
multi-site, multi-language and multi-domain scenarios.</p>

<p>Magnolia's largest group of Enterprise Edition customers is from
the financial sector, which includes banks, insurance companies and
other financial institutions. The ease and speed of deployment with
the Standard Templating Kit has attracted clients from media,
publishing and broadcasting. Due to Magnolia's open source approach
the system is favored by governments, universities, NGOs and the
military.</p>

<p>The Standard Templating Kit is a complete, out-of-the-box website
layout that conforms to accessibility standards. It provides
"templating best practice" and an extensive set of ready-made
functionality that can easily be extended for custom designs and
content output.</p>
"""

software = {
 'id':          'magnolia',
 'name':        'Magnolia',
 'version':     '4.4',
 'author':      'Magnolia CMS',
 'URL':         'http://www.magnolia-cms.com/',
 'icon_small':  'magnolia_x96.png',
 'icon_big':    'magnolia_x144.png',
 'screenshots': ('shots_367.png', 'shots_368.png', 'shots_369.png', 'shots_370.png'),
 'desc_short':  DESC_SHORT,
 'desc_long':   DESC_LONG,
 'category':    'Content Management',
 'score':       5,
}

installation = {
  'modes': ('vserver', 'webdir'),
  'OS':    ('linux', 'macosx', 'freebsd'),
  'DB':    ('mysql', 'postgresql', 'builtin')
}

maintainer = {
 'name':  None,
 'email': None,
}
