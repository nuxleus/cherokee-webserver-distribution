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
import validations

from util import *
from market.Install import Install_Stage
from market.Util import InstructionBox

# Load required modules
target   = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "target.pyo"),  "target_util")
tools    = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "tools.pyo"),   "tools_util")
java     = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "java.pyo"),    "java_util")

# Just for Virtual Servers
target.TARGETS = [
    ('vserver',   'Virtual Server'),
]
target.NOTE_CREATE_NEW = N_("At the time being, this package can only be configured under a new virtual server.")

POST_UNPACK_COMMANDS = [
    ({'command': 'chown -R ${root_user}:${root_group} ${app_root}'}),
    ({'command': 'chown -R ${web_user}:${web_group} ${app_root}/magnolia'}),
]

# Cfg chunks
# "catalina.sh run"           -> Does not fork
# "magnolia_control.sh start" -> Higher level, but forks
SOURCE = """
source!%(src_num)d!env_inherited = 0
source!%(src_num)d!type = host
source!%(src_num)d!nick = Magnolia %(src_num)d
source!%(src_num)d!host = %(localhost)s:%(src_port)d
source!%(src_num)d!interpreter = %(root)s/magnolia/apache-tomcat/bin/catalina.sh run
source!%(src_num)d!type = interpreter
source!%(src_num)d!env!JAVA_HOME = %(java_home)s
source!%(src_num)d!env_inherited = 0
source!%(src_num)d!timeout = 120
""" # It can take minutes to launch!!!

CONFIG_VSERVER = SOURCE + """
%(pre_vsrv)s!nick = %(target_vserver)s
%(pre_vsrv)s!document_root = /dev/null

%(pre_vsrv)s!rule!1!match = default
%(pre_vsrv)s!rule!1!encoder!gzip = 1
%(pre_vsrv)s!rule!1!handler = proxy
%(pre_vsrv)s!rule!1!handler!balancer = round_robin
%(pre_vsrv)s!rule!1!handler!balancer!source!1 = %(src_num)d
%(pre_vsrv)s!rule!1!handler!in_allow_keepalive = 1
%(pre_vsrv)s!rule!1!handler!in_preserve_host = 1
"""

CONFIG_DIR = SOURCE + """
%(pre_rule)s!match = directory
%(pre_rule)s!match!directory = %(target_directory)s

%(pre_rule)s!encoder!gzip = 1
%(pre_rule)s!handler = proxy
%(pre_rule)s!handler!balancer = round_robin
%(pre_rule)s!handler!balancer!source!1 = %(src_num)d
%(pre_rule)s!handler!in_allow_keepalive = 1
%(pre_rule)s!handler!in_preserve_host = 1
"""

URL_TARGET        = "/market/install/magnolia/config/target"
URL_SERVER_CONFIG = "/market/install/magnolia/config/server"
URL_ACCESS        = "/market/install/magnolia/access/user"

## Preconditions
class Precondition (Install_Stage):
    def __safe_call__ (self):
        box = CTK.Box()
        box += CTK.RawHTML ('<h1>%s</h1>' %(_("Checking for installation requirements")))

        if java.detect_java ('1.6'):
            box += CTK.RawHTML (js = CTK.DruidContent__JS_to_goto (box.id, URL_TARGET))
            return box.Render().toStr()

        box += InstructionBox (_(java.JAVA6_NOTE), java.JAVA6_INSTRUCTIONS)
        buttons = CTK.DruidButtonsPanel()
        buttons += CTK.DruidButton_Close(_('Cancel'))
        buttons += CTK.DruidButton_Goto (_('Retry'), market.Install.URL_INSTALL_SETUP_EXTERNAL, do_submit=True)
        return box.Render().toStr()

## Target
class Target (Install_Stage):
    def __safe_call__ (self):
        box = CTK.Box()
        target_wid = target.TargetSelection()
        target_wid.bind ('goto_next_stage', CTK.DruidContent__JS_to_goto (box.id, URL_SERVER_CONFIG))
        box += target_wid

        buttons = CTK.DruidButtonsPanel()
        buttons += CTK.DruidButton_Close(_('Cancel'))
        buttons += CTK.DruidButton_Submit (_('Next'), do_close=False)
        box += buttons

        return box.Render().toStr()

## Server configuration
class Server_Config (Install_Stage):
    def __safe_call__ (self):
        box = CTK.Box()
        pre = 'tmp!market!install'

        # Replacements
        app_id           = CTK.cfg.get_val ('%s!app!application_id'  %(pre))
        app_name         = CTK.cfg.get_val ('%s!app!application_name'%(pre))
        root             = CTK.cfg.get_val ('%s!root'                %(pre))
        target_type      = CTK.cfg.get_val ('%s!target'              %(pre))
        target_vserver   = CTK.cfg.get_val ('%s!target!vserver'      %(pre))
        target_vserver_n = CTK.cfg.get_val ('%s!target!vserver_n'    %(pre))
        target_directory = CTK.cfg.get_val ('%s!target!directory'    %(pre))
        pre_vsrv         = 'vserver!%s' %(target_vserver_n)

        src_num, x       = cfg_source_get_next()
        src_port         = cfg_source_find_free_port()
        localhost        = cfg_source_get_localhost_addr()
        java_home        = java.detect_java_home()

        # More replacements
        pre_rule = CTK.cfg.get_next_entry_prefix('%s!rule'%(pre_vsrv))
        tools.fix_server_port (root, src_port)

        # Pre-launch the application to save time
        tools.launch(root)

        # Apply the config
        if target_type == 'vserver':
            config = CONFIG_VSERVER%(locals())
            CTK.cfg.apply_chunk (config)

        elif target_type == 'directory':
            target_directory = target_directory.rstrip('/')
            config = CONFIG_DIR %(locals())
            CTK.cfg.apply_chunk (config)
            CTK.cfg.normalize ('%s!rule'%(pre_vsrv))

        # Redirect to final stage
        box += CTK.RawHTML (js = CTK.DruidContent__JS_to_goto (box.id, URL_ACCESS))
        return box.Render().toStr()


## User details
class Access_Details (Install_Stage):
    def __safe_call__ (self):
        box = CTK.Box()
        box += CTK.RawHTML ('<h2>%s</h2>' %(_("Access details")))
        box += CTK.RawHTML ('<p>%s</p>' %(_('Magnolia has been installed, and Cherokee is configured to automatically launch it whenever the resource is accessed if it is not already available. A one-time pre-launch has been issued to save time.')))
        box += CTK.RawHTML ('<p>%s</p>' %(_('Note that launching Magnolia can take up a couple of  minutes on modern servers, so please be patient the first time you access it.')))
        box += CTK.RawHTML ('<p>%s</p>' %(_('It is probably a good idea to pre-launch it instead of having the web-server do so on demand.')))
        box += CTK.RawHTML ('<p>%s</p>' %(_('These are the default access details:')))

        notice  = CTK.Notice ()
        notice += CTK.RawHTML ('<b>%s:</b>' %(_('User')))
        notice += CTK.Indenter (CTK.RawHTML ('superuser'))
        notice += CTK.RawHTML ('<b>%s:</b>' %(_('Password')))
        notice += CTK.Indenter (CTK.RawHTML ('superuser'))
        box += notice

        # Redirect to the Thanks page
        buttons = CTK.DruidButtonsPanel()
        buttons += CTK.DruidButton_Goto (_('Next'), market.Install.URL_INSTALL_DONE, do_submit=True)
        box += buttons

        return box.Render().toStr()


CTK.publish ('^%s$'%(market.Install.URL_INSTALL_SETUP_EXTERNAL), Precondition)
CTK.publish ('^%s$'%(URL_TARGET),        Target)
CTK.publish ('^%s$'%(URL_SERVER_CONFIG), Server_Config)
CTK.publish ('^%s$'%(URL_ACCESS),        Access_Details)
