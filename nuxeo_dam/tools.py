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
import popen
from util import *

def create_configuration (root, src_port):
    """Change custom deployment port"""
    try:
        path = os.path.join (root, 'nuxeo', 'templates', 'market', 'nuxeo.defaults')
        config = open (path, 'r').read()
        config = config.replace ('nuxeo.server.http.port=8080', 'nuxeo.server.http.port=%s'%(str(src_port)))
        config = config.replace ('nuxeo.server.ajp.port', '#nuxeo.server.ajp.port')
        open (path, 'w').write (config)
        market.Install_Log.log ("Default Nuxeo configuration created (port %s)" %(src_port))
    except Exception, e:
        market.Install_Log.log ("Error setting default Nuxeo configuration (port %s)" %(src_port))

def launch (root):
    cmd = 'nohup %(root)s/nuxeo/bin/nuxeoctl startbg' %(locals())
    if os.getuid() == 0:
        web_user = CTK.cfg.get_val ('server!user',  str(os.getuid()))
        cmd = 'su %s -c "%s"' %(web_user, cmd)

    market.Install_Log.log ("Launching Nuxeo. Command: %s" %(cmd))

    ret = popen.popen_sync (cmd)

    if ret['retcode'] == 0:
        market.Install_Log.log ("Success: Nuxeo launched")
    else:
        market.Install_Log.log ("Error: Nuxeo not launched.\n%s" %(ret['stderr']))

    return ret
