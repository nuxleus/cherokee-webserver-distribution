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
php_mods = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "php-mods.pyo"), "php_mods_util")
target   = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "target.pyo"),   "target_util")
tools    = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "tools.pyo"),    "tools_util")
database = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "database.pyo"), "database_util")

# Ownership and permissions
POST_UNPACK_COMMANDS = [
    ({'command': 'chown -R ${root_user}:${root_group} ${app_root}'}),
    ({'command': 'chown ${web_user} ${app_root}/phpBB3'}), # Needed to move install within PHP
]

# Cfg chunks
CONFIG_VSERVER = """
%(pre_vsrv)s!nick = %(target_vserver)s
%(pre_vsrv)s!document_root = %(root)s/phpBB3
%(pre_vsrv)s!directory_index = index.php,index.html

%(pre_rule_plus1)s!handler = custom_error
%(pre_rule_plus1)s!handler!error = 403
%(pre_rule_plus1)s!match = request
%(pre_rule_plus1)s!match!request = /(config.php|common.php|cache/.*|files/.*|images/avatars/upload/.*|store/.*)

# The PHP rule comes here

%(pre_rule_minus1)s!handler = common
%(pre_rule_minus1)s!handler!iocache = 0
%(pre_rule_minus1)s!match = default
"""

CONFIG_DIR = """
%(pre_rule_plus2)s!handler = custom_error
%(pre_rule_plus2)s!handler!error = 403
%(pre_rule_plus2)s!match = request
%(pre_rule_plus2)s!match!request = ^%(target_directory)s/(config.php|common.php|cache/.*|files/.*|images/avatars/upload/.*|store/.*)

%(pre_rule_plus1)s!document_root = %(root)s/phpBB3
%(pre_rule_plus1)s!match = directory
%(pre_rule_plus1)s!match!directory = %(target_directory)s
%(pre_rule_plus1)s!match!final = 0

# The PHP rule comes here

%(pre_rule_minus1)s!document_root = %(root)s/phpBB3
%(pre_rule_minus1)s!match = directory
%(pre_rule_minus1)s!match!directory = %(target_directory)s
%(pre_rule_minus1)s!handler = common
%(pre_rule_minus1)s!handler!iocache = 0
"""

URL_PRECONDITION = market.Install.URL_INSTALL_SETUP_EXTERNAL
URL_TARGET       = "/market/install/phpbb/target"
URL_DATABASE     = php.URL_PHP_CONFIG_DONE
URL_SERVER       = "/market/install/phpbb/server"
URL_POST_INSTALL = "/market/install/phpbb/post_installation"

DB_SUPPORTED = ['mysql', 'postgresql', 'oracle', 'sqlserver']

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

        # Database
        supported_dbs = database.get_supported_dbs (DB_SUPPORTED)
        if not supported_dbs:
            box += database.PreconditionError (DB_SUPPORTED)
            box += buttons
            return box.Render().toStr()

        # PHP Modules
        error = tools.check_modules()
        if error:
            note, instructions = error
            box += market.Util.InstructionBox (note, instructions, bin_path=php_cgi_bin)
            box += buttons
            return box.Render().toStr()

        # Check at least one DB module is available
        db_errors = tools.check_database_support()
        if db_errors:
            php_cgi_bin = php.figure_phpcgi_binary()

            note, instruction_list = db_errors
            box += market.Util.InstructionBox (note, instruction_list, bin_path=php_cgi_bin)
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

        # More replacements
        props = cfg_get_surrounding_repls ('pre_rule', php_info['rule'])
        props.update (locals())

        # Write cfg file
        tools.patch_phpbb_installer()

        # Apply the config
        if target_type == 'vserver':
            config = CONFIG_VSERVER %(props)
            CTK.cfg.apply_chunk (config)
            AddUsualStaticFiles (props['pre_rule_plus2'])
            CTK.cfg.normalize ('%s!rule'%(pre_vsrv))

        elif target_type == 'directory':
            config = CONFIG_DIR %(props)
            CTK.cfg.apply_chunk (config)

       # Redirect to post installation
        box += CTK.RawHTML (js = CTK.DruidContent__JS_to_goto (box.id, URL_POST_INSTALL))
        return box.Render().toStr()


## Post installation: Redirect to the Thanks page if successfull
class Post_Install (Install_Stage):
    def __safe_call__ (self):
        vserver_n    = CTK.cfg.get_val ('%s!target!vserver_n' %('tmp!market!install'))
        pre_vsrv     = 'vserver!%s' %(vserver_n)
        replacements = php.figure_php_user(pre_vsrv)

        market.Install_Log.log ("Post installation commands")
        commands = [
            ({'command': 'chown -R ${php_user}:${php_group} ${app_root}/phpBB3/files'}),
            ({'command': 'chown -R ${php_user}:${php_group} ${app_root}/phpBB3/store'}),
            ({'command': 'chown -R ${php_user}:${php_group} ${app_root}/phpBB3/cache'}),
            ({'command': 'chown -R ${php_user}:${php_group} ${app_root}/phpBB3/images/avatars/upload'}),
            ({'command': 'chown -R ${php_user}:${php_group} ${app_root}/phpBB3/config.php'}),
        ]

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


CTK.publish ('^%s$'%(URL_PRECONDITION), Precondition)
CTK.publish ('^%s$'%(URL_TARGET),       Target)
CTK.publish ('^%s$'%(URL_DATABASE),     Database)
CTK.publish ('^%s$'%(URL_SERVER),       App_Config)
CTK.publish ('^%s$'%(URL_POST_INSTALL), Post_Install)
