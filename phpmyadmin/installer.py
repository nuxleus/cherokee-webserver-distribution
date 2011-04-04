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
php      = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "php.pyo"),      "php_util")
target   = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "target.pyo"),   "target_util")
tools    = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "tools.pyo"),    "tools_util")
database = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "database.pyo"), "database_util")

# Ownership and permissions
POST_UNPACK_COMMANDS = [
    ({'command': 'chown -R ${root_user}:${root_group} ${app_root}'}),
    ({'command': 'mv ${app_root}/config.inc.php ${app_root}/phpMyAdmin'}),
    ({'command': 'mkdir ${app_root}/dir_upload && mkdir ${app_root}/dir_save'}),
    ({'command': 'chmod 755 ${app_root}/dir_* && chown ${web_user}:${web_group} ${app_root}/dir_*'}),
]

# Config chunks
CONFIG_VSERVER = """
%(pre_vsrv)s!nick = %(target_vserver)s
%(pre_vsrv)s!document_root = %(root)s/phpMyAdmin
%(pre_vsrv)s!directory_index = index.php,index.html

%(pre_rule_plus1)s!handler = custom_error
%(pre_rule_plus1)s!handler!error = 403
%(pre_rule_plus1)s!match = or
%(pre_rule_plus1)s!match!left = directory
%(pre_rule_plus1)s!match!left!directory = /libraries
%(pre_rule_plus1)s!match!right = directory
%(pre_rule_plus1)s!match!right!directory = /setup/lib

# IMPORTANT: The PHP rule comes here

%(pre_rule_minus1)s!handler = common
%(pre_rule_minus1)s!match = default
"""

CONFIG_DIR = """
%(pre_rule_plus2)s!handler = custom_error
%(pre_rule_plus2)s!handler!error = 403
%(pre_rule_plus2)s!match = or
%(pre_rule_plus2)s!match!left = directory
%(pre_rule_plus2)s!match!left!directory = %(target_directory)s/libraries
%(pre_rule_plus2)s!match!right = directory
%(pre_rule_plus2)s!match!right!directory = %(target_directory)s/setup/lib

%(pre_rule_plus1)s!document_root = %(root)s/phpMyAdmin
%(pre_rule_plus1)s!match = directory
%(pre_rule_plus1)s!match!directory = %(target_directory)s
%(pre_rule_plus1)s!match!final = 0

# IMPORTANT: The PHP rule comes here

%(pre_rule_minus1)s!document_root = %(root)s/phpMyAdmin
%(pre_rule_minus1)s!match = directory
%(pre_rule_minus1)s!match!directory = %(target_directory)s
%(pre_rule_minus1)s!handler = common
%(pre_rule_minus1)s!handler!allow_dirlist = 0
"""

URL_PRECONDITION = market.Install.URL_INSTALL_SETUP_EXTERNAL
URL_TARGET       = "/market/install/phpmyadmin/target"
URL_SERVER       = "/market/install/phpmyadmin/server"

DB_SUPPORTED = ['mysql']

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

        # PHP modules
        error = tools.check_modules()
        if error:
            note, instructions = error
            box += market.Util.InstructionBox (note, instructions, bin_path=php_cgi_bin)
            box += buttons
            return box.Render().toStr()

        # Database
        supported_dbs = database.get_supported_dbs (DB_SUPPORTED)
        if not supported_dbs:
            box += database.PreconditionError (DB_SUPPORTED)
            box += buttons
            return box.Render().toStr()

        # Next stage
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
        db_widget = database.MethodSelection (DB_SUPPORTED)
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

        # More replacements
        props = cfg_get_surrounding_repls ('pre_rule', php_info['rule'])
        props.update (locals())
        tools.perform_config_replacements (root)
        tools.create_pmadb (root)

        # Apply the config
        if target_type == 'vserver':
            config = CONFIG_VSERVER %(props)
            CTK.cfg.apply_chunk (config)
            AddUsualStaticFiles (props['pre_rule_plus2'])
            CTK.cfg.normalize ('%s!rule'%(pre_vsrv))

        elif target_type == 'directory':
            config = CONFIG_DIR %(props)
            CTK.cfg.apply_chunk (config)

        # Redirect to the Thanks page
        box += CTK.RawHTML (js = CTK.DruidContent__JS_to_goto (box.id, market.Install.URL_INSTALL_DONE))
        return box.Render().toStr()


CTK.publish ('^%s$'%(URL_PRECONDITION),        Precondition)
CTK.publish ('^%s$'%(URL_TARGET),              Target)
CTK.publish ('^%s$'%(php.URL_PHP_CONFIG_DONE), Database)
CTK.publish ('^%s$'%(URL_SERVER),              App_Config)
