# -*- Mode: python; Coding: utf-8 -*-

DESC_SHORT = """<p>Now easier to use, more flexible and more scalable,
Drupal 7 is the friendly and powerful content management platform for
building nearly any kind of website: from blogs and micro-sites to
collaborative social communities.</p>
"""

DESC_LONG = """<p>This philosophy obviously isn't for everyone. The
code is clean and light, and you will have a wide variety of plugins
to choose from so you can have the site of your dreams.</p>

<p><strong>Standout Features</strong></p>

<ul><li>Modules - thousands of them for utility, content, third-party integration, admin, content, media, e-commerce, and on and on.</li>
<li>Intense levels of personalization - considered to be the "core of Drupal."</li>
<li>Fully indexed and searchable content.</li>
<li>Role-based permissions - not so different from our other highly ranked systems, but vital nonetheless.</li>
</ul>

<p><strong>Management</strong></p>

<p>This CMS does offer a lot in the way of built-in
management. Analysis, tracking and statistics are built-in.</p>

<p>The web-based administration is a great plus here - you can
administer your Drupal site from a web browser anywhere in the world
and doesn't require any additional software or installation for
such.</p>

<p><strong>Performance</strong></p>

<p>Caching can be configured from the Administrator>Site
Configuration>Performance path. This reduces queries to the server and
will help a busy site stay up and running fast for its users.</p>

<p>The system also performs load balancing between multiple servers as
another way to keep the site running smoothly and quickly. This is a
built-in feature.</p>

<p><strong>Ease of Use</strong></p>

<p>Server page language and friendly URLs are built-ins. Almost
everything else can be added at will.</p>
"""

software = {
 'id':          'drupal7',
 'name':        'Drupal 7',
 'version':     '7.0',
 'author':      'Drupal Community',
 'URL':         'http://drupal.org/',
 'icon_small':  'drupal7_x96.png',
 'icon_big':    'drupal7_x144.png',
 'screenshots': ('shots_325.png', 'shots_337.png', 'shots_338.png', 'shots_339.png', 'shots_340.png',),
 'desc_short':  DESC_SHORT,
 'desc_long':   DESC_LONG,
 'category':    'Content Management',
 'score':       5,
}

installation = {
  'modes': ('vserver', 'webdir'),
  'OS':    ('linux', 'macosx', 'freebsd', 'solaris'),
  'DB':    ('mysql', 'sqlite3')
}

maintainer = {
 'name':  None,
 'email': None
}
