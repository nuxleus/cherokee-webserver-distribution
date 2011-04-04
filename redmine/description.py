# -*- Mode: python; Coding: utf-8 -*-

DESC_SHORT = """<p>Redmine is a flexible project management
application. It is cross-platform and cross-database. It is an open
source, web-based project management and bug-tracking tool, and can
aid in visual representation of projects and their deadlines.</p>
"""

DESC_LONG = """<p>It supports multiple projects and provides
integrated project management features, issue tracking, and support
for multiple version control options.</p>

<p>It supports:</p>
<ul>
<li>Multiple projects support</li>
<li>Flexible role based access control</li>
<li>Flexible issue tracking system</li>
<li>Gantt chart and calendar</li>
<li>News, documents & files management</li>
<li>Feeds & email notifications</li>
<li>Per project wiki</li>
<li>Per project forums</li>
<li>Time tracking</li>
<li>Custom fields for issues, time-entries, projects and users</li>
<li>SCM integration (SVN, CVS, Git, Mercurial, Bazaar and Darcs)</li>
<li>Issue creation via email</li>
<li>Multiple LDAP authentication support</li>
<li>User self-registration support</li>
<li>Multilanguage support</li>
<li>Multiple databases support</li>
</ul>
"""

software = {
 'id':          'redmine',
 'name':        'Redmine',
 'version':     '1.1.2',
 'author':      'Redmine Community',
 'URL':         'http://www.redmine.org/',
 'icon_small':  'redmine_x96.png',
 'icon_big':    'redmine_x144.png',
 'screenshots': ('shots_459.png', 'shots_460.png', 'shots_461.png',),
 'desc_short':  DESC_SHORT,
 'desc_long':   DESC_LONG,
 'category':    'Development',
 'score':       5,
}

installation = {
  'modes': ('vserver', 'webdir'),
  'OS':    ('linux', 'macosx', 'freebsd'),
  'DB':    ('mysql','postgresql','sqlite3')
}

maintainer = {
 'name':  None,
 'email': None,
}
