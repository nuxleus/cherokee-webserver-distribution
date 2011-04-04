# -*- Mode: python; Coding: utf-8 -*-

DESC_SHORT = """<p>MediaWiki is an Open Source software wiki package
written in PHP, originally for use on Wikipedia. It is now used by
several other projects of the non-profit Wikimedia Foundation and by
many other wikis.</p>"""

DESC_LONG = """<p>MediaWiki is basically a server-based software which
is licensed under the GNU General Public License (GPL). If you're
intent on creating a big or popular wiki don't worry - it's designed
to be run on a large server farm for a website that gets millions of
hits per day. MediaWiki uses PHP to process and display data stored in
its MySQL database. However, it requires no SQL database knowledge on
your part and pages use MediaWiki's wikitext format, so that users
without knowledge of XHTML or CSS can edit them easily.</p>

<p>A wiki enables communities to write documents collaboratively,
using a simple markup language and a web browser. A single page in a
wiki website is referred to as a "wiki page", while the entire
collection of pages, which are usually well interconnected by
hyperlinks, is "the wiki". A wiki is essentially a database for
creating, browsing, and searching through information. A wiki allows
for non-linear, evolving, complex and networked text, argument and
interaction.</p>

<p>A defining characteristic of wiki technology is the ease with which
pages can be created and updated. Generally, there is no review before
modifications are accepted. Many wikis are open to alteration by the
general public without requiring them to register user
accounts. Sometimes logging in for a session is recommended, to create
a "wiki-signature" cookie for signing edits automatically.[citation
needed] Many edits, however, can be made in real-time and appear
almost instantly online. This can facilitate abuse of the
system. Private wiki servers require user authentication to edit
pages, and sometimes even to read them.</p>

<p>Wikipedia must surely be on of the greatest innovations on the
Internet.</p>

<p>The secret of it's success was to harness the power of user general
knowledge via an extremely easy to use and read interface - a
wiki. MediaWiki is a small package which contains everything you need
to create your own wiki on any subject you choose. MediaWiki is
already being used by several other projects of the non-profit
Wikimedia Foundation including the MediaWiki developer site.</p>

<p>MediaWiki contains everything you need to get up and running with
your own no matter how big or small your project.</p>
"""

software = {
 'id':          'mediawiki',
 'name':        'MediaWiki',
 'version':     '1.16.2',
 'author':      'MediaWiki Community',
 'URL':         'http://www.mediawiki.org/',
 'icon_small':  'mediawiki_x96.png',
 'icon_big':    'mediawiki_x144.png',
 'screenshots': ('shots_424.png', 'shots_425.png', 'shots_426.png', 'shots_427.png', 'shots_428.png', 'shots_429.png',),
 'desc_short':  DESC_SHORT,
 'desc_long':   DESC_LONG,
 'category':    'Wiki',
 'score':       5,
}

installation = {
  'modes': ('vserver', 'webdir'),
  'OS':    ('linux', 'macosx', 'freebsd'),
  'DB':    ('mysql', 'postgresql', 'sqlite3')
}

maintainer = {
 'name':  None,
 'email': None,
}
