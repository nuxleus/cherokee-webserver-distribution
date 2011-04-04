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

POST_UNPACK_COMMANDS = [
    ({'command': 'mv ${app_root}/nuxeo-dm-5.4.0.1-tomcat ${app_root}/nuxeo', 'check_ret': True}),
    ({'command': 'chown -R ${root_user}:${root_group} ${app_root}'}),
    ({'command': 'chown -R ${web_user}:${web_group} ${app_root}/nuxeo', 'check_ret': True}),
]

# Cfg chunks
SOURCE = """
source!%(src_num)d!env_inherited = 0
source!%(src_num)d!type = host
source!%(src_num)d!nick = Nuxeo-DM %(src_num)d
source!%(src_num)d!host = %(localhost)s:%(src_port)d
source!%(src_num)d!interpreter = %(root)s/nuxeo/bin/nuxeoctl start
source!%(src_num)d!type = interpreter
source!%(src_num)d!env_inherited = 1
source!%(src_num)d!timeout = 90
"""

CONFIG_VSERVER = SOURCE + """
%(pre_vsrv)s!nick = %(target_vserver)s
%(pre_vsrv)s!document_root = /dev/null

%(pre_vsrv)s!rule!2!match = directory
%(pre_vsrv)s!rule!2!match!directory = /nuxeo
%(pre_vsrv)s!rule!2!encoder!gzip = 1
%(pre_vsrv)s!rule!2!handler = proxy
%(pre_vsrv)s!rule!2!handler!balancer = round_robin
%(pre_vsrv)s!rule!2!handler!balancer!source!1 = %(src_num)d
%(pre_vsrv)s!rule!2!handler!in_allow_keepalive = 1
%(pre_vsrv)s!rule!2!handler!in_preserve_host = 1

%(pre_vsrv)s!rule!1!match = default
%(pre_vsrv)s!rule!1!handler = redir
%(pre_vsrv)s!rule!1!handler!rewrite!1!show = 1
%(pre_vsrv)s!rule!1!handler!rewrite!1!substring = /nuxeo
"""

CONFIG_DIR = SOURCE + """
%(pre_rule_plus1)s!match = directory
%(pre_rule_plus1)s!match!directory = /nuxeo
%(pre_rule_plus1)s!encoder!gzip = 1
%(pre_rule_plus1)s!handler = proxy
%(pre_rule_plus1)s!handler!balancer = round_robin
%(pre_rule_plus1)s!handler!balancer!source!1 = %(src_num)d
%(pre_rule_plus1)s!handler!in_allow_keepalive = 1
%(pre_rule_plus1)s!handler!in_preserve_host = 1
"""

CONFIG_DIR_REDIR = """
%(pre_rule_plus2)s!match = directory
%(pre_rule_plus2)s!match!directory = %(target_directory)s
%(pre_rule_plus2)s!handler = redir
%(pre_rule_plus2)s!handler!rewrite!1!show = 1
%(pre_rule_plus2)s!handler!rewrite!1!substring = /nuxeo
"""

URL_TARGET        = "/market/install/nuxeo-dm/config/target"
URL_SERVER_CONFIG = "/market/install/nuxeo-dm/config/server"
URL_ACCESS        = "/market/install/nuxeo-dm/access/user"

## Preconditions
class Precondition (Install_Stage):
    def __safe_call__ (self):
        box = CTK.Box()
        box += CTK.RawHTML ('<h1>%s</h1>' %(_("Checking for installation requirements")))

        if java.detect_java ('1.5', cache=False) or java.detect_java ('1.6', cache=False):
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

        notice  = CTK.Notice()
        notice += CTK.RawHTML('<p>%s</p>' %(_('Nuxeo can only be deployed under its default location /nuxeo.')))
        notice += CTK.RawHTML('<p>%s</p>' %(_('The appropriate redirection rule will be created if the specified web path or deployment method chosen should require this.')))
        box += notice

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
        src_port         = cfg_source_find_empty_port()
        localhost        = cfg_source_get_localhost_addr()

        # More replacements
        pre_rule = CTK.cfg.get_next_entry_prefix('%s!rule'%(pre_vsrv))
        props = cfg_get_surrounding_repls ('pre_rule', pre_rule)
        props.update (locals())
        tools.fix_server_port (root, src_port)

        # Apply the config
        if target_type == 'vserver':
            config = CONFIG_VSERVER %(props)
            CTK.cfg.apply_chunk (config)

        elif target_type == 'directory':
            config = CONFIG_DIR %(props)
            target_directory = target_directory.rstrip('/')
            if target_directory != '/nuxeo':
                config += CONFIG_DIR_REDIR %(props)

            CTK.cfg.apply_chunk (config)
            CTK.cfg.normalize ('%s!rule'%(pre_vsrv))

        # Pre-launch the application to save time
        tools.launch(root)

        # Proceed to access details
        box += CTK.RawHTML (js = CTK.DruidContent__JS_to_goto (box.id, URL_ACCESS))
        return box.Render().toStr()


## User details
class Access_Details (Install_Stage):
    def __safe_call__ (self):
        box = CTK.Box()
        box += CTK.RawHTML ('<h2>%s</h2>' %(_('Access details')))
        box += CTK.RawHTML ('<p>%s</p>' %(_('Nuxeo-DM has been installed, and Cherokee is configured to automatically launch it whenever the resource is accessed if it is not already available. A one-time pre-launch has been issued to save time.')))
        box += CTK.RawHTML ('<p>%s</p>' %(_('Note that launching Nuxeo-DM can take up a couple of  minutes on modern servers, so please be patient the first time you access it.')))
        box += CTK.RawHTML ('<p>%s</p>' %(_('It is probably a good idea to pre-launch it instead of having the web-server do so on demand.')))
        box += CTK.RawHTML ('<p>%s</p>' %(_('These are the default access details:')))

        notice  = CTK.Notice ()
        notice += CTK.RawHTML ('<b>%s:</b>' %(_('Username')))
        notice += CTK.Indenter (CTK.RawHTML ('Administrator'))
        notice += CTK.RawHTML ('<b>%s:</b>' %(_('Password')))
        notice += CTK.Indenter (CTK.RawHTML ('Administrator'))
        box += notice

        buttons = CTK.DruidButtonsPanel()
        buttons += CTK.DruidButton_Goto (_('Next'), market.Install.URL_INSTALL_DONE, do_submit=True)
        box += buttons

        return box.Render().toStr()


CTK.publish ('^%s$'%(market.Install.URL_INSTALL_SETUP_EXTERNAL), Precondition)
CTK.publish ('^%s$'%(URL_TARGET),        Target)
CTK.publish ('^%s$'%(URL_SERVER_CONFIG), Server_Config)
CTK.publish ('^%s$'%(URL_ACCESS),        Access_Details)
