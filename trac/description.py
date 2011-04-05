# -*- Mode: python; Coding: utf-8 -*-

DESC_SHORT = """<p>Trac is an enhanced wiki and issue tracking system
for software development projects using a minimalistic approach to
web-based software project management. Its mission is to help
developers write great software while staying out of the way.</p>
"""

DESC_LONG = """
<p>Trac should impose as little as possible on a team's established
development process and policies. It provides an interface to
Subversion (or other version control systems), an integrated Wiki and
convenient reporting facilities.</p>

<p>Trac allows wiki markup in issue descriptions and commit messages,
creating links and seamless references between bugs, tasks,
changesets, files and wiki pages. A timeline shows all current and
past project events in order, making the acquisition of an overview of
the project and tracking progress very easy. The roadmap shows the
road ahead, listing the upcoming milestones.</p>

<p><strong>Wiki Engine</strong></p>

<p>The built-in wiki makes documenting your project, collaborative
editing, feedback and discussion notes available - and editable - at
all times. Documentation for Trac itself is also included as wiki
pages.</p>

<p>Editing wiki text is easy, using a simplified syntax rather than
HTML. This makes editing easier and encourages people to annotate and
contribute text content.</p>

<p><strong>Issue Tracker</strong></p>

<p>The Trac issue tracker aims to be straight-forward and simple to
use. Reporting bugs with Trac is very easy. With no required data
fields , the user can focus on what's important, describing the
case.</p>

<p>Use the issue tracker to manage bugs, tasks, enhancement requests
and customer feedback.</p>

<p>Viewing a ticket reveals the entire history of the issue case,
including added comments, change of status, priority and
assignment.</p>

<p><strong>Project Timeline</strong></p>

<p>The timeline gives you an ordered list of events throughout the
project, an instant progress report.</p>

<p>It's easy to acquire perspective on development and direction of a
project using the timeline to correlate issues, code patches and wiki
edits.</p>

<p><strong>Code Browser</strong></p>

<p>The code browser lets you navigate a source code repository
directly. You can browse revisions and access specific revisions of
files, view changeset logs and download files.</p>

<p>Currently, Trac supports the subversion revision control system,
and we're planning on support for CVS and Arch in later versions.</p>

<p><strong>Changeset Viewer</strong></p>

<p>Viewing changes to source code and text files in the repository is
made easy using the built-in changeset viewer.</p>

<p>When a someone commits a changeset, Trac shows the contents of a
changeset by displaying the difference between the new and previous
revisions of each file of the changeset. The display is an easy to
read and intuitive side-by-side view clearly marking added, removed
and modified lines in the source code.</p>

<p><strong>Project Reports</strong></p>

<p>Reports lets project members and users search and visualize project
data with a single click. For example: Show all active tickets sorted
by priority, or list all tasks assigned to a specific developer.</p>

<p>You can also create customized reports to suit your own project
requirements.</p>
"""

software = {
 'id':          'trac',
 'name':        'Trac',
 'version':     '0.12',
 'author':      'Trac Community',
 'URL':         'http://trac.edgewall.org/',
 'icon_small':  'trac_x96.png',
 'icon_big':    'trac_x144.png',
 'screenshots': ('shots_186.png', 'shots_187.png', 'shots_188.png', 'shots_189.png',),
 'desc_short':  DESC_SHORT,
 'desc_long':   DESC_LONG,
 'category':    'Development',
 'score':       5,
}

installation = {
  'modes': ('vserver', 'webdir'),
  'OS':    ('linux', 'macosx', 'freebsd'),
  'DB':    ('mysql',)
}

maintainer = {
 'name':  None,
 'email': None
}
