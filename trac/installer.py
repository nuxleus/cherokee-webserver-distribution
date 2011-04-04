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

import re
import os
import CTK
import popen
import market
import SystemInfo
import validations

from util import *
from market.Install import Install_Stage
from market.CommandProgress import CommandProgress

# Load required modules
target   = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "target.pyo"),  "target_util")
tools    = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "tools.pyo"),   "tools_util")
cc       = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "cc.pyo"),      "cc_util")
database = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "database.pyo"), "database_util")

POST_UNPACK_COMMANDS = [
    ({'command': 'chown -R ${root_user}:${root_group} ${app_root}'}),
]

ERROR_DEPENDENCIES = N_('There was an error during the installation of the required dependencies.')
ERROR_PROJECT      = N_('There was an error during the creation of the Trac project.')
ERROR_RETRY        = N_('Please try again if the problem can be solved manually issuing the following command.')
NOTE_INSTALLING_H  = N_('Installing Trac.')
NOTE_INSTALLING_P1 = N_('Trac is being installed and a default Trac project is being created.')
NOTE_INSTALLING_P2 = N_('This might take some time. Please wait.')

NOTE_USER          = N_("Name of the initial user configured for Trac")
NOTE_PASSWORD      = N_("Password of the initial user configured for Trac")
NOTE_AUTHLIST_H    = N_("User configuration")
NOTE_AUTHLIST_P    = N_("Trac relies on the web server for user authentication. After the installation you will be able to define more users through the Security tab of the '/login' rule in Cherokee-Admin.")

# Cfg chunks
SOURCE = """
source!%(src_num)d!type = interpreter
source!%(src_num)d!nick = Trac %(src_num)d
source!%(src_num)d!host = %(localhost)s:%(src_port)d
source!%(src_num)d!interpreter = %(root)s/bin/tracd --single-env --protocol=scgi --hostname=%(localhost)s --port=%(src_port)s %(trac_project)s
source!%(src_num)d!timeout = 15
source!%(src_num)d!env!PYTHONPATH = %(PYTHONPATH)s
"""

CONFIG_VSERVER = SOURCE + """
%(pre_vsrv)s!nick = %(target_vserver)s
%(pre_vsrv)s!document_root = /dev/null

%(pre_vsrv)s!rule!10!match = directory
%(pre_vsrv)s!rule!10!match!directory = /chrome/common
%(pre_vsrv)s!rule!10!document_root = %(root)s/trac/trac/htdocs
%(pre_vsrv)s!rule!10!handler = file
%(pre_vsrv)s!rule!10!expiration = time
%(pre_vsrv)s!rule!10!expiration!time = 7d

%(pre_vsrv)s!rule!5!auth = authlist
%(pre_vsrv)s!rule!5!auth!list!1!user = %(user)s
%(pre_vsrv)s!rule!5!auth!list!1!password = %(password)s
%(pre_vsrv)s!rule!5!auth!methods = digest
%(pre_vsrv)s!rule!5!auth!realm = Trac
%(pre_vsrv)s!rule!5!match = fullpath
%(pre_vsrv)s!rule!5!match!final = 0
%(pre_vsrv)s!rule!5!match!fullpath!1 = /login

%(pre_vsrv)s!rule!1!match = default
%(pre_vsrv)s!rule!1!encoder!gzip = 1
%(pre_vsrv)s!rule!1!handler = scgi
%(pre_vsrv)s!rule!1!handler!change_user = 0
%(pre_vsrv)s!rule!1!handler!check_file = 0
%(pre_vsrv)s!rule!1!handler!error_handler = 0
%(pre_vsrv)s!rule!1!handler!pass_req_headers = 1
%(pre_vsrv)s!rule!1!handler!xsendfile = 0
%(pre_vsrv)s!rule!1!handler!balancer = round_robin
%(pre_vsrv)s!rule!1!handler!balancer!source!1 = %(src_num)d
"""

CONFIG_DIR = SOURCE + """
%(pre_rule_plus3)s!document_root = %(root)s/trac/trac/htdocs
%(pre_rule_plus3)s!match = directory
%(pre_rule_plus3)s!match!directory = %(target_directory)s/chrome/common
%(pre_rule_plus3)s!handler = file
%(pre_rule_plus3)s!expiration = time
%(pre_rule_plus3)s!expiration!time = 7d

%(pre_rule_plus2)s!auth = authlist
%(pre_rule_plus2)s!auth!list!1!user = %(user)s
%(pre_rule_plus2)s!auth!list!1!password = %(password)s
%(pre_rule_plus2)s!auth!methods = digest
%(pre_rule_plus2)s!auth!realm = Trac
%(pre_rule_plus2)s!match = fullpath
%(pre_rule_plus2)s!match!final = 0
%(pre_rule_plus2)s!match!fullpath!1 = %(target_directory)s/login

%(pre_rule_plus1)s!match = directory
%(pre_rule_plus1)s!match!directory = %(target_directory)s
%(pre_rule_plus1)s!encoder!gzip = 1
%(pre_rule_plus1)s!handler = scgi
%(pre_rule_plus1)s!handler!change_user = 0
%(pre_rule_plus1)s!handler!check_file = 0
%(pre_rule_plus1)s!handler!error_handler = 0
%(pre_rule_plus1)s!handler!pass_req_headers = 1
%(pre_rule_plus1)s!handler!xsendfile = 0
%(pre_rule_plus1)s!handler!balancer = round_robin
%(pre_rule_plus1)s!handler!balancer!source!1 = %(src_num)d
"""

URL_PRECONDITION  = market.Install.URL_INSTALL_SETUP_EXTERNAL
URL_TARGET        = "/market/install/trac/config/target"
URL_INSTALLATION  = "/market/install/trac/config/app"
URL_USER_CONFIG   = "/market/install/trac/config/user"
URL_SERVER_CONFIG = "/market/install/trac/config/web"
URL_APPLY         = "/market/install/trac/apply"


VALIDATION = [
    ('tmp!market!install!trac!user',     validations.is_not_empty),
    ('tmp!market!install!trac!password', validations.is_not_empty)
]

DB_SUPPORTED = ['sqlite3']

## Step 1: Preconditions
class Precondition (Install_Stage):
    def __safe_call__ (self):
        box = CTK.Box()
        box += CTK.RawHTML ('<h2>%s</h2>' %(_("Checking Requirements")))

        buttons = CTK.DruidButtonsPanel()
        buttons += CTK.DruidButton_Close(_('Cancel'))
        buttons += CTK.DruidButton_Goto (_('Retry'), URL_PRECONDITION, do_submit=True)

        # CC
        if not cc.detect_cc():
            box += InstructionBox (_(cc.NOTE), cc.CC_INSTRUCTIONS)
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


## Step 2: Target
class Target (Install_Stage):
    def __safe_call__ (self):
        box = CTK.Box()
        target_wid = target.TargetSelection()
        target_wid.bind ('goto_next_stage', CTK.DruidContent__JS_to_goto (box.id, URL_INSTALLATION))
        box += target_wid

        buttons = CTK.DruidButtonsPanel()
        buttons += CTK.DruidButton_Close(_('Cancel'))
        buttons += CTK.DruidButton_Submit (_('Next'), do_close=False)
        box += buttons

        return box.Render().toStr()


## Step 3: Trac installation
class Trac_Installation (Install_Stage):
    def __safe_call__ (self):
        box     = CTK.Box()
        buttons = CTK.DruidButtonsPanel()

        pre        = 'tmp!market!install'
        root       = CTK.cfg.get_val ('%s!root' %(pre))
        project    = os.path.join (root, 'project')
        trac_src   = os.path.join (root, 'trac')
        trac_admin = os.path.join (root, 'bin', 'trac-admin')
        easy_bin   = os.path.join (root, 'bin', 'easy_install')
        group_root = SystemInfo.get_info()['group_root']

        server_user  = CTK.cfg.get_val ('server!user',  'root')
        server_group = CTK.cfg.get_val ('server!group', group_root)

        # Figure out PYTHONPATH
        ret = popen.popen_sync ('python setup.py install --prefix=%(root)s'%(locals()), cd = '%(root)s/Genshi-0.6'%(locals()))

        err = ret['stderr'] + ret['stdout'] # Python 2.4.3 actually succeeds
        tmp = re.findall (r' (%(root)s.+site-packages)'%(locals()), err)

        PYTHONPATH = tmp[0]
        CTK.cfg['tmp!market!install!trac!PYTHONPATH'] = PYTHONPATH

        # Create site-packages
        if not os.path.isdir (PYTHONPATH):
            os.makedirs (PYTHONPATH)

        # Build PYTHONPATH
        env = os.environ.copy()
        if 'PYTHONPATH' in env:
            env['PYTHONPATH'] = '%s:%s' %(PYTHONPATH, env['PYTHONPATH'])
        else:
            env['PYTHONPATH'] = PYTHONPATH

        # Installation
        tasks = [
            # Install dependencies
            ({'command': "python setup.py install --prefix=${app_root}", 'env': env, 'cd': '%(root)s/flup-1.0.2'    %(locals())}),
            ({'command': "python setup.py install --prefix=${app_root}", 'env': env, 'cd': '%(root)s/Genshi-0.6'    %(locals())}),
            #({'command': "python setup.py install --prefix=${app_root}", 'env': env, 'cd': '%(root)s/pysqlite-2.6.0'%(locals())}),
            ({'function': tools.install_pysqlite, 'description': _('Satisfying pysqlite requirements'), 'params' : {'root':root, 'env':str(env)}}),
            ({'command': "python %(trac_src)s/setup.py install --prefix=${app_root}" %(locals()), 'env': env, 'cd': trac_src}),

            # Create Project
            ({'command': "%(trac_admin)s %(project)s initenv <<EOF\nTrac\n\nEOF\n" %(locals()), 'env': env}),
            ({'command': "chown -R %(server_user)s:%(server_group)s %(project)s"   %(locals())})]

        box += CTK.RawHTML ('<h2>%s</h2>' %(_('Installing Trac')))
        box += CTK.RawHTML ('<p>%s</p>'   %(_('This process may take a while. Please, hold on.')))
        box += CommandProgress (tasks, URL_USER_CONFIG)

        buttons = CTK.DruidButtonsPanel()
        buttons += CTK.DruidButton_Close(_('Cancel'))
        box += buttons

        return box.Render().toStr()


## Step 4: User configuration
def User_Config_Apply():
    pre = 'tmp!market!install'

    user     = CTK.post.get_val("%s!user"%(pre))
    password = CTK.post.get_val("%s!password"%(pre))

    market.Install_Log.log ('    User configured: %s:%s' %(user, password))
    return CTK.cfg_apply_post()


class User_Config (Install_Stage):
    def __safe_call__ (self):
        box     = CTK.Box()
        buttons = CTK.DruidButtonsPanel()

        pre     = "tmp!market!install"
        submit  = CTK.Submitter (URL_APPLY)
        table   = CTK.PropsTable()
        table.Add (_('Trac User'),     CTK.TextCfg('%s!user'%(pre),     False, {'class':'noauto'}), _(NOTE_USER))
        table.Add (_('Trac Password'), CTK.TextCfg('%s!password'%(pre), False, {'class':'noauto'}), _(NOTE_PASSWORD))
        submit += table
        submit.bind ('submit_success', CTK.DruidContent__JS_to_goto (box.id, URL_SERVER_CONFIG))

        box += CTK.RawHTML ('<h2>%s</h2>'   %(_(NOTE_AUTHLIST_H)))
        box += CTK.RawHTML ('<p>%s</p>'     %(_(NOTE_AUTHLIST_P)))
        box += submit

        buttons += CTK.DruidButton_Close(_('Cancel'))
        buttons += CTK.DruidButton_Submit (_('Next'), do_close=False)
        box += buttons

        return box.Render().toStr()

## Step 4: App configuration
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
        PYTHONPATH       = CTK.cfg.get_val ('%s!trac!PYTHONPATH'     %(pre))
        pre_vsrv         = 'vserver!%s' %(target_vserver_n)

        user             = CTK.cfg.get_val ('%s!user'                %(pre))
        password         = CTK.cfg.get_val ('%s!password'            %(pre))

        src_num, x       = cfg_source_get_next()
        src_port         = cfg_source_find_free_port()
        localhost        = cfg_source_get_localhost_addr()
        trac_project     = "%(root)s/project" %(locals())

        # More replacements
        next_rule = CTK.cfg.get_next_entry_prefix('%s!rule'%(pre_vsrv))
        props = cfg_get_surrounding_repls ('pre_rule', next_rule)
        props.update (locals())
        tools.fix_trac_ini (root)

        # Apply the config
        if target_type == 'vserver':
            config = CONFIG_VSERVER%(props)
            CTK.cfg.apply_chunk (config)

        elif target_type == 'directory':
            config = CONFIG_DIR %(props)
            CTK.cfg.apply_chunk (config)
            CTK.cfg.normalize ('%s!rule'%(pre_vsrv))

        # Redirect to the Thanks page
        box += CTK.RawHTML (js = CTK.DruidContent__JS_to_goto (box.id, market.Install.URL_INSTALL_DONE))
        return box.Render().toStr()


CTK.publish ('^%s$'%(URL_PRECONDITION),  Precondition)
CTK.publish ('^%s$'%(URL_TARGET),        Target)
CTK.publish ('^%s$'%(URL_INSTALLATION),  Trac_Installation)
CTK.publish ('^%s$'%(URL_USER_CONFIG),   User_Config)
CTK.publish ('^%s$'%(URL_SERVER_CONFIG), Server_Config)
CTK.publish ('^%s$'%(URL_APPLY),         User_Config_Apply, validation=VALIDATION, method="POST")
