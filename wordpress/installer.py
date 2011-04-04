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
from market.Install import Install_Stage
from Wizard import AddUsualStaticFiles

# Load required modules
php      = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "php.pyo"),    "php_util")
target   = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "target.pyo"), "target_util")
tools    = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "tools.pyo"),    "tools_util")
database = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "database.pyo"), "database_util")

# Messages
LANG_NOTE = N_("List of available languages")
LANG_H2   = N_("Deployment Language")
LANG_P1   = N_("Please, specify the deployment language for the application.")

# Languages
OPTS_LANG  = [
('ar', _('Arabic')),
('de', _('German')),
('en', _('English')),
('es', _('Spanish')),
('fr', _('French')),
('ja', _('Japanese')),
('pt', _('Portuguese')),
('ru', _('Russian')),
('zh', _('Chinese')),
]

# Ownership and permissions
POST_UNPACK_COMMANDS = [
    ({'command': 'chown -R ${root_user}:${root_group} ${app_root}'}),
    ({'command': 'chown -R ${web_user}:${web_group} ${app_root}/*'}),
]

# Cfg chunks
CONFIG_VSERVER = """
%(pre_vsrv)s!nick = %(target_vserver)s
%(pre_vsrv)s!document_root = %(root)s/wordpress
%(pre_vsrv)s!directory_index = index.php,index.html

# The PHP rule comes here

%(pre_rule_minus2)s!match = fullpath
%(pre_rule_minus2)s!match!fullpath!1 = /wp-admin
%(pre_rule_minus2)s!handler = redir
%(pre_rule_minus2)s!handler!rewrite!1!show = 0
%(pre_rule_minus2)s!handler!rewrite!1!substring = /wp-admin/

%(pre_rule_minus3)s!match = exists
%(pre_rule_minus3)s!match!iocache = 1
%(pre_rule_minus3)s!match!match_any = 1
%(pre_rule_minus3)s!match!match_only_files = 1
%(pre_rule_minus3)s!handler = common
%(pre_rule_minus3)s!handler!iocache = 1
%(pre_rule_minus3)s!handler = common
%(pre_rule_minus3)s!handler!allow_dirlist = 0

%(pre_vsrv)s!rule!1!match = default
%(pre_vsrv)s!rule!1!handler = redir
%(pre_vsrv)s!rule!1!handler!rewrite!1!show = 0
%(pre_vsrv)s!rule!1!handler!rewrite!1!regex = /?(.*)
%(pre_vsrv)s!rule!1!handler!rewrite!1!substring = /index.php?/$1
"""

CONFIG_DIR = """
%(pre_rule_plus1)s!match = directory
%(pre_rule_plus1)s!match!directory = %(target_directory)s
%(pre_rule_plus1)s!match!final = 0
%(pre_rule_plus1)s!document_root = %(root)s/wordpress

# The PHP rule comes here

%(pre_rule_minus1)s!match = fullpath
%(pre_rule_minus1)s!match!fullpath!1 = %(target_directory)s/wp-admin
%(pre_rule_minus1)s!handler = redir
%(pre_rule_minus1)s!handler!rewrite!10!show = 0
%(pre_rule_minus1)s!handler!rewrite!10!substring = %(target_directory)s/wp-admin/

%(pre_rule_minus3)s!match = and
%(pre_rule_minus3)s!match!final = 1
%(pre_rule_minus3)s!match!left = directory
%(pre_rule_minus3)s!match!left!directory = %(target_directory)s
%(pre_rule_minus3)s!match!right = exists
%(pre_rule_minus3)s!match!right!iocache = 1
%(pre_rule_minus3)s!match!right!match_any = 1
%(pre_rule_minus3)s!match!right!match_index_files = 1
%(pre_rule_minus3)s!match!right!match_only_files = 1
%(pre_rule_minus3)s!handler = common
%(pre_rule_minus3)s!handler!allow_dirlist = 0
%(pre_rule_minus3)s!handler!allow_pathinfo = 0
%(pre_rule_minus3)s!handler!iocache = 1

%(pre_rule_minus4)s!match = request
%(pre_rule_minus4)s!match!request = %(target_directory)s/?(.*)
%(pre_rule_minus4)s!handler = redir
%(pre_rule_minus4)s!handler!rewrite!1!show = 0
%(pre_rule_minus4)s!handler!rewrite!1!substring = %(target_directory)s/index.php?/$1
"""

URL_TARGET       = "/market/install/wordpress/target"
URL_DATABASE     = "/market/install/wordpress/database"
URL_SERVER       = "/market/install/wordpress/server"
URL_APPLY        = "/market/install/wordpress/apply"
URL_POST_INSTALL = "/market/install/wordpress/post_installation"

DB_SUPPORTED = ['mysql']


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

        box += CTK.RawHTML (js = CTK.DruidContent__JS_to_goto (box.id, URL_TARGET))
        return box.Render().toStr()


## Step 1: Target
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

## Step 2: PHP auto-configuration

## Step 3: Language
class Language (Install_Stage):
    def __safe_call__ (self):
        box = CTK.Box()
        pre  = "tmp!market!install"
        root = CTK.cfg.get_val ('%s!root' %(pre))
        path = os.path.join (root, 'wp-es')

        # If only default language present, skip stage
        if not os.path.isdir (path):
            box += CTK.RawHTML (js = CTK.DruidContent__JS_to_goto (box.id, URL_DATABASE))
            return box.Render().toStr()

        table = CTK.PropsTable()
        table.Add (_('Language'), CTK.ComboCfg('%s!wordpress!lang'%(pre), OPTS_LANG, {'class':'noauto', 'selected':'en'}), _(LANG_NOTE))

        submit  = CTK.Submitter (URL_APPLY)
        submit += table
        submit.bind ('submit_success', CTK.DruidContent__JS_to_goto (table.id, URL_DATABASE))

        buttons  = CTK.DruidButtonsPanel()
        buttons += CTK.DruidButton_Close(_('Cancel'))
        buttons += CTK.DruidButton_Submit (_('Next'), do_close=False)

        box  = CTK.Box()
        box += CTK.RawHTML ('<h2>%s</h2>'%(LANG_H2))
        box += CTK.RawHTML ('<p>%s</p>'  %(LANG_P1))
        box += submit
        box += buttons
        return box.Render().toStr()


## Step 4: Database selection
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


## Step 5: Server configuration
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
        deployment_lang  = CTK.cfg.get_val ('%s!wordpress!lang'      %(pre),'en')
        pre_vsrv         = 'vserver!%s' %(target_vserver_n)

        # PHP info
        php_info = php.get_info (pre_vsrv)

        # More replacements
        props = cfg_get_surrounding_repls ('pre_rule', php_info['rule'])
        props.update (locals())

        # Link correct language
        popen.popen_sync ('ln -fs %(root)s/wp-%(deployment_lang)s/wordpress %(root)s/wordpress' %(locals()))
        popen.popen_sync ('cp -r %(root)s/plugins/* %(root)s/wordpress/wp-content/plugins' %(locals()))

        # Provide DB details
        tools.configure_database (root)

        # Optional steps (if Cache module is present)
        if os.path.isfile (os.path.join (root, 'wp-cache-config.php')):
            tools.extend_sample_config_file (root)
            tools.move_cache_advanced (root)
            tools.move_cache_config (root)

        # Apply the config
        if target_type == 'vserver':
            config = CONFIG_VSERVER %(props)
            CTK.cfg.apply_chunk (config)
            AddUsualStaticFiles (props['pre_rule_plus1'], ['/favicon.ico','/crossdomain.xml'])
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
        commands = [({'command': 'chown -R ${php_user}:${php_group} ${app_root}/*'})]
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


CTK.publish ('^%s$'%(market.Install.URL_INSTALL_SETUP_EXTERNAL), Precondition)
CTK.publish ('^%s$'%(URL_TARGET),                                Target)
CTK.publish ('^%s$'%(php.URL_PHP_CONFIG_DONE),                   Language)
CTK.publish ('^%s$'%(URL_DATABASE),                              Database)
CTK.publish ('^%s$'%(URL_SERVER),                                Server)
CTK.publish ('^%s$'%(URL_POST_INSTALL),                          Post_Install)

# POST
CTK.publish ('^%s$'%(URL_APPLY), CTK.cfg_apply_post, method="POST")
