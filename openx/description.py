# -*- Mode: python; Coding: utf-8 -*-

DESC_SHORT = """<p>OpenX is an open source ad serving tool formerly
known as Openads and phpAdsNew. It is both robust and powerful.  It is
used by more than 200,000 websites in more than 100 countries and
serve more than 350 billion ads monthly.</p>
"""

DESC_LONG = """<p>It enables publishers to serve ads, magange
campaigns from different advertisers and/or ad networks, track and
report on campaign success, and set rules to target the delivery of
campaigns, or even ads, to specific users, to help maximise the
effectiveness of campaigns.</p>

<p>OpenX solves a problem that can quickly become overwhelming - ad
management. When you are in charge of managing numerous advertising
assets you come to know how complex this can be. OpenX Ad Server makes
this job simple with plenty of management tools that allow you to
serve to specific Web sites, zones, and channels. With the OpenX
management console you can manage individual ad banners, campaigns,
zones, and more. With OpenX you can serve up as few or as many ads as
you need.</p>

<ul>
<li>Simple management console: Manage all aspects of your OpenX server
from one easy Web-based console.</li>

<li>Outstanding report generators: Generate many different types of
reports from single ads to global reports.</li>

<li>Easy Web-based installation: Installation can be completed in less
than five minutes with an easy Web-based installation tool.</li>

<li>Robust plugin system to expand your installation: Add as few or as
many plugins (widgets) as you need. Once installed, plugins can be
enabled or disabled with a simple drag and drop.</li>
</ul>
"""

software = {
 'id':          'openx',
 'name':        'OpenX',
 'version':     '2.8.7',
 'author':      'OpenX',
 'URL':         'http://www.openx.org/',
 'icon_small':  'openx_x96.png',
 'icon_big':    'openx_x144.png',
 'screenshots': ('shots_289.png', 'shots_290.png', 'shots_291.png', 'shots_292.png'),
 'desc_short':  DESC_SHORT,
 'desc_long':   DESC_LONG,
 'category':    'Business',
 'score':       5,
}

installation = {
  'modes': ('vserver', 'webdir'),
  'OS':    ('linux', 'macosx', 'freebsd'),
  'DB':    ('mysql',)
}

maintainer = {
 'name':  None,
 'email': None,
}
