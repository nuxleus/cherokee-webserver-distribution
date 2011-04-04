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
import string
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
    ({'command': 'mkdir ${app_root}/moodledata'}),
    ({'command': 'chown -R ${root_user}:${root_group} ${app_root}'}),
    ({'command': 'chown -R ${web_user}:${web_group} ${app_root}/moodle ${app_root}/moodledata'}),
]

# Config chunks
CONFIG_VSERVER = """
%(pre_vsrv)s!nick = %(target_vserver)s
%(pre_vsrv)s!document_root = %(root)s/moodle
%(pre_vsrv)s!directory_index = index.php,index.html

# IMPORTANT: The PHP rule comes here

%(pre_rule_minus1)s!match = default
%(pre_rule_minus1)s!handler!allow_pathinfo = 1
%(pre_rule_minus1)s!handler = common
%(pre_rule_minus1)s!handler!iocache = 0
"""

CONFIG_DIR = """
%(pre_rule_plus1)s!document_root = %(root)s/moodle
%(pre_rule_plus1)s!match = directory
%(pre_rule_plus1)s!match!directory = %(target_directory)s
%(pre_rule_plus1)s!match!final = 0

# IMPORTANT: The PHP rule comes here

%(pre_rule_minus1)s!match = directory
%(pre_rule_minus1)s!match!directory = %(target_directory)s
%(pre_rule_minus1)s!handler = common
%(pre_rule_minus1)s!handler!allow_pathinfo = 1
%(pre_rule_minus1)s!document_root = %(root)s/moodle
"""

URL_PRECONDITION  = market.Install.URL_INSTALL_SETUP_EXTERNAL
URL_TARGET        = "/market/install/moodle/target"
URL_DATABASE      = php.URL_PHP_CONFIG_DONE
URL_DETAILS       = "/market/install/moodle/details"
URL_SERVER        = "/market/install/moodle/server"
URL_POST_INSTALL  = "/market/install/moodle/post_installation"
URL_DETAILS_APPLY = "/market/install/moodle/apply"

NOTE_ADMINUSER  = N_('Username for the administrator account. Only lower case allowed.')
NOTE_ADMINPASS  = N_('Password for the administrator account. At least 8 mixed-case alphanumeric and non-alphanumeric characters required.')
NOTE_FULLNAME   = N_('Full name of the website.')
NOTE_SHORTNAME  = N_('Short name of the website.')
NOTE_DOMAINNAME = N_('Domain name under which the virtual server can be accessed from the Internet, such as example.com for instance.')

DETAILS_H2     = N_('Site details')
DETAILS_P1     = N_('The installation needs to configure the following settings.')

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

        # Check general modules
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

        # Check at least one DB module is available
        db_errors = tools.check_database_support()
        if db_errors:
            php_cgi_bin = php.figure_phpcgi_binary()

            note, instruction_list = db_errors
            box += market.Util.InstructionBox (note, instruction_list, bin_path=php_cgi_bin)
            box += buttons
            return box.Render().toStr()

        # Check PHP settings
        setting_errors = tools.check_settings()
        if setting_errors:
            box += CTK.RawHTML('<p>%s</p>' %(_("Some of your PHP settings do not meet Moodle's requirements. Please edit your PHP configuration files and try again.")))
            table = CTK.Table({'class':'infosection'})
            table.set_header(1)
            table += [CTK.RawHTML(x) for x in ('%s '%_('Setting'), '%s '%_('Expected value'), _('Current value'))]
            for setting_test in setting_errors:
                table += [CTK.RawHTML(str(x)) for x in setting_test]

            box += CTK.Indenter (table)
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

## Database selection
class Database (Install_Stage):
    def __safe_call__ (self):
        box = CTK.Box()
        php_db_modules = php_mods.supported_db_modules (DB_SUPPORTED)
        db_widget  = database.MethodSelection (php_db_modules)
        db_widget.bind ('goto_next_stage', CTK.DruidContent__JS_to_goto (box.id, URL_DETAILS))
        box += db_widget

        buttons = CTK.DruidButtonsPanel()
        buttons += CTK.DruidButton_Close(_('Cancel'))
        buttons += CTK.DruidButton_Submit (_('Next'), do_close=False)
        box += buttons

        return box.Render().toStr()


## Final site details
class Site_Details (Install_Stage):
    VALIDATION = [
        ('tmp!market!install!moodle!agreement', tools.validate_agreement),
        ('tmp!market!install!moodle!adminuser', tools.validate_username),
        ('tmp!market!install!moodle!adminpass', tools.validate_password),
        ('tmp!market!install!moodle!agreement', tools.validate_agreement),
        ('tmp!market!install!moodle!domain',    tools.validate_domain),
    ]

    def __safe_call__ (self):
        box = CTK.Box()
        pre = "tmp!market!install"

        submit = CTK.Submitter (URL_DETAILS_APPLY)
        table  = CTK.PropsTable()

        table.Add (_('Admin user'), CTK.TextCfg ('%s!moodle!adminuser'%(pre), False, {'class':'required'}),     _(NOTE_ADMINUSER))
        table.Add (_('Admin password'), CTK.TextCfg ('%s!moodle!adminpass'%(pre), False, {'class':'required'}), _(NOTE_ADMINPASS))
        table.Add (_('Full sitename'), CTK.TextCfg ('%s!moodle!fullname'%(pre), False, {'class':'required'}),   _(NOTE_FULLNAME))
        table.Add (_('Short sitename'), CTK.TextCfg ('%s!moodle!shortname'%(pre), False, {'class':'required'}), _(NOTE_SHORTNAME))

        target_type      = CTK.cfg.get_val ('%s!target'           %(pre))
        if target_type == 'directory':
            target_vserver_n = CTK.cfg.get_val ('%s!target!vserver_n' %(pre))
            pre_vsrv         = 'vserver!%s' %(target_vserver_n)
            vserver_nick     = CTK.cfg.get_val ('%s!nick'  %(pre_vsrv))
            vserver_match    = CTK.cfg.get_val ('%s!match' %(pre_vsrv), 'name')
            if vserver_match == 'name' and vserver_nick != 'default':
                submit += CTK.Hidden('%s!moodle!domain'%(pre), vserver_nick)
            else:
                table.Add (_('Domain name'), CTK.TextCfg ('%s!moodle!domain'%(pre), False, {'class':'required'}), _(NOTE_DOMAINNAME))

        agree_box = CTK.Box()
        agree_box += CTK.RawHTML(_('Make sure you understand and accept the '))
        agree_box += CTK.LinkWindow ('http://docs.moodle.org/en/License', CTK.RawHTML(_('Moodle License')))
        agree_box += CTK.RawHTML(_(' before proceeding. Moodle license must be accepted to proceed.'))
        agree_box += CTK.CheckCfgText ('%s!moodle!agreement'%(pre), False, _('Accept license'), {'class':'required'})

        submit += table
        submit += agree_box
        submit.bind ('submit_success', CTK.DruidContent__JS_to_goto (table.id, URL_SERVER))

        buttons  = CTK.DruidButtonsPanel()
        buttons += CTK.DruidButton_Close(_('Cancel'))
        buttons += CTK.DruidButton_Submit (_('Next'), do_close=False)

        box  = CTK.Box()
        box += CTK.RawHTML ('<h2>%s</h2>'%(DETAILS_H2))
        box += CTK.RawHTML ('<p>%s</p>'  %(DETAILS_P1))
        box += submit
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

        # Apply the config
        if target_type == 'vserver':
            config = CONFIG_VSERVER %(props)
            CTK.cfg.apply_chunk (config)
            AddUsualStaticFiles (props['pre_rule_plus2'])
            CTK.cfg.normalize ('%s!rule'%(pre_vsrv))

        elif target_type == 'directory':
            config = CONFIG_DIR %(props)
            CTK.cfg.apply_chunk (config)

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
        commands = [({'function': tools.install_cli,
                      'description': _('Moodle installation and database population is in progress. The process may take several minutes.')}),
                    ({'command': 'chown -R ${php_user}:${php_group} ${app_root}/moodle ${app_root}/moodledata'}),]
        progress = market.CommandProgress.CommandProgress (commands, market.Install.URL_INSTALL_DONE)

        progress['php_user']  = replacements['php_user']
        progress['php_group'] = replacements['php_group']

        box = CTK.Box()
        box += CTK.RawHTML ('<h2>%s</h2>' %(_('Performing automatic installation')))
        box += CTK.RawHTML ('<p>%s</p>'   %(_('This process may take a while. Please, hold on.')))
        box += progress

        buttons = CTK.DruidButtonsPanel()
        buttons += CTK.DruidButton_Close(_('Cancel'))
        box += buttons

        return box.Render().toStr()


CTK.publish ('^%s$'%(URL_PRECONDITION), Precondition)
CTK.publish ('^%s$'%(URL_TARGET),       Target)
CTK.publish ('^%s$'%(URL_DATABASE),     Database)
CTK.publish ('^%s$'%(URL_DETAILS),      Site_Details)
CTK.publish ('^%s$'%(URL_SERVER),       App_Config)
CTK.publish ('^%s$'%(URL_POST_INSTALL), Post_Install)

CTK.publish ('^%s$'%(URL_DETAILS_APPLY), CTK.cfg_apply_post, validation=Site_Details.VALIDATION, method="POST")
