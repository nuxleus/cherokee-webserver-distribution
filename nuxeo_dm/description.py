# -*- Mode: python; Coding: utf-8 -*-

DESC_SHORT = """<p>Feature-rich, comprehensive document management
solution. From initial capture and creation, collaboration, across
approval, review and revisions, to the final publication and
archiving, Nuxeo DM is the best tool to manage corporate content.</p>
"""

DESC_LONG = """<p>Collaborative document management has become an
infrastructure requirement of 21st century business. Managing and
tracking the flow of content through the business cycle enables user
to engage with corporate information efficiently.</p>

<p>Secure interactive workspaces connect teams to their critical
documents, even across the most distributed, decentralized
organizations. Users can work in the online or offline web or desktop
experience they prefer, editing their content live or uploading /
downloading as needed.</p>

<p><strong>Key benefits</strong></p>

<p>Nuxeo DM, a state-of-the-art application built on a new generation
of ECM platform, provides:</p>

<ul><li>Streamlined information access across diverse repositories</li>
<li>Improved productivity, with the automation of routine tasks</li>
<li>A trusted repository, designed for secure and easy scaling as projects expand</li>
<li>Flexibility, with a modular, open source platform,</li>
<li>Adaptability, with Nuxeo Studio, a configuration and customization environment</li>
<li>Interoperability, with open standards, including CMIS and Dublin Core</li>
</ul>
"""

software = {
 'id':          'nuxeo_dm',
 'name':        'Nuxeo DM',
 'version':     '5.4.0.1',
 'author':      'Nuxeo',
 'URL':         'http://www.nuxeo.org/',
 'icon_small':  'nuxeo_x96.png',
 'icon_big':    'nuxeo_x144.png',
 'screenshots': ('shots_259.png', 'shots_261.png', 'shots_262.png', 'shots_264.png'),
 'desc_short':  DESC_SHORT,
 'desc_long':   DESC_LONG,
 'category':    'Content Management',
 'score':       5,
}

installation = {
  'modes': ('vserver', 'webdir'),
  'OS':    ('linux'),
  'DB':    ('mysql', 'postgresql', 'builtin')
}

maintainer = {
 'name':  None,
 'email': None,
}
