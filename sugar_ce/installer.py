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

from util import *
from market.Install import Install_Stage
from Wizard import AddUsualStaticFiles

# Load required modules
php    = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "php.pyo"),    "php_util")
target = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "target.pyo"), "target_util")

# Ownership and permissions
POST_UNPACK_COMMANDS = [
    ({'command': 'chown -R ${root_user}:${root_group} ${app_root}'}),
]

# Config chunks
CONFIG_VSERVER = """
%(pre_vsrv)s!nick = %(target_vserver)s
%(pre_vsrv)s!document_root = %(root)s/sugar
%(pre_vsrv)s!directory_index = index.php,index.html

%(pre_rule_plus3)s!handler = redir
%(pre_rule_plus3)s!handler!rewrite!1!show = 1
%(pre_rule_plus3)s!handler!rewrite!1!substring = /index.php
%(pre_rule_plus3)s!match = request
%(pre_rule_plus3)s!match!request = ^/.*/.*\.php

%(pre_rule_plus2)s!handler = redir
%(pre_rule_plus2)s!handler!rewrite!1!show = 1
%(pre_rule_plus2)s!handler!rewrite!1!substring = /index.php
%(pre_rule_plus2)s!match = request
%(pre_rule_plus2)s!match!request = emailmandelivery.php

%(pre_rule_plus1)s!handler = redir
%(pre_rule_plus1)s!handler!rewrite!1!show = 0
%(pre_rule_plus1)s!handler!rewrite!1!substring = /log_file_restricted.html
%(pre_rule_plus1)s!match = request
%(pre_rule_plus1)s!match!request = ^/(.*\.log.*|not_imported_.*txt)

# The PHP rule comes here

%(pre_rule_minus1)s!handler = common
%(pre_rule_minus1)s!handler!iocache = 0
%(pre_rule_minus1)s!match = default
"""

CONFIG_DIR = """
%(pre_rule_plus1)s!document_root = %(root)s/sugar
%(pre_rule_plus1)s!match = directory
%(pre_rule_plus1)s!match!directory = %(target_directory)s
%(pre_rule_plus1)s!match!final = 0

# The PHP rule comes here

%(pre_rule_minus1)s!handler = redir
%(pre_rule_minus1)s!handler!rewrite!1!show = 1
%(pre_rule_minus1)s!handler!rewrite!1!substring = %(target_directory)s/index.php
%(pre_rule_minus1)s!match = fullpath
%(pre_rule_minus1)s!match!final = 1
%(pre_rule_minus1)s!match!fullpath!1 = %(target_directory)s/emailmandelivery.php
%(pre_rule_minus1)s!match!request = emailmandelivery.php

%(pre_rule_minus2)s!handler = redir
%(pre_rule_minus2)s!handler!rewrite!1!show = 0
%(pre_rule_minus2)s!handler!rewrite!1!substring = %(target_directory)s/log_file_restricted.html
%(pre_rule_minus2)s!match = request
%(pre_rule_minus2)s!match!request = ^%(target_directory)s/(.*\.log.*|not_imported_.*txt)

%(pre_rule_minus3)s!handler = redir
%(pre_rule_minus3)s!handler!rewrite!1!show = 1
%(pre_rule_minus3)s!handler!rewrite!1!substring = %(target_directory)s/index.php
%(pre_rule_minus3)s!match = request
%(pre_rule_minus3)s!match!request = ^%(target_directory)s/.*/.*\.php

%(pre_rule_minus4)s!handler = common
%(pre_rule_minus4)s!handler!allow_dirlist = 0
%(pre_rule_minus4)s!handler!allow_pathinfo = 1
%(pre_rule_minus4)s!match = directory
%(pre_rule_minus4)s!match!directory = %(target_directory)s
"""

URL_PRECONDITION = market.Install.URL_INSTALL_SETUP_EXTERNAL
URL_TARGET       = "/market/install/sugar/target"
URL_POST_INSTALL = "/market/install/post_installation"


## Preconditions
class Precondition (Install_Stage):
    def __safe_call__ (self):
        box = CTK.Box()
        box += CTK.RawHTML ('<h2>%s</h2>' %(_("Checking Requirements")))

        buttons = CTK.DruidButtonsPanel()
        buttons += CTK.DruidButton_Close(_('Cancel'))
        buttons += CTK.DruidButton_Goto (_('Retry'), market.Install.URL_INSTALL_SETUP_EXTERNAL, do_submit=True)

        # Check PHP
        php_cgi_bin = php.figure_phpcgi_binary()

        if not php_cgi_bin:
            box += php.PHP_Interpreter_Not_Found_Widget()
            box += buttons
            return box.Render().toStr()

        box += CTK.RawHTML (js = CTK.DruidContent__JS_to_goto (box.id, URL_TARGET))
        return box.Render().toStr()

## Target
class Target (Install_Stage):
    def __safe_call__ (self):
        box = CTK.Box()
        target_wid = target.TargetSelection()
        target_wid.bind ('goto_next_stage', CTK.DruidContent__JS_to_goto (box.id, php.URL_PHP_CONFIG_INTRO))
        box += target_wid

        buttons = CTK.DruidButtonsPanel()
        buttons += CTK.DruidButton_Close(_('Cancel'))
        buttons += CTK.DruidButton_Submit (_('Next'), do_close=False)
        box += buttons

        return box.Render().toStr()

## PHP auto-configuration

## App configuration
class Server (Install_Stage):
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

        # PHP info
        php_info = php.get_info (pre_vsrv)

        # More replacements
        props = cfg_get_surrounding_repls ('pre_rule', php_info['rule'])
        props.update (locals())

        # Apply the config
        if target_type == 'vserver':
            config = CONFIG_VSERVER %(props)
            CTK.cfg.apply_chunk (config)
            AddUsualStaticFiles (props['pre_rule_plus4'])
            CTK.cfg.normalize ('%s!rule'%(pre_vsrv))

        elif target_type == 'directory':
            config = CONFIG_DIR %(props)
            CTK.cfg.apply_chunk (config)

        box += CTK.RawHTML (js = CTK.DruidContent__JS_to_goto (box.id, URL_POST_INSTALL))
        return box.Render().toStr()


## Post installation: Redirect to the Thanks page if successfull
class Post_Install (Install_Stage):
    def __safe_call__ (self):
        vserver_n    = CTK.cfg.get_val ('%s!target!vserver_n' %('tmp!market!install'))
        pre_vsrv     = 'vserver!%s' %(vserver_n)
        replacements = php.figure_php_user(pre_vsrv)

        market.Install_Log.log ("Post installation commands")
        commands = [({'command': 'chown -R ${php_user}:${php_group} ${app_root}/sugar'})]
        progress = market.CommandProgress.CommandProgress (commands, market.Install.URL_INSTALL_DONE)

        progress['php_user']  = replacements['php_user']
        progress['php_group'] = replacements['php_group']

        box = CTK.Box()
        box += CTK.RawHTML ('<h2>%s</h2>' %(_('Performing adjustments')))
        box += CTK.RawHTML ('<p>%s</p>'   %(_('This process may take a while. Please, hold on.')))
        box += progress

        buttons = CTK.DruidButtonsPanel()
        buttons += CTK.DruidButton_Close(_('Cancel'))
        box += buttons

        return box.Render().toStr()


CTK.publish ('^%s$'%(URL_PRECONDITION),        Precondition)
CTK.publish ('^%s$'%(URL_TARGET),              Target)
CTK.publish ('^%s$'%(php.URL_PHP_CONFIG_DONE), Server)
CTK.publish ('^%s$'%(URL_POST_INSTALL),        Post_Install)

