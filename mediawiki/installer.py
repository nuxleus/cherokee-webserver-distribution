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
    ({'command': 'mkdir ${app_root}/data'}),
    ({'command': 'chmod u+w ${app_root}/mediawiki/config'}),
]

# Cfg chunks
CONFIG_DIR = """
%(pre_rule_plus3)s!document_root = %(root)s/mediawiki
%(pre_rule_plus3)s!match = directory
%(pre_rule_plus3)s!match!directory = %(script_path)s
%(pre_rule_plus3)s!match!final = 0

%(pre_rule_plus2)s!handler = redir
%(pre_rule_plus2)s!handler!rewrite!1!show = 1
%(pre_rule_plus2)s!handler!rewrite!1!substring = %(script_path)s/index.php
%(pre_rule_plus2)s!match = fullpath
%(pre_rule_plus2)s!match!fullpath!1 = %(target_directory)s
%(pre_rule_plus2)s!match!fullpath!2 = %(target_directory)s/

%(pre_rule_plus1)s!handler = redir
%(pre_rule_plus1)s!handler!rewrite!1!show = 0
%(pre_rule_plus1)s!handler!rewrite!1!substring = %(script_path)s/index.php?/$1
%(pre_rule_plus1)s!match = request
%(pre_rule_plus1)s!match!request = %(target_directory)s/(.+)

# The PHP rule comes here
"""

CONFIG_VSERVER = """
%(pre_vsrv)s!nick = %(target_vserver)s
%(pre_vsrv)s!document_root = %(root)s/mediawiki
%(pre_vsrv)s!directory_index = index.php,index.html

%(pre_rule_plus3)s!document_root = %(root)s/mediawiki
%(pre_rule_plus3)s!match = directory
%(pre_rule_plus3)s!match!directory = %(script_path)s
%(pre_rule_plus3)s!match!final = 0

%(pre_rule_plus2)s!handler = redir
%(pre_rule_plus2)s!handler!rewrite!1!show = 1
%(pre_rule_plus2)s!handler!rewrite!1!substring = %(script_path)s/index.php
%(pre_rule_plus2)s!match = fullpath
%(pre_rule_plus2)s!match!fullpath!1 = %(target_directory)s
%(pre_rule_plus2)s!match!fullpath!2 = %(target_directory)s/

%(pre_rule_plus1)s!handler = redir
%(pre_rule_plus1)s!handler!rewrite!1!show = 0
%(pre_rule_plus1)s!handler!rewrite!1!substring = %(script_path)s/index.php?/$1
%(pre_rule_plus1)s!match = request
%(pre_rule_plus1)s!match!request = %(target_directory)s/(.+)

# The PHP rule comes here

%(pre_vsrv)s!rule!1!match = default
%(pre_vsrv)s!rule!1!handler = common
"""

LOCAL_SETTINGS = """
$wgScriptPath       = "%(script_path)s";
$wgScript           = "$wgScriptPath/index.php";
$wgRedirectScript   = "$wgScriptPath/redirect.php";
$wgArticlePath      = "%(target_directory)s/$1";
$wgUsePathInfo      = true;
"""

ROBOTS_TXT = """
User-agent: *
Disallow: %(script_path)s/
Disallow: %(target_directory)s/Special:Search
Disallow: %(target_directory)s/Special:Random
"""

URL_PRECONDITION = market.Install.URL_INSTALL_SETUP_EXTERNAL
URL_TARGET       = "/market/install/mediawiki/target"
URL_SERVER       = php.URL_PHP_CONFIG_DONE
URL_POST_INSTALL = "/market/install/mediawiki/post_installation"


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

## Step 2: PHP auto-configuration

## Step 3: App configuration
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
        target_directory = CTK.cfg.get_val ('%s!target!directory'    %(pre), '/wiki')
        pre_vsrv         = 'vserver!%s' %(target_vserver_n)
        script_path      = ['/w', '/wiki'][target_directory in ['/w', '/w/']]

        # PHP info
        php_info = php.get_info (pre_vsrv)

        # More replacements
        props = cfg_get_surrounding_repls ('pre_rule', php_info['rule'])
        props.update (locals())

        # Write auxiliary files
        try:
            f = open (os.path.join (root, 'mediawiki','config','LocalSettings.inc'), 'w+')
            f.write (LOCAL_SETTINGS %(locals()))
            market.Install_Log.log ("Success: LocalSettings.inc written.")
        except:
            market.Install_Log.log ("Error: LocalSettings.inc not written.")
            raise

        try:
            f = open (os.path.join(root, 'mediawiki', 'robots.txt'), 'w+')
            f.write (ROBOTS_TXT %(locals()))
            market.Install_Log.log ("Success: robots.txt written")
        except:
            market.Install_Log.log ("Error: robots.txt not written")
            raise

        # Apply the config
        if target_type == 'vserver':
            config = CONFIG_VSERVER%(props)
            AddUsualStaticFiles (props['pre_rule_minus1'])
            CTK.cfg.apply_chunk (config)

        elif target_type == 'directory':
            config = CONFIG_DIR %(props)
            CTK.cfg.apply_chunk (config)
            CTK.cfg.normalize ('%s!rule'%(pre_vsrv))

        # Redirect to post installation
        box += CTK.RawHTML (js = CTK.DruidContent__JS_to_goto (box.id, URL_POST_INSTALL))
        return box.Render().toStr()


## Post installation: Redirect to the Thanks if successfull
class Post_Install (Install_Stage):
    def __safe_call__ (self):
        vserver_n    = CTK.cfg.get_val ('%s!target!vserver_n' %('tmp!market!install'))
        pre_vsrv     = 'vserver!%s' %(vserver_n)
        replacements = php.figure_php_user(pre_vsrv)

        market.Install_Log.log ("Post installation commands")
        commands = [({'command': 'chown -R ${php_user}:${php_group} ${app_root}/mediawiki'}),
                    ({'command': 'chown -R ${php_user}:${php_group} ${app_root}/data'}),]
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
CTK.publish ('^%s$'%(URL_SERVER),       App_Config)
CTK.publish ('^%s$'%(URL_POST_INSTALL), Post_Install)
