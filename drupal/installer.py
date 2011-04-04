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
import shutil
import pwd
import grp
import stat

import CTK
import market

from util import *
from market.Install import Install_Stage

# Load modules
php      = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "php.pyo"),      "php_util")
php_mods = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "php-mods.pyo"), "php_mods_util")
target   = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "target.pyo"),   "target_util")
tools    = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "tools.pyo"),    "tools_util")
database = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "database.pyo"), "database_util")

# Common commands for all Drupal installers
POST_UNPACK_COMMANDS = [
    ({'command': 'rm -rf ${app_root}/drupal/STATUS.*.txt'}),
    ({'command': 'cp ${app_root}/drupal/sites/default/default.settings.php ${app_root}/drupal/sites/default/settings.php'}),
    ({'command': 'chmod 750 ${app_root}/drupal/sites/default/settings.php'}),
    ({'command': 'chown -R ${root_user}:${root_group} ${app_root}'}),
    ({'command': 'chown -R ${web_user}:${web_group} ${app_root}/drupal'}),
]

# Cfg chunks
CONFIG_VSERVER = """
%(pre_vsrv)s!nick = %(target_vserver)s
%(pre_vsrv)s!document_root = %(root)s/drupal
%(pre_vsrv)s!directory_index = index.php,index.html

%(pre_rule_plus3)s!match = request
%(pre_rule_plus3)s!match!request = ^/([0-9]+)$
%(pre_rule_plus3)s!handler = redir
%(pre_rule_plus3)s!handler!rewrite!1!regex = ^/([0-9]+)$
%(pre_rule_plus3)s!handler!rewrite!1!show = 0
%(pre_rule_plus3)s!handler!rewrite!1!substring = /index.php?q=/node/$1

%(pre_rule_plus2)s!match = request
%(pre_rule_plus2)s!match!request = \.(engine|inc|info|install|module|profile|test|po|sh|.*sql|theme|tpl(\.php)?|xtmpl|svn-base)$|^(code-style\.pl|Entries.*|Repository|Root|Tag|Template|all-wcprops|entries|format)$
%(pre_rule_plus2)s!handler = custom_error
%(pre_rule_plus2)s!handler!error = 403

%(pre_rule_plus1)s!match = fullpath
%(pre_rule_plus1)s!match!fullpath!1 = /
%(pre_rule_plus1)s!handler = redir
%(pre_rule_plus1)s!handler!rewrite!1!show = 0
%(pre_rule_plus1)s!handler!rewrite!1!substring = /index.php

# IMPORTANT: The PHP rule comes here

%(pre_rule_minus1)s!match = exists
%(pre_rule_minus1)s!match!iocache = 1
%(pre_rule_minus1)s!match!match_any = 1
%(pre_rule_minus1)s!match!match_index_files = 0
%(pre_rule_minus1)s!match!match_only_files = 1
%(pre_rule_minus1)s!handler = file

%(pre_rule_minus2)s!match = default
%(pre_rule_minus2)s!handler = redir
%(pre_rule_minus2)s!handler!rewrite!1!show = 0
%(pre_rule_minus2)s!handler!rewrite!1!regex = ^/(.*)\?(.*)$
%(pre_rule_minus2)s!handler!rewrite!1!substring = /index.php?q=$1&$2
%(pre_rule_minus2)s!handler!rewrite!2!show = 0
%(pre_rule_minus2)s!handler!rewrite!2!regex = ^/(.*)$
%(pre_rule_minus2)s!handler!rewrite!2!substring = /index.php?q=$1
"""

CONFIG_DIR = """
%(pre_rule_plus4)s!match = request
%(pre_rule_plus4)s!match!request = ^%(target_directory)s/([0-9]+)$
%(pre_rule_plus4)s!handler = redir
%(pre_rule_plus4)s!handler!rewrite!1!regex = ^%(target_directory)s/([0-9]+)$
%(pre_rule_plus4)s!handler!rewrite!1!show = 0
%(pre_rule_plus4)s!handler!rewrite!1!substring = %(target_directory)s/index.php?q=/node/$1

%(pre_rule_plus3)s!match = request
%(pre_rule_plus3)s!match!request = %(target_directory)s/$
%(pre_rule_plus3)s!handler = redir
%(pre_rule_plus3)s!handler!rewrite!1!show = 0
%(pre_rule_plus3)s!handler!rewrite!1!substring = %(target_directory)s/index.php

%(pre_rule_plus2)s!match = directory
%(pre_rule_plus2)s!match!directory = %(target_directory)s
%(pre_rule_plus2)s!match!final = 0
%(pre_rule_plus2)s!document_root = %(root)s/drupal

%(pre_rule_plus1)s!match = and
%(pre_rule_plus1)s!match!left = directory
%(pre_rule_plus1)s!match!left!directory = %(target_directory)s
%(pre_rule_plus1)s!match!right = request
%(pre_rule_plus1)s!match!right!request = \.(engine|inc|info|install|module|profile|test|po|sh|.*sql|theme|tpl(\.php)?|xtmpl|svn-base)$|^(code-style\.pl|Entries.*|Repository|Root|Tag|Template|all-wcprops|entries|format)$
%(pre_rule_plus1)s!handler = custom_error
%(pre_rule_plus1)s!handler!error = 403

# IMPORTANT: The PHP rule comes here

%(pre_rule_minus1)s!match = and
%(pre_rule_minus1)s!match!left = directory
%(pre_rule_minus1)s!match!left!directory = %(target_directory)s
%(pre_rule_minus1)s!match!right = exists
%(pre_rule_minus1)s!match!right!iocache = 1
%(pre_rule_minus1)s!match!right!match_any = 1
%(pre_rule_minus1)s!match!right!match_index_files = 0
%(pre_rule_minus1)s!match!right!match_only_files = 1
%(pre_rule_minus1)s!handler = file

%(pre_rule_minus2)s!match = directory
%(pre_rule_minus2)s!match!directory = %(target_directory)s
%(pre_rule_minus2)s!handler = redir
%(pre_rule_minus2)s!handler!rewrite!1!show = 0
%(pre_rule_minus2)s!handler!rewrite!1!regex = ^/(.*)\?(.*)$
%(pre_rule_minus2)s!handler!rewrite!1!substring = %(target_directory)s/index.php?q=$1&$2
%(pre_rule_minus2)s!handler!rewrite!2!show = 0
%(pre_rule_minus2)s!handler!rewrite!2!regex = ^/(.*)$
%(pre_rule_minus2)s!handler!rewrite!2!substring = %(target_directory)s/index.php?q=$1
"""

URL_PRECONDITION = market.Install.URL_INSTALL_SETUP_EXTERNAL
URL_TARGET       = "/market/install/drupal/target"
URL_DATABASE     = php.URL_PHP_CONFIG_DONE
URL_SERVER       = "/market/install/drupal/server"
URL_POST_INSTALL = "/market/install/drupal/post_installation"

DB_SUPPORTED = ['mysql', 'postgresql']


## Preconditions
class Precondition (Install_Stage):
    def __safe_call__ (self):
        box = CTK.Box()
        box += CTK.RawHTML ('<h2>%s</h2>' %(_("Checking Requirements")))

        buttons = CTK.DruidButtonsPanel()
        buttons += CTK.DruidButton_Close(_('Cancel'))
        buttons += CTK.DruidButton_Goto (_('Retry'), URL_PRECONDITION, do_submit=True)

        # Check PHP
        php_cgi_bin = php.figure_phpcgi_binary()

        if not php_cgi_bin:
            box += php.PHP_Interpreter_Not_Found_Widget()
            box += buttons
            return box.Render().toStr()

        # Check at least one php DB module is available
        db_errors = tools.check_php_database_support()
        if db_errors:
            note, instruction_list = db_errors

            box += market.Util.InstructionBox (note, instruction_list, bin_path=php_cgi_bin)
            box += buttons
            return box.Render().toStr()

        # Database
        supported_dbs = database.get_supported_dbs (DB_SUPPORTED)
        if not supported_dbs:
            box += database.PreconditionError (DB_SUPPORTED)
            box += buttons
            return box.Render().toStr()

        box += CTK.RawHTML (js = CTK.DruidContent__JS_to_goto (box.id, URL_TARGET))
        return box.Render().toStr()


## Target selection
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

## Database selection
class Database (Install_Stage):
    def __safe_call__ (self):
        box = CTK.Box()
        php_db_modules = php_mods.supported_db_modules (DB_SUPPORTED)
        db_widget = database.MethodSelection (php_db_modules)
        db_widget.bind ('goto_next_stage', CTK.DruidContent__JS_to_goto (box.id, URL_SERVER))
        box += db_widget

        buttons = CTK.DruidButtonsPanel()
        buttons += CTK.DruidButton_Close(_('Cancel'))
        buttons += CTK.DruidButton_Submit (_('Next'), do_close=False)
        box += buttons

        return box.Render().toStr()


## App configuration
class App_Config (Install_Stage):
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

        # Fixes Drupal bug for multilingual content
        CTK.cfg['%s!encoder!gzip' %(php_info['rule'])] = '0'

        # More replacements
        props = cfg_get_surrounding_repls ('pre_rule', php_info['rule'])
        props.update (locals())
        tools.preload_installer (root)

        # Apply the config
        if target_type == 'vserver':
            config = CONFIG_VSERVER %(props)
            CTK.cfg.apply_chunk (config)

        elif target_type == 'directory':
            config = CONFIG_DIR %(props)
            CTK.cfg.apply_chunk (config)
            CTK.cfg.normalize ('%s!rule'%(pre_vsrv))

        # Redirect to post installation, and from there to Thanks page
        box += CTK.RawHTML (js = CTK.DruidContent__JS_to_goto (box.id, URL_POST_INSTALL))
        return box.Render().toStr()


## Post installation: Redirect to the Thanks if successfull
class Post_Install (Install_Stage):
    def __safe_call__ (self):
        vserver_n    = CTK.cfg.get_val ('%s!target!vserver_n' %('tmp!market!install'))
        pre_vsrv     = 'vserver!%s' %(vserver_n)
        replacements = php.figure_php_user(pre_vsrv)

        market.Install_Log.log ("Post installation commands")
        commands = [({'command': 'chown -R ${php_user}:${php_group} ${app_root}/drupal'}),]
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
CTK.publish ('^%s$'%(URL_DATABASE),            Database)
CTK.publish ('^%s$'%(URL_SERVER),              App_Config)
CTK.publish ('^%s$'%(URL_POST_INSTALL),        Post_Install)
