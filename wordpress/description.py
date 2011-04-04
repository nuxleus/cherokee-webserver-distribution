# -*- Mode: python; Coding: utf-8 -*-

DESC_SHORT = """<p>WordPress is a state-of-the-art, semantic, personal
publishing platform with a focus on aesthetics, Web standards, and
usability. It was born out of a desire for an elegant,
well-architected personal publishing system.</p>
"""

DESC_LONG = """<p>While primarily geared towards functioning as a
Weblog, WordPress is also a flexible CMS capable of managing many
types of Web sites.</p>

<p>In addition to the basic blog functions, it also has an integrated
link manager, categories, tags, custom taxonomies, file attachments,
XFN support, support for stand-alone pages, Atom and RSS feeds for
both content and comments, blogging API support (Atom Publishing
Protocol, Blogger, MetaWeblog, and Movable Type APIs), spam blocking
features, advanced cruft-free URL generation, a flexible theme system,
and an advanced plugin API.</p>

<p>WordPress is web software you can use to create a beautiful website
or blog. We like to say that WordPress is both free and priceless at
the same time.</p>

<p>The core software is built by hundreds of community volunteers, and
when you're ready for more there are thousands of plugins and themes
available to transform your site into almost anything you can
imagine. Over 25 million people have chosen WordPress to power the
place on the web they call "home". We'd love you to join the
family.</p>

<p><strong>State-of-the-art personal publishing platform</strong></p>

<p>WordPress is a state-of-the-art semantic personal publishing
platform with a focus on aesthetics, web standards, and
usability. What a mouthful.</p>

<p>WordPress is both free and priceless at the same time. More simply,
WordPress is what you use when you want to work with your blogging
software, not fight it. WordPress started with a single bit of code to
enhance the typography of everyday writing on the web and fewer users
than you can count on your hands and toes. Since then it has grown to
be the largest self-hosted blogging tool in the world, used on
hundreds of thousands of sites and seen by millions of people every
day.</p>

<p>Everything you see, from the documentation to the code itself, was
created by and for the community.</p>

<p>WordPress is an Open Source project, which means there are hundreds
of people all over the world working on it.</p>

<p>It also means you are free to use it for anything from your cat's
home page to a Fortune 500
"""

software = {
 'id':          'wordpress',
 'name':        'WordPress',
 'version':     '3.1.0',
 'author':      'Wordpress Community',
 'URL':         'http://wordpress.org/',
 'icon_small':  'wp_x96.png',
 'icon_big':    'wp_x144.png',
 'screenshots': ('shots_377.png', 'shots_378.png', 'shots_379.png', 'shots_380.png', 'shots_381.png', 'shots_382.png', 'shots_383.png', 'shots_384.png', 'shots_385.png',),
 'desc_short':  DESC_SHORT,
 'desc_long':   DESC_LONG,
 'category':    'Content Management',
 'score':       5,
}

installation = {
  'modes': ('vserver', 'webdir'),
  'OS':    ('linux', 'macosx', 'freebsd'),
  'DB':    ('mysql')
}

maintainer = {
 'name':  'Taher Shihadeh',
 'email': 'taher@unixwars.com'
}
