# -*- coding: utf-8 -*-
#
# Cherokee Distribution
#
# Authors:
#      Alvaro Lopez Ortega <alvaro@alobbs.com>
#
# Copyright (C) 2011 Alvaro Lopez Ortega
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of version 2 of the GNU General Public
# License as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#

import os
import CTK
import market
import SystemInfo
from util import *

cc = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "cc.pyo"), "cc_util")

ANON_USER_MAPPING = """{}"""
AUTH_USER_MAPPING = """{'%(davpath)s': {'%(user)s': {'password': '%(pass)s', 'description': '', 'roles': []}}}"""

UWSGI_CONFIG = """
<uwsgi>
        <master/>
        <processes>4</processes>
        <socket>%(localhost)s:%(src_port)d</socket>

        <![CDATA[

from wsgidav.fs_dav_provider import FilesystemProvider
from wsgidav.wsgidav_app import DEFAULT_CONFIG, WsgiDAVApp

provider = FilesystemProvider('%(webdav_dir)s')

config = DEFAULT_CONFIG.copy()

config.update({
    "provider_mapping": {"/": provider},
    "user_mapping": {},
    "verbose": 1,
    "enable_loggers": [],
    "propsmanager": True,
    "locksmanager": True,
    "domaincontroller": None,
    })

application = WsgiDAVApp(config)

]]>

</uwsgi>
"""

XML2_NOTE = N_("Your system doesn't seem to provide the required dependecy 'xml2-config'")
XML2_INSTRUCTIONS = {
    'zypper':   'sudo zypper install libxml2-devel',
    'default':   N_('The XML C parser and toolkit of Gnome is available at http://xmlsoft.org/')
}

def check_cc ():
    bin = cc.detect_cc()
    if not bin:
        return (cc.CC_NOTE, cc.CC_INSTRUCTIONS)


def check_xml2config ():
    bin = path_find_binary (['xml2-config'], cc.CC_PATHS)
    if not bin:
        return (XML2_NOTE, XML2_INSTRUCTIONS)


def create_xml (root, localhost, src_port, webdav_dir):
    config = UWSGI_CONFIG % (locals())
    path   = os.path.join (root, 'uwsgi', 'wsgidav.xml')

    try:
        open(path, 'w').write(config)
        market.Install_Log.log ('uwsgi/wsgidav.xml created successfully.')
    except:
        market.Install_Log.log ('uwsgi/wsgidav.xml could not be created.')
        raise EnvironmentError, 'Could not write XML file'
