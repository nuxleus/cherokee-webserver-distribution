# -*- Mode: python; Coding: utf-8 -*-

DESC_SHORT = """<p>Sugar CRM is customer relationship management
software offering sales force, marketing automation, and customer
support functionality. It helps companies communicate with prospects,
share sales information, close deals, and keep customers happy.</p>
"""

DESC_LONG = """<p>Although customer relationship management (CRM) is
about much more than just software, the emphasis on CRM in sales and
marketing came about as technology developed fast enough to allow
sophisticated and automated management of customer processes.</p>

<p>This includes processes such as identifying a target market,
selecting prospects within that market, turning prospects into
customers and then managing the customer relationship to ensure best
value (for example, repeat business, brand loyalty, etc.). Software
exists to support all these functions and automate marketing
touches.</p>

<p>Many CRM software packages focus on the sales process including
tracking prospects and sales steps such as qualifying leads and making
appointments, as well as the communication processes such as targeted
email messages, letters and phone calls. Sugar CRM is an open source
solution with many of the features you would expect from any CRM
software system.</p>

<p>Sugar CRM can provide support to organisations in many areas of
operation.</p>

<p><strong>Sales Force Automation</strong></p>

<p>Sugar provides a number of features to aid the sales process. At
the most basic level, sales opportunities can be tracked as well as
contacts and accounts set up and managed. The software also allows an
organisation's sales process to be automated whether that's the names
of the sales teams or quotation numbers and prices.</p>

<p><strong>Marketing Automation</strong></p>

<p>Sugar CRM also provides features to support marketing campaigns,
from inception to delivery, including email marketing and
tracking.</p>

<p><strong>Customer Support</strong></p>

<p>Sugar CRM also provides support for managing inbound emails and
other communication and allows problems to be managed. Problems can be
tracked and full reporting is available.</p>

<p><strong>Sugar CRM Reporting</strong></p>

<p>The reporting capabilities of Sugar CRM are extensive and fully
customizable.</p>

<p>Sugar CRM provides a solution that can be used instantly and
intuitively. There are tutorials and videos available to help with all
aspects, as well as a support community of users and developers. The
user interface can be easily customized to suit any organisation
without the need for programming skills, however, if more detailed
change is needed then organisations can also amend the underlying
source code or ask the support community to provide additional
help.</p>

<p>Try it out. You will find that investing in Sugar CRM pays off.</p>
"""

software = {
 'id':          'sugar_ce',
 'name':        'Sugar CE',
 'version':     '6.1.4',
 'author':      'Sugar Community',
 'URL':         'http://wordpress.org/',
 'icon_small':  'sugar_x96.png',
 'icon_big':    'sugar_x144.png',
 'screenshots': ('shots_462.png', 'shots_463.png', 'shots_464.png', 'shots_465.png',),
 'desc_short':  DESC_SHORT,
 'desc_long':   DESC_LONG,
 'category':    'Business',
 'score':       5,
}

installation = {
  'modes': ('vserver', 'webdir'),
  'OS':    ('linux', 'macosx', 'freebsd'),
  'DB':    ('mysql', 'sqlserver')
}

maintainer = {
 'name':  None,
 'email': None,
}
