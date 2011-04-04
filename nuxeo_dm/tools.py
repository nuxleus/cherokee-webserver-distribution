#
# Copyright (c) 2010, Octality S.L. - Eume 6, Villaviciosa de Odon,
# 28670 Madrid, SPAIN. All rights reserved.
#
# Any unauthorized dissemination, distribution or copying is strictly
# forbidden.
#

import os
import CTK
import market
import popen
from util import *

def fix_server_port (root, src_port):
    """Change deployment port"""
    try:
        path = os.path.join (root, 'nuxeo', 'templates', 'default', 'nuxeo.defaults')
        config_src = open (path, 'r').read()
        config_dst = config_src.replace ('8080', (str(src_port)))
        if config_src == config_dst:
            raise Exception, "Port replacement failed"
        open (path, 'w').write (config_dst)
        market.Install_Log.log ("Default Nuxeo port set to %s" %(src_port))
    except Exception, e:
        market.Install_Log.log ("Error setting default Nuxeo port to %s" %(src_port))
        raise e

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
