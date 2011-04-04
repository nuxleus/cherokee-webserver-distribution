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

AJP_STR   = """<Connector port="8009" 
               enableLookups="false" redirectPort="8443" protocol="AJP/1.3" />"""
HTTP_STR  = """<Connector port="8080" maxHttpHeaderSize="8192"
               maxThreads="150" minSpareThreads="25" maxSpareThreads="75"
               enableLookups="false" redirectPort="8443" acceptCount="100"
               connectionTimeout="20000" disableUploadTimeout="true" />"""
PROXY_STR = """<Connector port="8082" 
               maxThreads="150" minSpareThreads="25" maxSpareThreads="75"
               enableLookups="false" acceptCount="100" connectionTimeout="20000"
               proxyPort="80" disableUploadTimeout="true" />"""

# Load required module
java = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "java.pyo"),    "java_util")

def fix_server_port (root, src_port):
    """Change deployment port"""
    try:
        path = os.path.join (root, 'magnolia', 'apache-tomcat', 'conf', 'server.xml')
        config = open (path, 'r').read()
        config = config.replace (AJP_STR, '<!-- %s -->'%(AJP_STR))   # Disable AJP port
        config = config.replace ('port="8080"', 'port="%s"'%(str(src_port)))
        open (path, 'w').write (config)
        market.Install_Log.log ("Default Magnolia port set to %s" %(src_port))
    except Exception, e:
        market.Install_Log.log ("Error setting default Magnolia port to %s" %(src_port))
        raise e


def launch (root):
    java_home = java.detect_java_home().strip()

    cmd = 'JAVA_HOME=%(java_home)s %(root)s/magnolia/apache-tomcat/bin/magnolia_control.sh start > /dev/null 2>&1' %(locals())
    if os.getuid() == 0:
        web_user = CTK.cfg.get_val ('server!user',  str(os.getuid()))
        cmd = 'su %s -c "%s"' %(web_user, cmd)

    market.Install_Log.log ("Launching Magnolia. Command: %s" %(cmd))

    ret = popen.popen_sync (cmd)

    if ret['retcode'] == 0:
        market.Install_Log.log ("Success: Magnolia launched")
    else:
        market.Install_Log.log ("Error: Magnolia not launched.\n%s" %(ret['stderr']))

    return ret
