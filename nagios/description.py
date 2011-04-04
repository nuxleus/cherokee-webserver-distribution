# -*- Mode: python; Coding: utf-8 -*-

DESC_SHORT = """<p>Nagios is a powerful monitoring system that enables
organizations to identify and resolve IT infrastructure problems
before they affect critical business processes. It is used to build
business processes resilient to unknown outages.</p>
"""

DESC_LONG = """<p>Nagios is a powerful tool. Designed with scalability and flexibility in mind, that provides you with instant awareness of your organization's mission-critical IT infrastructure. Nagios allows you to detect and repair problems and mitigate future issues before they affect end-users and customers.</p>

<p>By using Nagios, you can:</p>

<ul>
<li>Plan for infrastructure upgrades before outdated systems cause failures</li>
<li>Respond to issues at the first sign of a problem</li>
<li>Automatically fix problems when they are detected</li>
<li>Coordinate technical team responses</li>
<li>Ensure your organization's SLAs are being met</li>
<li>Ensure IT infrastructure outages have a minimal effect on your organization's bottom line</li>
<li>Monitor your entire infrastructure and business processes</li>
</ul>

<strong>How it workds</strong>
<ul>

<li>Monitoring: IT staff configure Nagios to monitor critical IT
infrastructure components, including system metrics, network
protocols, applications, services, servers, and network
infrastructure.</li>

<li>Alerting: Nagios sends alerts when critical infrastructure
components fail and recover, providing administrators with notice of
important events. Alerts can be delivered via email, SMS, or custom
script.</li>

<li>Response: IT staff can acknowledge alerts and begin resolving
outages and investigating security alerts immediately. Alerts can be
escalated to different groups if alerts are not acknowledged in a
timely manner.</li>

<li>Reporting: Reports provide a historical record of outages, events,
notifications, and alert response for later review. Availability
reports help ensure your SLAs are being met.</li>

<li>Maintenance: Scheduled downtime prevents alerts during scheduled
maintenance and upgrade windows.</li>

<li>Planning: Trending and capacity planning graphs and reports allow
you to identify necessary infrastructure upgrades before failures
occur.</li>
</ul>
"""

software = {
 'id':          'nagios',
 'name':        'Nagios',
 'version':     '3.2.3',
 'author':      'Nagios Community',
 'URL':         'http://www.nagios.org/',
 'icon_small':  'nagios_x96.png',
 'icon_big':    'nagios_x144.png',
 'screenshots': ('shots_248.png', 'shots_249.png', 'shots_250.png', 'shots_251.png',),
 'desc_short':  DESC_SHORT,
 'desc_long':   DESC_LONG,
 'category':    'Development',
 'score':       5,
}

installation = {
  'modes': ('vserver', 'webdir'),
  'OS':    ('linux', 'freebsd', 'macosx'),
  'DB':    (),
}

maintainer = {
 'name':  None,
 'email': None,
}
