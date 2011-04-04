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
import popen
from util import *
from market import Install_Log
from market.Install import Install_Stage
from Wizard import AddUsualStaticFiles

# Load required modules
target = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "target.pyo"), "target_util")

# Just for Virtual Servers
target.TARGETS = [
    ('vserver',   'Virtual Server'),
]
target.NOTE_CREATE_NEW = N_("For cross-platform-compatibility, this package can only be configured in a new virtual server at the time being")

# Ownership and permissions
POST_UNPACK_COMMANDS = [
    ({'command': 'chown -R ${root_user}:${root_group} ${app_root}'}),
    ({'command': 'mv ${app_root}/moin-1.9.3 ${app_root}/moin'}),
    ({'command': 'mv ${app_root}/moin/wikiconfig.py ${app_root}/moin/wikiconfig.py.insecure'}),
    ({'command': 'cp ${app_root}/moin/wiki/config/wikiconfig.py ${app_root}/moin/wikiconfig.py'}),
    ({'command': 'chmod -R 770 ${app_root}/moin/wiki'}),
    ({'command': 'chown -R ${web_user}:${web_group} ${app_root}/moin'}),
]

# Messages
NOTE_SITENAME = N_("Name to show as Wiki name-logo")
NOTE_USER     = N_("Username of the administrator account")
NOTE_PASSWORD = N_("Password of the administrator account")
ERROR_USER    = N_("Could not create Moin administrator account")

# URLS
URL_INSTALLER_2   = "/market/install/moin/2"
URL_INSTALLER_3   = "/market/install/moin/3"
URL_DETAILS_APPLY = "/market/install/moin/apply"

# Cfg chunks
SOURCE = """
source!%(src_num)d!env_inherited = 1
source!%(src_num)d!host = %(localhost)s:%(src_port)d
source!%(src_num)d!interpreter = %(root)s/moin/wikiserver.py
source!%(src_num)d!nick = Moin %(src_num)d
source!%(src_num)d!type = interpreter
source!%(src_num)d!env!PYTHONPATH = %(root)s/moin:$PYTHONPATH
"""

CONFIG_VSERVER = SOURCE + """
%(pre_vsrv)s!nick = %(target_vserver)s
%(pre_vsrv)s!document_root = /dev/null

%(pre_vsrv)s!rule!200!match = directory
%(pre_vsrv)s!rule!200!match!directory = /moin_static
%(pre_vsrv)s!rule!200!document_root = %(root)s/moin/MoinMoin/web/static/htdocs
%(pre_vsrv)s!rule!200!handler = file

%(pre_vsrv)s!rule!100!match = default
%(pre_vsrv)s!rule!100!handler = proxy
%(pre_vsrv)s!rule!100!handler!balancer = round_robin
%(pre_vsrv)s!rule!100!handler!balancer!source!1 = %(src_num)d
"""

CONFIG_DIR = SOURCE + """
%(rule_pre_2)s!match = directory
%(rule_pre_2)s!match!directory = %(target_directory)s/moin_static
%(rule_pre_2)s!document_root = %(root)s/MoinMoin/web/static/htdocs
%(rule_pre_2)s!handler = file

%(rule_pre_1)s!match = directory
%(rule_pre_1)s!match!directory = %(target_directory)s
%(rule_pre_1)s!handler = proxy
%(rule_pre_1)s!handler!balancer = round_robin
%(rule_pre_1)s!handler!balancer!source!1 = %(src_num)d
"""

# wikiserverconfig_local.py
LOCAL_SETTINGS = """
from wikiserverconfig import LocalConfig

class Config(LocalConfig):
    port  = %s
"""

ADD_USER_COMMAND  = "%(root)s/moin/wiki/server/moin --config-dir=%(root)s/moin account create --name=%(user)s --password=%(password)s --email=@"


def Write_Local_Settings (root, port):
    local_settings = LOCAL_SETTINGS %(port)
    server_user    = CTK.cfg.get_val ('server!user')
    server_group   = CTK.cfg.get_val ('server!group')

    if server_user:
        local_settings += "    user  = '%s'\n" %(server_user)
    if server_user:
        local_settings += "    group = '%s'\n" %(server_group)

    path = os.path.join (root, 'moin', 'wikiserverconfig_local.py')
    try:
        open (path, 'w').write (local_settings)
        Install_Log.log ('Local Settings written successfully.')
    except:
        Install_Log.log ('ERROR: writing Local Settings.')
        raise


def Wiki_Config_Replacements (params):
    path   = os.path.join (params['root'], 'moin', 'wikiconfig.py')
    config = open (path, 'r').read()

    url_prefix_static = '/moin_static'
    if params.get('target_directory'):
        url_prefix_static = os.path.join (params['target_directory'], url_prefix_static)

    config = config.replace('#${url_prefix_static}', 'url_prefix_static = "%s"' %(url_prefix_static))
    config = config.replace('#${sitename}',          'sitename = u"%(sitename)s"' %(params))
    config = config.replace('#${superuser}',         'superuser = [u"%(user)s", ]' %(params))
    config = config.replace('#${acl_rights_before}', 'acl_rights_before = u"%(user)s:read,write,delete,revert,admin"' %(params))

    try:
        open (path, 'w').write(config)
        Install_Log.log ('Success: wikiconfig.py modified.')
    except:
        Install_Log.log ('Error: wikiconfig.py not modified.')
        raise

    server_user  = CTK.cfg.get_val ('server!user',  str(os.getuid()))
    server_group = CTK.cfg.get_val ('server!group', str(os.getgid()))
    root         = params['root']

    ret = popen.popen_sync ('chown -R %(server_user)s:%(server_group)s %(root)s/moin' %(locals()))
    if ret['retcode']:
        Install_Log.log ('Error: Moin permissions not correctly set.')
        raise ret['stderr']

    Install_Log.log ('Success: Moin permissions correctly set.')


def Wiki_Details_Apply():
    pre = 'tmp!market!install'

    user     = CTK.post.get_val("%s!user"%(pre))
    password = CTK.post.get_val("%s!password"%(pre))
    root     = CTK.cfg.get_val ('%s!root'            %(pre))

    env = os.environ.copy()
    env['PYTHONPATH'] = os.path.join(root, 'moin')
    ret = popen.popen_sync (ADD_USER_COMMAND %(locals()), stderr=True, env=env)

    Install_Log.log ('Running command: %s' %(ADD_USER_COMMAND %(locals())))
    Install_Log.log ('    ' + ret['stdout'])

    if ret['stderr']:
        Install_Log.log ('    ' + ret['stderr'])

    if not '- created.' in ret['stdout']:
        return {'ret':'error', 'errors': {"%s!user"%(pre): _(ERROR_USER)}}

    ret = CTK.cfg_apply_post()
    return ret


class Wiki_Details (CTK.Box):
    def __init__ (self):
        CTK.Box.__init__ (self)
        pre = "tmp!market!install"

        submit = CTK.Submitter (URL_DETAILS_APPLY)
        self += submit

        table = CTK.PropsTable()
        table.Add (_('Wiki Sitename'),  CTK.TextCfg('%s!sitename'%(pre), False, {'class':'noauto'}), _(NOTE_SITENAME))
        table.Add (_('Admin User'),     CTK.TextCfg('%s!user'%(pre),     False, {'class':'noauto'}), _(NOTE_USER))
        table.Add (_('Admin Password'), CTK.TextCfg('%s!password'%(pre), False, {'class':'noauto'}), _(NOTE_PASSWORD))
        submit += table


## Step 1: Target
class First_Step (Install_Stage):
    def __safe_call__ (self):
        box = CTK.Box()
        target_wid = target.TargetSelection()
        target_wid.bind ('goto_next_stage', CTK.DruidContent__JS_to_goto (box.id, URL_INSTALLER_2))
        box += target_wid

        buttons = CTK.DruidButtonsPanel()
        buttons += CTK.DruidButton_Close (_('Cancel'))
        buttons += CTK.DruidButton_Submit (_('Next'), do_close=False)
        box += buttons

        return box.Render().toStr()

## Step 2: Wiki details
class Wiki_Config (Install_Stage):
    def __safe_call__ (self):
        box = CTK.Box()
        details = Wiki_Details()
        details.bind ('submit_success', CTK.DruidContent__JS_to_goto (box.id, URL_INSTALLER_3))

        box += CTK.RawHTML ('<h2>%s</h2>' %(_("Wiki details")))
        box += details

        buttons = CTK.DruidButtonsPanel()
        buttons += CTK.DruidButton_Close(_('Cancel'))
        buttons += CTK.DruidButton_Submit (_('Next'), do_close=False)
        box += buttons

        return box.Render().toStr()

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
        target_directory = CTK.cfg.get_val ('%s!target!directory'    %(pre))
        pre_vsrv         = 'vserver!%s' %(target_vserver_n)
        src_num, x       = cfg_source_get_next()
        src_port         = cfg_source_find_free_port()
        localhost        = cfg_source_get_localhost_addr()
        sitename         = CTK.cfg.get_val ("%s!sitename"%(pre))
        user             = CTK.cfg.get_val ("%s!user"%(pre))

        # More replacements
        next_rule = CTK.cfg.get_next_entry_prefix('%s!rule'%(pre_vsrv))
        props = cfg_get_surrounding_repls ('pre_rule', next_rule)
        props.update (locals())

        # Write configuration files
        Write_Local_Settings (root, src_port)
        Wiki_Config_Replacements (locals())

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


CTK.publish ('^%s$'%(market.Install.URL_INSTALL_SETUP_EXTERNAL), First_Step)
CTK.publish ('^%s$'%(URL_INSTALLER_2), Wiki_Config)
CTK.publish ('^%s$'%(URL_INSTALLER_3), App_Config)
CTK.publish ('^%s$'%(URL_DETAILS_APPLY), Wiki_Details_Apply, method="POST")
