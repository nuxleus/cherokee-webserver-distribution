# -*- Mode: python; Coding: utf-8 -*-

DESC_SHORT = """<p>Vanilla is an open-source, pluggable, themable,
multi-lingual community-building solution. It is specially made to
help small communities grow larger through SEO mojo, totally
customizable social tools, and great user experience.</p>"""

DESC_LONG = """<p>Vanilla can seamlessly integrate with your existing
website, blog, or custom-built application.</p>

<p>Vanilla's major features include: forum, custom domain, custom
theme, sso (single sing-on), stats, advanced role-management, and
more.</p>

<p>Vanilla is a powerful community publishing platform, and it comes
with a great set of features designed to make your experience and your
communities experience easy and as pleasant and appealing as
possible. It offers a standards-compliant, fast, and light publishing
platform, with sensible default settings and features, and an
extremely customizable core.</p>

<p>There is also a large number of powerful plugins, that extend the
functionality of Vanilla. The core of Vanilla is designed to be lean,
to maximize flexibility and minimize code bloat. Plugins offer custom
functions and features so that you can tailor your community to your
specific needs.</p>
"""

software = {
 'id':          'vanilla',
 'name':        'Vanilla',
 'version':     '2.0.17.9',
 'author':      'Vanilla',
 'URL':         'http://vanillaforums.org',
 'icon_small':  'vanilla_x96.png',
 'icon_big':    'vanilla_x144.png',
 'screenshots': ('shots_466.png', 'shots_467.png', 'shots_468.png', 'shots_469.png'),
 'desc_short':  DESC_SHORT,
 'desc_long':   DESC_LONG,
 'category':    'Content Management',
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
