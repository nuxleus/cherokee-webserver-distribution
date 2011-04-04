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

AJP_STR = """<Connector port="8009" protocol="AJP/1.3" redirectPort="8443" URIEncoding="UTF-8" />"""

def fix_server_port (root, src_port):
    """Change deployment port"""
    try:
        path = os.path.join (root, 'liferay', 'tomcat', 'conf', 'server.xml')
        config = open (path, 'r').read()
        config = config.replace (AJP_STR, '<!-- %s -->'%(AJP_STR)) # Disable AJP port
        config = config.replace ('port="8080"', 'port="%s"'%(str(src_port)))
        open (path, 'w').write (config)
        market.Install_Log.log ("Default Liferay port set to %s" %(src_port))
    except Exception, e:
        market.Install_Log.log ("Error setting default Liferay port to %s" %(src_port))
        raise e

def fix_context (root, target_directory):
    """Change Liferay context from / to target_directory"""
    market.Install_Log.log ("Root Context adjustment.")
    if not target_directory:
        market.Install_Log.log ("    Installing as Virtual Server. Root context change not needed.")
        return

    src = os.path.join (root, 'liferay', 'tomcat', 'webapps', 'ROOT')
    dst = os.path.join (root, 'liferay', 'tomcat', 'webapps', target_directory.strip('/'))
    ret = popen.popen_sync ('mv %s %s' %(src, dst), retcode=True)
    if ret['retcode']:
        msg = "Error: Unable to move ROOT directory."
        market.Install_Log.log ("    %s" %(msg))
        raise EnvironmentError, msg

    try:
        path = os.path.join (dst, 'WEB-INF', 'classes', 'portal-ext.properties')
        open(path, 'w').write ('portal.ctx=%s\n' %(target_directory))
    except:
        msg = "Error: Unable to write portal-ext.properties."
        market.Install_Log.log ("    %s" %(msg))
        raise EnvironmentError, msg

    src = os.path.join (root, 'liferay', 'tomcat', 'conf', 'Catalina', 'localhost', 'ROOT.xml')
    dst = os.path.join (root, 'liferay', 'tomcat', 'conf', 'Catalina', 'localhost', '%s.xml' % (target_directory.strip('/')))
    ret = popen.popen_sync ('mv %s %s' %(src, dst), retcode=True)
    if ret['retcode']:
        msg = "Error: Unable to move XML file."
        market.Install_Log.log ("    %s" %(msg))
        raise EnvironmentError, msg

    market.Install_Log.log ("    Root Context successfuly changed to %s." %(target_directory))

def delete_sample_data (root):
    market.Install_Log.log ("Sample Data Removal.")
    props  = os.path.join (root, 'liferay', 'data', 'hsql', 'lportal.properties')
    script = os.path.join (root, 'liferay', 'data', 'hsql', 'lportal.script')
    hook   = os.path.join (root, 'liferay', 'tomcat', 'webapps', 'sevencogs-hook')
    ret = popen.popen_sync ('rm -rf %s %s %s' %(props, script, hook), retcode=True)
    if ret['retcode']:
        msg = "Error: Unable to remove 7Cogs sample data."
        market.Install_Log.log ("    %s" %(msg))
        raise EnvironmentError, msg

    market.Install_Log.log ("    7Cogs sample data removed.")

def launch (root):
    cmd = 'nohup %(root)s/liferay/tomcat/bin/startup.sh > /dev/null 2>&1' %(locals())
    if os.getuid() == 0:
        web_user = CTK.cfg.get_val ('server!user',  str(os.getuid()))
        cmd = 'su %s -c "%s"' %(web_user, cmd)

    market.Install_Log.log ("Launching Liferay. Command: %s" %(cmd))
    ret = popen.popen_sync (cmd)

    if ret['retcode'] == 0:
        market.Install_Log.log ("Success: Liferay launched")
    else:
        market.Install_Log.log ("Error: Liferay not launched.\n%s" %(ret['stderr']))

    return ret
