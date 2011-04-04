# -*- Mode: python; Coding: utf-8 -*-

DESC_SHORT = """
<p>Joomla! is known as one of the leading and most powerful content
management system software out there. Joomla! applications will keep
track of every piece of content on your site from text and photos to
music and video.</p>
"""

DESC_LONG = """
<p>Choose to manage menus, content, components, extensions or tools
from the admin navigation bar. The text editor is
self-explanatory.</p>

<p><strong>Standout Features</strong></p>

<ul><li>Easy installation</li>
<li>Flexible configuration</li>
<li>Mobile plugin that optimizes Joomla! for mobile</li>
<li>Plugins for all commerce options</li>
</ul>

<p><strong>Built-in Applications</strong></p>

<p>Built-in applications are a-plenty with this system. The blog
function is quite comprehensive. Between the built-ins and the plugins
Joomla! can be used to create corporate sites or portals, corporate
intranets and extranets, online zines, newspapers and other
publications, e-commerce and online reservations, small business
sites, non-profit sites, school and church Web sites and even personal
or family sites.</p>

<p>Creating a new content is as easy as 1,2,3. Within the content tab,
choose "new article" and try to input some text to use for the front
page. It won't let you publish or save this information unless you
have first created a section(s) and category(ies) in which the content
can live. It only takes a few seconds to navigate back to the section
and category managers in which you created, named and saved those
areas.</p>

<p>Next go back to the content tab and select the article function, at
which point you will have successfully added some text for the front
page. If you want to just blog with this program, name a section and
category, then when you create an article select "front page" in the
editor and your blog entries will appear in standard blog format.</p>

<p>Each post or article can be optimized inside the editor as well -
you can enter meta data and keywords for each post.</p>

<p>Joomla! does not submit to blog directories for you so if you use
Joomla you will have to register with the aggregator and/or directory
services of your choice so your entries will be submitted to the
search engines.</p>

<p>In this system, an Article is some written information that you
want to display on your site. It normally contains some text and can
contain pictures and other types of content. Sections and categories
in Joomla! provide an optional method for organizing your
articles. Here's how it works. A Section contains one or more
categories, and each Category can have articles assigned to it. One
Article can only be in one Category and Section.</p>

<p>First, there are built-in Menu Item Types in Joomla! that take
advantage of this organization. These are the Section Blog, Section
List, Category Blog, and Category List. These Menu Item Types (also
called "layouts") make it very easy to show articles that belong to
sections or categories. As new articles are created and assigned to
sections and categories, they will automatically be placed on these
pages according to the parameters you set for each page.</p>

<p>The media formats you can insert include Flash, Quicktime,
Shockware, Windows Media and Real Media.</p>
"""

software = {
 'id':          'joomla',
 'name':        'Joomla',
 'version':     '1.6.1',
 'author':      'Joomla Community',
 'URL':         'http://www.joomla.org/',
 'icon_small':  'joomla_x96.png',
 'icon_big':    'joomla_x144.png',
 'screenshots': ('shots_403.png', 'shots_404.png', 'shots_405.png', 'shots_406.png',),
 'desc_short':  DESC_SHORT,
 'desc_long':   DESC_LONG,
 'category':    'Content Management',
 'score':       5,
}

installation = {
  'modes': ('vserver', 'webdir'),
  'OS':    ('linux', 'macosx', 'freebsd'),
  'DB':    ('mysql','postgresql')
}

maintainer = {
 'name':  None,
 'email': None,
}
