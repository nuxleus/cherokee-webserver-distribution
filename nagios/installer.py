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
import CTK
import market
import SystemInfo
import validations
import popen

from util import *
from market.Install import Install_Stage
from market.Util import InstructionBox
from Wizard import AddUsualStaticFiles
from market.CommandProgress import CommandProgress


# Load required modules
php      = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "php.pyo"),      "php_util")
target   = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "target.pyo"),   "target_util")
tools    = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "tools.pyo"),    "tools_util")
pwd_grp  = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "pwd_grp.pyo"),  "pwd_grp_util")
services = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "services.pyo"), "services_util")

NOTE_NAGIOSADMIN_H = N_("Administrator configuration")
NOTE_NAGIOSADMIN_P = N_("Nagios relies on the web server for user authentication. Please provide a user and password to access the web interface, as well as an email for notifications.")
NOTE_EMAIL         = N_("Email address you'd like to use for receiving alerts.")
NOTE_USERNAME      = N_("Username for the administrator user.")
NOTE_PASSWORD      = N_("Password for the administrator user.")

NOTE_NAGIOSUSER_H  = N_("Nagios system user")
NOTE_NAGIOSUSER_P  = N_("Nagios requires several user/group system-settings to run. Setting up a username and group for Nagios is mandatory. It can be done manually, or automatically generated for you.")
NOTE_NAGIOSUSER    = N_("User under which Nagios will be running")
NOTE_NAGIOSGROUP   = N_("Group under which Nagios will be running")
NOTE_NAGIOSCMD     = N_("Specify a group for allowing external commands to be submitted through the web interface.")
NOTE_METHOD        = N_("Please choose the desired user configuration method.")

ERROR_GROUP        = N_("User does not belong to the specified group")

PRE = "tmp!market!install"

METHODS = [
    ('automatic', _('Automatic')), # provide user details to be created
    ('manual',    _('Manual')),    # provide existing user and groups
]

# Ownership and permissions
POST_UNPACK_COMMANDS = [
    ({'command': 'mv ${app_root}/nagios-3.2.3 ${app_root}/nagios_core'}),
    ({'command': 'mv ${app_root}/nagios-plugins-1.4.15 ${app_root}/nagios_plugins'}),
    ({'command': 'chown -R ${root_user}:${root_group} ${app_root}'}),
]

# Config chunks
CONFIG_VSERVER = """
%(pre_vsrv)s!document_root = %(root)s/nagios/share
%(pre_vsrv)s!directory_index = index.html,index.php

%(pre_rule_minus1)s!auth = authlist
%(pre_rule_minus1)s!auth!list!1!user = %(nagiosadmin)s
%(pre_rule_minus1)s!auth!list!1!password = %(password)s
%(pre_rule_minus1)s!auth!methods = digest
%(pre_rule_minus1)s!auth!realm = Nagios
%(pre_rule_minus1)s!match = directory
%(pre_rule_minus1)s!match!directory = /
%(pre_rule_minus1)s!match!final = 0

# The PHP rule comes here

%(pre_rule_minus2)s!document_root = %(root)s/nagios/sbin
%(pre_rule_minus2)s!handler = cgi
%(pre_rule_minus2)s!match = directory
%(pre_rule_minus2)s!match!directory = /cgi-bin

%(pre_rule_minus3)s!handler = common
%(pre_rule_minus3)s!handler!allow_dirlist = 1
%(pre_rule_minus3)s!handler!allow_pathinfo = 0
%(pre_rule_minus3)s!handler!iocache = 1
%(pre_rule_minus3)s!match = default
"""

CONFIG_DIR = """
%(pre_rule_plus1)s!auth = authlist
%(pre_rule_plus1)s!auth!list!1!user = %(nagiosadmin)s
%(pre_rule_plus1)s!auth!list!1!password = %(password)s
%(pre_rule_plus1)s!auth!methods = digest
%(pre_rule_plus1)s!auth!realm = Nagios
%(pre_rule_plus1)s!match = directory
%(pre_rule_plus1)s!match!directory = %(target_directory)s
%(pre_rule_plus1)s!match!final = 0
%(pre_rule_plus1)s!document_root = %(root)s/nagios/share

# The PHP rule comes here

%(pre_rule_minus2)s!document_root = %(root)s/nagios/sbin
%(pre_rule_minus2)s!handler = cgi
%(pre_rule_minus2)s!handler!change_user = 0
%(pre_rule_minus2)s!handler!check_file = 1
%(pre_rule_minus2)s!handler!error_handler = 1
%(pre_rule_minus2)s!handler!pass_req_headers = 1
%(pre_rule_minus2)s!handler!xsendfile = 0
%(pre_rule_minus2)s!match = directory
%(pre_rule_minus2)s!match!directory = %(target_directory)s/cgi-bin

%(pre_rule_minus3)s!document_root = %(root)s/nagios/share
%(pre_rule_minus3)s!handler = common
%(pre_rule_minus3)s!match = directory
%(pre_rule_minus3)s!match!directory = %(target_directory)s
"""

URL_PRECONDITION       = market.Install.URL_INSTALL_SETUP_EXTERNAL
URL_TARGET             = "/market/install/nagios/target"
URL_USER_CONFIG_ADMIN  = php.URL_PHP_CONFIG_DONE
URL_USER_CONFIG_SYSTEM = "/market/install/nagios/system"
URL_USER_CREATION      = "/market/install/nagios/create"
URL_SERVER_BUILD       = "/market/install/nagios/build"
URL_SERVER_CONFIG      = "/market/install/nagios/server"
URL_LAUNCH_CONFIG      = "/market/install/nagios/launchconfig"
URL_LAUNCH_SERVICE     = "/market/install/nagios/launch"
URL_APPLY              = "/market/install/nagios/apply"
URL_METHOD_APPLY       = "/market/install/nagios/method/apply"
URL_AUTO_APPLY         = "/market/install/nagios/method_auto/apply"
URL_MANUAL_APPLY       = "/market/install/nagios/method_manual/apply"

# Validation functions
def system_user_exists (value):
    if pwd_grp.user_exists (value):
        return value
    raise ValueError, _('User does not exist')

def system_group_exists (value):
    if pwd_grp.group_exists (value):
        return value
    raise ValueError, _('Group does not exist')


## Preconditions
class Precondition (Install_Stage):
    def __safe_call__ (self):
        box = CTK.Box()
        box += CTK.RawHTML ('<h2>%s</h2>' %(_("Checking Dependencies")))

        if tools.check_cc():
            box += CTK.RawHTML (js = CTK.DruidContent__JS_to_goto (box.id, URL_TARGET))
            return box.Render().toStr()

        box += InstructionBox (_(tools.DEP_NOTE), tools.DEP_INSTRUCTIONS)
        buttons = CTK.DruidButtonsPanel()
        buttons += CTK.DruidButton_Close(_('Cancel'))
        buttons += CTK.DruidButton_Goto (_('Retry'), URL_PRECONDITION, do_submit=True)
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


## User configuration (Admin user)
class User_Config_Admin (Install_Stage):
    def __safe_call__ (self):
        box     = CTK.Box()
        box    += CTK.RawHTML ('<h2>%s</h2>' %(_('User configuration')))

        buttons = CTK.DruidButtonsPanel()
        submit  = CTK.Submitter (URL_APPLY)

        table   = CTK.PropsTable()
        table.Add (_('Username'), CTK.TextCfg('%s!nagiosadmin'%(PRE), False, {'class':'noauto', 'value':'nagiosadmin'}), _(NOTE_USERNAME))
        table.Add (_('Password'), CTK.TextCfg('%s!password'%(PRE), False, {'class':'noauto'}), _(NOTE_PASSWORD))
        table.Add (_('Email'), CTK.TextCfg('%s!email'%(PRE), False, {'class':'noauto'}), _(NOTE_EMAIL))

        submit += CTK.RawHTML ('<h2>%s</h2>' %(_(NOTE_NAGIOSADMIN_H)))
        submit += CTK.RawHTML ('<p>%s</p>'   %(_(NOTE_NAGIOSADMIN_P)))
        submit += table
        submit.bind ('submit_success', CTK.DruidContent__JS_to_goto (box.id, URL_USER_CONFIG_SYSTEM))

        box += submit

        buttons += CTK.DruidButton_Close(_('Cancel'))
        buttons += CTK.DruidButton_Submit (_('Next'), do_close=False)
        box += buttons

        return box.Render().toStr()


## User configuration (Nagios system user)
class User_Config_System (Install_Stage):
    def __safe_call__ (self):
        box     = CTK.Box()

        refresh = CTK.Refreshable({'id': 'nagios-user-creation-refresh'})
        refresh.register (lambda: User_Config_System_Refresh(refresh).Render())
        box += refresh
        return box.Render().toStr()


class User_Config_System_Refresh (CTK.Box):
    def __init__ (self, refresh):
        CTK.Box.__init__ (self)

        self += CTK.RawHTML ('<h2>%s</h2>' %(_(NOTE_NAGIOSUSER_H)))
        self += CTK.RawHTML ('<p>%s</p>'   %(_(NOTE_NAGIOSUSER_P)))
        self += Method_Chooser (refresh)

        method = CTK.cfg.get_val('%s!nagiosmethod' %(PRE))

        if method == 'automatic':
            widget = Method_Auto()
            widget.bind ('goto_next_stage', CTK.DruidContent__JS_to_goto (self.id, URL_USER_CREATION))

        else:
            widget = Method_Manual()
            widget.bind ('goto_next_stage', CTK.DruidContent__JS_to_goto (self.id, URL_SERVER_BUILD))

        buttons = CTK.DruidButtonsPanel()
        buttons += CTK.DruidButton_Close(_('Cancel'))
        buttons += CTK.DruidButton_Submit (_('Next'), do_close=False)
        self += widget
        self += buttons


class Method_Auto (CTK.Box):
    VALIDATION = [
        ('tmp!market!install!nagiosuser',  validations.is_not_empty),
        ('tmp!market!install!nagiosgroup', validations.is_not_empty),
        ('tmp!market!install!nagioscmd',   validations.is_not_empty),
    ]

    class Apply:
        def __call__ (self):
            return CTK.cfg_apply_post()

    def __init__ (self):
        CTK.Box.__init__ (self)

        submit  = CTK.Submitter (URL_AUTO_APPLY)
        submit += CTK.Hidden ('%s!nagiosuser'  %(PRE), 'nagios')
        submit += CTK.Hidden ('%s!nagiosgroup' %(PRE), 'nagios')
        submit += CTK.Hidden ('%s!nagioscmd'   %(PRE), 'nagioscmd')
        submit.bind ('submit_success', submit.JS_to_trigger ('goto_next_stage'))
        self += submit


class Method_Manual (CTK.Box):
    VALIDATION = [
        ('tmp!market!install!nagiosuser',  validations.is_not_empty),
        ('tmp!market!install!nagiosgroup', validations.is_not_empty),
        ('tmp!market!install!nagioscmd',   validations.is_not_empty),
        ('tmp!market!install!nagiosuser',  system_user_exists),
        ('tmp!market!install!nagiosgroup', system_group_exists),
        ('tmp!market!install!nagioscmd',   system_group_exists),
    ]

    class Apply:
        def __call__ (self):
            user     = CTK.post.get_val ('%s!nagiosuser'  %(PRE))
            group    = CTK.post.get_val ('%s!nagiosgroup' %(PRE))
            cmdgroup = CTK.post.get_val ('%s!nagioscmd'   %(PRE))

            errors = {}
            if not pwd_grp.is_user_in_group (user, group):
                errors['%s!nagiosgroup' %(PRE)] = _(ERROR_GROUP)

            if not pwd_grp.is_user_in_group (user, cmdgroup):
                errors['%s!nagioscmd' %(PRE)] = _(ERROR_GROUP)

            if errors:
                return {'ret':'fail', 'errors': errors}

            return CTK.cfg_apply_post()

    def __init__ (self):
        CTK.Box.__init__ (self)

        table   = CTK.PropsTable()
        table.Add (_('Nagios user'),          CTK.TextCfg('%s!nagiosuser' %(PRE), False, {'class':'noauto', 'value':'nagios'}),    _(NOTE_NAGIOSUSER))
        table.Add (_('Nagios group'),         CTK.TextCfg('%s!nagiosgroup'%(PRE), False, {'class':'noauto', 'value':'nagios'}),    _(NOTE_NAGIOSGROUP))
        table.Add (_('Nagios command group'), CTK.TextCfg('%s!nagioscmd'  %(PRE), False, {'class':'noauto', 'value':'nagioscmd'}), _(NOTE_NAGIOSCMD))

        submit  = CTK.Submitter (URL_MANUAL_APPLY)
        submit += table
        submit.bind ('submit_success', submit.JS_to_trigger ('goto_next_stage'))

        self += submit


class Method_Chooser (CTK.Box):
    class Apply:
        def __call__ (self):
            method_prev = CTK.cfg.get_val('%s!nagiosmethod'%(PRE), METHODS[0][0])
            method_post = CTK.post.get_val('%s!nagiosmethod'%(PRE))

            # If method hasn't changed, we don't want to trigger a
            # submit_success likely to be bound to a refreshable.
            if method_prev == method_post:
                return  {'ret':'fail'}

            return CTK.cfg_apply_post()


    def __init__ (self, refresh):
        CTK.Box.__init__ (self)

        # Populate cfg with the current type
        if not CTK.cfg.get_val('%s!nagiosmethod'%(PRE)):
            CTK.cfg['%s!nagiosmethod'%(PRE)] = METHODS[0][0]

        # Build widget
        combo = CTK.ComboCfg ('%s!nagiosmethod' %(PRE), trans_options(METHODS))

        table = CTK.PropsTable()
        table.Add (_('User configuration method'), combo, _(NOTE_METHOD))

        submit = CTK.Submitter (URL_METHOD_APPLY)
        submit += table
        submit.bind('submit_success', refresh.JS_to_refresh())

        self += submit


## User creation
class User_Creation (Install_Stage):
    def __safe_call__ (self):
        nagiosuser  = CTK.cfg.get_val ('%s!nagiosuser'  %(PRE))
        nagiosgroup = CTK.cfg.get_val ('%s!nagiosgroup' %(PRE))
        nagioscmd   = CTK.cfg.get_val ('%s!nagioscmd'   %(PRE))
        root        = CTK.cfg.get_val ('%s!root'        %(PRE))

        box = CTK.Box()
        box += CTK.RawHTML ('<h2>%s</h2>' %(_("Checking System Users")))

        # Installation
        ret = tools.create_credentials (nagiosuser, nagiosgroup, nagioscmd, root)

        if ret.get('ret') == True:
            box += CTK.RawHTML (js = CTK.DruidContent__JS_to_goto (box.id, URL_SERVER_BUILD))
            return box.Render().toStr()

        box += CTK.RawHTML ('<p>%s</p>' %(ret['error']))
        box += CTK.Notice (content=CTK.RawHTML ('<p>%s</p><pre>%s</pre>' %(_('The installer could not successfully execute the following command:'), ret['command'])))
        box += CTK.RawHTML ('<p>%s</p><pre>%s</pre>' %(_('The reported error was:'), ret['stderr']))

        buttons = CTK.DruidButtonsPanel()
        buttons += CTK.DruidButton_Close(_('Cancel'))
        buttons += CTK.DruidButton_Goto (_('Retry'), URL_USER_CREATION, do_submit=True)
        box += buttons

        return box.Render().toStr()


## User configuration
class Server_Install (Install_Stage):
    def make_install_init (self):
        # System Info
        system_info = SystemInfo.get_info()
        OS = system_info.get('system','').lower()

        # Fetch Parameters
        root       = CTK.cfg.get_val ('%s!root' %(PRE))
        nagiosuser = CTK.cfg.get_val ('%s!nagiosuser'  %(PRE))

        if OS == 'linux':
            ret = popen.popen_sync ("make install-init", cd="%(root)s/nagios_core"%(locals()))
            if ret['retcode']:
                return ret

        elif OS == 'darwin':
            path_pre   = os.path.join (root, 'nrpe.plist.pre')
            path_plist = os.path.join (root, 'nrpe.plist')

            # Build plist file
            plist = open (path_pre, 'r').read()
            plist = plist.replace ('${UserName}',         nagiosuser)
            plist = plist.replace ('${WorkingDirectory}', os.path.join (root, 'nagios'))

            f = open (path_plist, 'w+')
            f.write (plist)
            f.close()

        else: # Default case.
            ret = popen.popen_sync ("make install-init", cd="%(root)s/nagios_core"%(locals()))
            if ret['retcode']:
                return ret


        return {'retcode': 0}

    def __safe_call__ (self):
        root             = CTK.cfg.get_val ('%s!root'             %(PRE))
        target_directory = CTK.cfg.get_val ('%s!target!directory' %(PRE), '').rstrip('/')
        nagiosuser       = CTK.cfg.get_val ('%s!nagiosuser'       %(PRE))
        nagiosgroup      = CTK.cfg.get_val ('%s!nagiosgroup'      %(PRE))
        nagioscmd        = CTK.cfg.get_val ('%s!nagioscmd'        %(PRE))
        email            = CTK.cfg.get_val ('%s!email'            %(PRE))
        contacts_path    = os.path.join (root, 'nagios', 'etc', 'objects', 'contacts.cfg')

        cmd_config = './configure --with-command-group=%(nagioscmd)s --prefix=${app_root}/nagios'
        if target_directory:
            cmd_config += ' --with-htmurl=%(target_directory)s --with-cgiurl=%(target_directory)s/cgi-bin'
        else:
            cmd_config += ' --with-htmurl=/ --with-cgiurl=/cgi-bin'

        tasks = [({'cd': '${app_root}/nagios_core',    'command': cmd_config %(locals())}),
                 ({'cd': '${app_root}/nagios_core',    'command': 'make all'}),
                 ({'cd': '${app_root}/nagios_core',    'command': 'make install'}),
                 ({'function': self.make_install_init}),
                 ({'cd': '${app_root}/nagios_core',    'command': 'make install-config'}),
                 ({'cd': '${app_root}/nagios_core',    'command': 'make install-commandmode'}),
                 ({'cd': '${app_root}/nagios_plugins', 'command': './configure --with-nagios-user=%(nagiosuser)s --with-nagios-group=%(nagiosgroup)s --prefix=${app_root}/nagios'%(locals())}),
                 ({'cd': '${app_root}/nagios_plugins', 'command': 'make'}),
                 ({'cd': '${app_root}/nagios_plugins', 'command': 'make install'}),
                 # The following two steps fix and validate the configuration
                 ({'command': "sed -i.bkp 's/nagios@localhost/%(email)s/' %(contacts_path)s" %(locals())}),
                 ({'command': '${app_root}/nagios/bin/nagios -v ${app_root}/nagios/etc/nagios.cfg'}),
                 ({'command': 'chown -R %(nagiosuser)s:%(nagiosgroup)s ${app_root}/nagios'   %(locals())})]

        box  = CTK.Box()
        box += CTK.RawHTML ('<h2>%s</h2>' %(_('Installing Nagios')))
        box += CTK.RawHTML ('<p>%s</p>'   %(_('This process may take a while. Please, hold on.')))
        box += CommandProgress (tasks, URL_LAUNCH_CONFIG)

        buttons = CTK.DruidButtonsPanel()
        buttons += CTK.DruidButton_Close(_('Cancel'))
        box += buttons

        return box.Render().toStr()


## Launch configuration
class Launch_Config (Install_Stage):
    def __safe_call__ (self):
        box = CTK.Box()
        box += CTK.RawHTML ('<h2>%s</h2>' %(_("Nagios start up")))
        box += CTK.RawHTML ('<p>%s</p>' %(_("Nagios requires the Nagios system service to be launched at boot time. It is recommended that you allow the installer to add the service to your system.")))

        table = CTK.PropsTable()
        table.Add (_('Add system service'), CTK.CheckCfgText('%s!nagiosstartup'%(PRE), True, _('Enable'), {'class':'noauto'}), _('Mark the checkbox to automatically launch Nagios on start up.'))

        submit  = CTK.Submitter (URL_APPLY)
        submit += table
        submit.bind ('submit_success', CTK.DruidContent__JS_to_goto (box.id, URL_LAUNCH_SERVICE))
        box += submit

        buttons = CTK.DruidButtonsPanel()
        buttons += CTK.DruidButton_Close(_('Cancel'))
        buttons += CTK.DruidButton_Submit (_('Next'), do_close=False)
        box += buttons

        return box.Render().toStr()


## Launch the service
class Launch_Service (Install_Stage):
    def __safe_call__ (self):
        box = CTK.Box()
        box += CTK.RawHTML ('<h2>%s</h2>' %(_("Nagios start up")))

        system_info = SystemInfo.get_info()
        OS = system_info.get('system','').lower()

        root    = CTK.cfg.get_val ('%s!root' %(PRE))
        startup = CTK.cfg.get_val ('%s!nagiosstartup' %(PRE))
        plist   = os.path.join (root, 'nrpe.plist')

        # Register service: init.d, launchd, etc.
        ret = services.register_service ('nagios', macos_plist=plist)
        if ret['retcode'] == 0:
            # Launch
            if startup:
                if OS == 'darwin':
                    services.launch_service ('org.nagios.nrpe')
                else:
                    services.launch_service ('nagios')

            box += CTK.RawHTML (js = CTK.DruidContent__JS_to_goto (box.id, URL_SERVER_CONFIG))
            return box.Render().toStr()

        # Error handling
        notice = CTK.Notice ()
        notice += CTK.RawHTML ('<p>%s</p>' %(_('The installer could not successfully execute the following command:')))
        notice += CTK.RawHTML ('<pre>%s</pre>' %(ret['command']))
        notice += CTK.RawHTML ('<p>%s</p>' %(_('The reported error was:')))
        notice += CTK.RawHTML ('<pre>%s</pre>' %(ret['stderr']))

        box += CTK.RawHTML ('<p>%s</p>' %(ret['error']))
        box += notice
        box += CTK.RawHTML ('<p>%s</p>' %(_('You can either manually fix the problem and retry, or you can skip the step knowing that the Nagios system service will not be launched at boot time.')))

        buttons = CTK.DruidButtonsPanel()
        buttons += CTK.DruidButton_Close(_('Cancel'))
        buttons += CTK.DruidButton_Goto (_('Retry'), URL_LAUNCH_SERVICE, do_submit=True)
        buttons += CTK.DruidButton_Goto (_('Skip'),  URL_SERVER_CONFIG, do_submit=True)
        box += buttons

        return box.Render().toStr()


## App configuration
class Server_Config (Install_Stage):
    def __safe_call__ (self):
        box = CTK.Box()

        # Replacements
        app_id           = CTK.cfg.get_val ('%s!app!application_id'  %(PRE))
        app_name         = CTK.cfg.get_val ('%s!app!application_name'%(PRE))
        root             = CTK.cfg.get_val ('%s!root'                %(PRE))
        target_type      = CTK.cfg.get_val ('%s!target'              %(PRE))
        target_vserver   = CTK.cfg.get_val ('%s!target!vserver'      %(PRE))
        target_vserver_n = CTK.cfg.get_val ('%s!target!vserver_n'    %(PRE))
        target_directory = CTK.cfg.get_val ('%s!target!directory'    %(PRE))
        pre_vsrv         = 'vserver!%s' %(target_vserver_n)

        password          = CTK.cfg.get_val ('%s!password'           %(PRE))
        email             = CTK.cfg.get_val ('%s!email'              %(PRE))
        nagiosadmin       = CTK.cfg.get_val ('%s!nagiosadmin'        %(PRE))

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
            # Add index.html to index files if not present
            key   = '%s!directory_index' %(pre_vsrv)
            index = CTK.cfg.get_val (key)
            if not 'index.html' in index:
                CTK.cfg[key] = ','.join([x.strip() for x in index.split(',') + ['index.html']])

            config = CONFIG_DIR %(props)
            CTK.cfg.apply_chunk (config)

        box += CTK.RawHTML (js = CTK.DruidContent__JS_to_goto (box.id, market.Install.URL_INSTALL_DONE))
        return box.Render().toStr()



VALIDATION = [
    ('tmp!market!install!email',       validations.is_not_empty),
    ('tmp!market!install!email',       validations.is_email),
    ('tmp!market!install!password',    validations.is_not_empty),
    ('tmp!market!install!nagiosadmin', validations.is_not_empty),
]

CTK.publish ('^%s$'%(URL_PRECONDITION),        Precondition)
CTK.publish ('^%s$'%(URL_TARGET),              Target)
CTK.publish ('^%s$'%(URL_USER_CONFIG_ADMIN),   User_Config_Admin)
CTK.publish ('^%s$'%(URL_USER_CONFIG_SYSTEM),  User_Config_System)
CTK.publish ('^%s$'%(URL_USER_CREATION),       User_Creation)
CTK.publish ('^%s$'%(URL_SERVER_BUILD),        Server_Install)
CTK.publish ('^%s$'%(URL_LAUNCH_CONFIG),       Launch_Config)
CTK.publish ('^%s$'%(URL_LAUNCH_SERVICE),      Launch_Service)
CTK.publish ('^%s$'%(URL_SERVER_CONFIG),       Server_Config)

# POST
CTK.publish ('^%s$'%(URL_APPLY),        CTK.cfg_apply_post,    validation=VALIDATION, method="POST")
CTK.publish ('^%s$'%(URL_METHOD_APPLY), Method_Chooser.Apply,  method="POST")
CTK.publish ('^%s$'%(URL_AUTO_APPLY),   Method_Auto.Apply,     validation=Method_Auto.VALIDATION, method="POST")
CTK.publish ('^%s$'%(URL_MANUAL_APPLY), Method_Manual.Apply,   validation=Method_Manual.VALIDATION, method="POST")
