# -*- Mode: python; Coding: utf-8 -*-

DESC_SHORT = """<p>Comprehensive digital asset management
solution. The Nuxeo Digital Asset Management offering, Nuxeo DAM,
helps marketing and brand managers catalogue, process, and distribute
rich media content, including images, audio, and video.</p>
"""

DESC_LONG = """<p>Digital Asset Management has become a core
infrastructure requirement for media organizations and marketing
departments that need to protect their media content
investment. Issues such as intellectual property management, local
regulations concerning the distribution of media content, and media
asset search/retrieval can become unmanageable in the face of large
volumes of content and diverse distribution channels.</p>

<p>Streamlining these tasks enables creative users to focus on ideas
and design by freeing them from resource-intensive content control
tasks.</p>

<p><strong>Key benefits</strong></p>

<p>Nuxeo DAM, a state-of-the-art application built on a new generation
of ECM, provides:</p>

<ul><li>An intuitive experience, designed for creative users</li>
<li>Improved productivity, with the automation and streamlining of routine tasks</li>
<li>A trusted repository, designed for secure and easy scaling as projects expand</li>
<li>Interoperability, with a CMIS-enabled platform</li>
</ul>

<p>Nuxeo DAM is a packaged application based on Nuxeo EP (Enterprise
Platform), an extensible, Java-based ECM platform. Nuxeo EP is
CMIS-enabled, thus ensuring that Nuxeo DAM benefits from the
interoperability capabilities of the underlying platform. What does
this mean? Organizations can safely invest in any number of
CMIS-compliant Web Content Management offerings, and be assured that
their rich media assets in Nuxeo DAM are easily distributed to create
an engaging web experience.</p>
"""

software = {
 'id':          'nuxeo_dam',
 'name':        'Nuxeo DAM',
 'version':     '1.2',
 'author':      'Nuxeo',
 'URL':         'http://www.nuxeo.org/',
 'icon_small':  'nuxeo_x96.png',
 'icon_big':    'nuxeo_x144.png',
 'screenshots': ('shots_430.png', 'shots_431.png', 'shots_432.png', 'shots_433.png'),
 'desc_short':  DESC_SHORT,
 'desc_long':   DESC_LONG,
 'category':    'Content Management',
 'score':       5,
}

installation = {
  'modes': ('vserver', 'webdir'),
  'OS':    ('linux',),
  'DB':    ('mysql', 'postgresql', 'builtin')
}

maintainer = {
 'name':  None,
 'email': None,
}
