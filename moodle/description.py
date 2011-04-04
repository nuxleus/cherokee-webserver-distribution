# -*- Mode: python; Coding: utf-8 -*-

DESC_SHORT = """<p>Moodle is a Course Management System (CMS), also
known as a Learning Management System (LMS) or a Virtual Learning
Environment (VLE). It is a web application that educators can use to
create effective online learning sites.</p>
"""

DESC_LONG = """<p>Moodle is a software package for producing
Internet-based courses and web sites. It is a global development
project designed to support a social constructionist framework of
education.</p>

<p>Moodle is provided as Open Source software (under the GNU Public
License). Basically this means Moodle is copyrighted, but that you
have additional freedoms. You are allowed to copy, use and modify
Moodle provided that you agree to: provide the source to others; not
modify or remove the original license and copyrights, and apply this
same license to any derivative work. Read the license for full details
and please contact the copyright holder directly if you have any
questions.</p>

<p>Moodle can be installed on any computer that can run PHP, and can
support an SQL type database (for example MySQL). There are many
knowledgeable Moodle Partners to assist you, and even host your Moodle
site.</p>

<p>The word Moodle was originally an acronym for Modular
Object-Oriented Dynamic Learning Environment, which is mostly useful
to programmers and education theorists. It's also a verb that
describes the process of lazily meandering through something, doing
things as it occurs to you to do them, an enjoyable tinkering that
often leads to insight and creativity. As such it applies both to the
way Moodle was developed, and to the way a student or teacher might
approach studying or teaching an online course. Anyone who uses Moodle
is a Moodler. Come moodle with us!</p>
"""

software = {
 'id':          'moodle',
 'name':        'Moodle',
 'version':     '2.0.2',
 'author':      'Moodle Community',
 'URL':         'http://moodle.org/',
 'icon_small':  'moodle_x96.png',
 'icon_big':    'moodle_x144.png',
 'screenshots': ('shots_415.png', 'shots_416.png', 'shots_417.png', 'shots_418.png', 'shots_419.png', 'shots_420.png', 'shots_421.png', 'shots_422.png', 'shots_423.png',),
 'desc_short':  DESC_SHORT,
 'desc_long':   DESC_LONG,
 'category':    'Web Applications',
 'score':       5,
}

installation = {
  'modes': ('vserver', 'webdir'),
  'OS':    ('linux', 'freebsd'),
  'DB':    ('mysql', 'postgresql')
}

maintainer = {
 'name':  None,
 'email': None
}
