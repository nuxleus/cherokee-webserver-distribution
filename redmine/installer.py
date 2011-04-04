# -*- coding: utf-8 -*-
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
import validations
import market.InstallUtil

from util import *
from market.Install import Install_Stage
from market.Util import InstructionBox
from market.CommandProgress import CommandProgress

INSTALL_H2 = N_("Installing")
INSTALL_P1 = N_("Redmine is being installed. This might take some time. Please wait…")

LANG_NOTE  = N_("List of available languages")
LANG_H2    = N_("Deployment Language")
LANG_P1    = N_("Please, specify the deployment language for the application.")

ACCESS_H2  = N_("Set up completed")
ACCESS_P1  = N_("Redmine has been installed. These are the default access details:")

NOTE_MYSQL1 = N_('Redmine supports MySQL as database backend, but the version of Ruby on your system is lower than the minimum requirement (1.8.6). MySQL support will be disabled.')
NOTE_MYSQL2 = N_('Redmine supports MySQL as database backend, but your system does not provide the MySQL development files required to support it. MySQL support will be disabled.')
NOTE_SQLITE = N_('Redmine supports SQLite3 as database backend, but the version of Ruby on your system is lower than the minimum requirement (1.8.7). SQLite3 support will be disabled.')
NOTE_NODBS  = N_('Redmine supports several database backends: MySQL, PostgreSQL, and SQLite3. Unfortunately none of them seems to be available. Try again if you can fix the situation.')

# Load required modules
target   = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "target.pyo"),   "target_util")
database = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "database.pyo"), "database_util")
tools    = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "tools.pyo"),    "tools_util")
ruby     = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "ruby.pyo"),     "ruby_util")
cc       = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "cc.pyo"),       "cc_util")
cpp      = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "cpp.pyo"),      "cpp_util")

# Ownership and permissions
POST_UNPACK_COMMANDS = [
    ({'command': 'mkdir -p ${app_root}/redmine/tmp'}),
    ({'command': 'mkdir -p ${app_root}/redmine/public/plugin_assets'}),
    ({'cd': '${app_root}', 'command': 'mkdir .gem bin lib src'}),
    ({'cd': '${app_root}/redmine', 'command': 'chmod -R 755 files log tmp public/plugin_assets'}),
    ({'command': 'chown -R ${root_user}:${root_group} ${app_root}'}),
    ({'cd': '${app_root}/redmine', 'command': 'chown -R ${web_user}:${web_group} files log tmp public/plugin_assets'}),
]

# Cfg chunks
SOURCE = """
source!%(src_num)d!type = interpreter
source!%(src_num)d!nick = Redmine %(src_num)d
source!%(src_num)d!host = %(localhost)s:%(src_port)d
source!%(src_num)d!interpreter = %(ruby_bin)s %(root)s/redmine/script/server thin start --binding=%(localhost)s --port=%(src_port)s --environment=production
source!%(src_num)d!timeout = 15
source!%(src_num)d!env_inherited = 0
source!%(src_num)d!env!RAILS_ENV = production
source!%(src_num)d!env!RUBYLIB = %(root)s/lib:$RUBYLIB
source!%(src_num)d!env!GEM_HOME = %(root)s/.gem
source!%(src_num)d!env!GEM_PATH = %(root)s/.gem:/usr/lib/ruby/gems:$GEM_PATH
"""

CONFIG_VSERVER = SOURCE + """
%(pre_vsrv)s!nick = %(target_vserver)s
%(pre_vsrv)s!document_root = /dev/null

%(pre_vsrv)s!rule!10!encoder!gzip = 1
%(pre_vsrv)s!rule!10!handler = proxy
%(pre_vsrv)s!rule!10!handler!balancer = round_robin
%(pre_vsrv)s!rule!10!handler!balancer!source!1 = %(src_num)d
%(pre_vsrv)s!rule!10!handler!in_allow_keepalive = 1
%(pre_vsrv)s!rule!10!match = default
"""

CONFIG_DIR = SOURCE + """
%(pre_rule_plus1)s!match = directory
%(pre_rule_plus1)s!match!directory = %(target_directory)s
%(pre_rule_plus1)s!encoder!gzip = 1
%(pre_rule_plus1)s!handler = proxy
%(pre_rule_plus1)s!handler!in_allow_keepalive = 1
%(pre_rule_plus1)s!handler!balancer = round_robin
%(pre_rule_plus1)s!handler!balancer!source!1 = %(src_num)d
%(pre_rule_plus1)s!handler!in_rewrite_request!1!regex = %(target_directory)s/(.*)
%(pre_rule_plus1)s!handler!in_rewrite_request!1!substring = /$1
"""

URL_TARGET         = "/market/install/redmine/target"
URL_DATABASE_PRE   = "/market/install/redmine/db_pre"
URL_DATABASE       = "/market/install/redmine/db"
URL_LANGUAGE       = "/market/install/redmine/language"
URL_INSTALL        = "/market/install/redmine/install"
URL_CONFIG_SERVER  = "/market/install/redmine/server"
URL_ACCESS_DETAILS = "/market/install/redmine/access"
URL_APPLY          = "/market/install/redmine/apply"

DB_SUPPORTED = ['mysql', 'postgresql', 'sqlite3']


## Preconditions
class Precondition (Install_Stage):
    def __safe_call__ (self):
        box = CTK.Box()
        box += CTK.RawHTML ('<h2>%s</h2>' %(_("Checking Requirements")))

        buttons = CTK.DruidButtonsPanel()
        buttons += CTK.DruidButton_Close(_('Cancel'))
        buttons += CTK.DruidButton_Goto (_('Retry'), market.Install.URL_INSTALL_SETUP_EXTERNAL, do_submit=True)

        # Ruby
        ruby_bin = ruby.detect_ruby ('1.8')
        gem_bin  = ruby.detect_gem()

        if not ruby_bin or not gem_bin:
            box += InstructionBox (_(ruby.RUBY18_NOTE), ruby.RUBY18_INSTRUCTIONS)
            box += buttons
            return box.Render().toStr()

        # CC
        cc_bin = cc.detect_cc (cache=False)
        if not cc_bin:
            box += InstructionBox (_(cc.CC_NOTE), cc.CC_INSTRUCTIONS)
            box += buttons
            return box.Render().toStr()

        # C++
        cpp_bin = cpp.detect_cpp (cache=False)
        if not cpp_bin:
            box += InstructionBox (_(cpp.CPP_NOTE), cpp.CPP_INSTRUCTIONS)
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
        target_wid.bind ('goto_next_stage', CTK.DruidContent__JS_to_goto (box.id, URL_DATABASE_PRE))

        buttons = CTK.DruidButtonsPanel()
        buttons += CTK.DruidButton_Close (_('Cancel'))
        buttons += CTK.DruidButton_Submit (_('Next'), do_close=False)

        box += target_wid
        box += buttons
        return box.Render().toStr()


## Database info
class Database_Pre (Install_Stage):
    def __safe_call__ (self):
        ruby_min   = ruby.ruby_version()
        dblist     = database.get_supported_dbs (DB_SUPPORTED)
        db_system  = [x['db'] for x in dblist]
        db_redmine = DB_SUPPORTED[:]

        box  = CTK.Box()
        box += CTK.RawHTML ('<h2>%s</h2>' %(_("Database Requirements")))
        message  = ''

        if 'mysql' in db_system:
            if version_to_int (ruby_min) < version_to_int ('1.8.6'):
                message += '<p>%s</p>' % (_(NOTE_MYSQL1))
                db_redmine.remove('mysql')

            elif not database.mysql_dev_path(): # required by mysql gem:
                message += '<p>%s</p>' % (_(NOTE_MYSQL2))
                db_redmine.remove('mysql')

                box += market.Util.InstructionBox (database.MYSQL_DEV_NOTE, database.MYSQL_DEV_INSTRUCTIONS)

        if 'sqlite3' in db_system:
            if version_to_int (ruby_min) < version_to_int ('1.8.7'): # required by sqlite3 gem:
                message += '<p>%s</p>' % (_(NOTE_SQLITE))
                db_redmine.remove('sqlite3')

        # No DBS
        if db_redmine == []:
            message += '<p>%s</p>' % (_(NOTE_NODBS))

            buttons  = CTK.DruidButtonsPanel()
            buttons += CTK.DruidButton_Close(_('Cancel'))
            buttons += CTK.DruidButton_Goto (_('Retry'), URL_DATABASE_PRE, do_submit=True)

            notice  = CTK.Notice()
            notice += CTK.RawHTML (message)

            box += notice
            box += buttons

        # Some DBs present on system but not supported for some reason
        elif message:
            buttons  = CTK.DruidButtonsPanel()
            buttons += CTK.DruidButton_Close(_('Cancel'))
            buttons += CTK.DruidButton_Goto (_('Next'), URL_DATABASE, do_submit=True)

            notice  = CTK.Notice()
            notice += CTK.RawHTML (message)

            box += notice
            box += buttons

        # DB list untouched
        else:
            box += CTK.RawHTML (js=CTK.DruidContent__JS_to_goto (box.id, URL_DATABASE))

        return box.Render().toStr()


## Database selection
class Database (Install_Stage):
    def __safe_call__ (self):
        ruby_min = ruby.ruby_version()

        db_supported = DB_SUPPORTED[:]

        if version_to_int (ruby_min) < version_to_int ('1.8.6') or \
                not database.mysql_dev_path(): # required by mysql gem:
            db_supported.remove('mysql')

        if version_to_int (ruby_min) < version_to_int ('1.8.7'): # required by sqlite3 gem:
            db_supported.remove('sqlite3')

        box = CTK.Box()
        db_widget = database.MethodSelection (db_supported)
        db_widget.bind ('goto_next_stage', CTK.DruidContent__JS_to_goto (box.id, URL_LANGUAGE))

        buttons = CTK.DruidButtonsPanel()
        buttons += CTK.DruidButton_Close (_('Cancel'))
        buttons += CTK.DruidButton_Submit (_('Next'), do_close=False)

        box += db_widget
        box += buttons
        return box.Render().toStr()


## Language selection
class Language (Install_Stage):
    def __safe_call__ (self):
        pre = "tmp!market!install"

        table = CTK.PropsTable()
        table.Add (_('Language'), CTK.ComboCfg('%s!lang'%(pre), tools.OPTS_LANG, {'class':'noauto', 'selected':'en'}), _(LANG_NOTE))

        submit  = CTK.Submitter (URL_APPLY)
        submit += table

        buttons  = CTK.DruidButtonsPanel()
        buttons += CTK.DruidButton_Close(_('Cancel'))
        buttons += CTK.DruidButton_Goto (_('Next'), URL_INSTALL, do_submit=True)

        box  = CTK.Box()
        box += CTK.RawHTML ('<h2>%s</h2>'%(LANG_H2))
        box += CTK.RawHTML ('<p>%s</p>'  %(LANG_P1))
        box += submit
        box += buttons
        return box.Render().toStr()


## App installation
class Installation (Install_Stage):
    def __safe_call__ (self):
        pre  = 'tmp!market!install'
        root = CTK.cfg.get_val ('%s!root' %(pre))
        lang = CTK.cfg.get_val ('%s!lang' %(pre))
        db   = CTK.cfg.get_val ('%s!db!db_type' %(pre))

        path = os.path.join (root, 'redmine')
        env  = tools.get_ruby_env()

        tools.write_database_configuration (root)

        GEM_INST_FAST = 'gem install --no-test --no-rdoc --no-ri --verbose --local '
        GEM_INST_SLOW = 'gem install --no-test --no-rdoc --verbose --local '

        tpre =  [({'command': GEM_INST_FAST + '${app_root}/rake-0.8.7.gem',                  'env': env}),
                 ({'command': GEM_INST_FAST + '${app_root}/activesupport-2.3.5.gem',         'env': env}),
                 ({'command': GEM_INST_FAST + '${app_root}/activerecord-2.3.5.gem',          'env': env}),
                 ({'command': GEM_INST_SLOW + '${app_root}/rack-1.0.1.gem',                  'env': env}),
                 ({'command': GEM_INST_FAST + '${app_root}/actionpack-2.3.5.gem',            'env': env}),
                 ({'command': GEM_INST_FAST + '${app_root}/actionmailer-2.3.5.gem',          'env': env}),
                 ({'command': GEM_INST_FAST + '${app_root}/activeresource-2.3.5.gem',        'env': env}),
                 ({'command': GEM_INST_FAST + '${app_root}/rails-2.3.5.gem',                 'env': env}),
                 ({'command': GEM_INST_SLOW + '${app_root}/daemons-1.1.0.gem',               'env': env}),
                 ({'command': GEM_INST_SLOW + '${app_root}/eventmachine-0.12.10.gem',        'env': env}),
                 ({'command': GEM_INST_FAST + '${app_root}/thin-1.2.7.gem',                  'env': env}),
                 ({'command': GEM_INST_FAST + '${app_root}/cgi_multipart_eof_fix-2.5.0.gem', 'env': env}),
                 ({'command': GEM_INST_FAST + '${app_root}/i18n-0.4.2.gem',                  'env': env}),]

        # PostgreSQL
        if db == 'postgresql':
            tdb = [({'command': GEM_INST_FAST + '${app_root}/postgres-pr-0.6.3.gem', 'env': env}),]

        # SQLite
        elif db == 'sqlite3':
            tdb = [({'command': GEM_INST_FAST + '${app_root}/sqlite3-1.3.3.gem',      'env': env}),
                   ({'command': GEM_INST_FAST + '${app_root}/sqlite3-ruby-1.3.3.gem', 'env': env}),]
        # MySQL
        elif db == 'mysql':
            mysql_bin = database.mysql_bins (database.MYSQL_BIN_NAMES)
            mysql_dir = os.path.realpath (mysql_bin + '/../..')

            if 'mysql' in mysql_dir:
                tdb = [({'command': GEM_INST_FAST + '${app_root}/mysql-2.8.1.gem -- --with-mysql-dir=%s'%(mysql_dir), 'env': env}),]
            else:
                tdb = [({'command': GEM_INST_FAST + '${app_root}/mysql-2.8.1.gem', 'env': env}),]

        else:
            assert False, "Unsupported DB"

        tpost = [({'command': 'cd %s && rake generate_session_store' %(path),         'env': env}),
                 ({'command': 'cd %s && RAILS_ENV=production rake db:migrate' %(path),'env': env}),
                 ({'command': 'cd %s && RAILS_ENV=production rake redmine:load_default_data %s' %(path, tools.EOF_STR%(locals())), 'env': env}),
                 ({'command': 'chown -R ${web_user}:${web_group} ${app_root}/redmine/db'}),]

        tasks = tpre + tdb + tpost

        buttons  = CTK.DruidButtonsPanel()
        buttons += CTK.DruidButton_Close(_('Cancel'))

        box  = CTK.Box()
        box += CTK.RawHTML ('<h2>%s</h2>'%(INSTALL_H2))
        box += CTK.RawHTML ('<p>%s</p>'  %(INSTALL_P1))
        box += CommandProgress (tasks, URL_CONFIG_SERVER)
        box += buttons

        return box.Render().toStr()


## Cherokee configuration
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
        pre_vsrv         = 'vserver!%s' %(target_vserver_n)

        src_num, x       = cfg_source_get_next()
        src_port         = cfg_source_find_free_port()
        localhost        = cfg_source_get_localhost_addr()
        ruby_bin         = ruby.detect_ruby('1.8')

        # More replacements
        next_rule = CTK.cfg.get_next_entry_prefix('%s!rule'%(pre_vsrv))
        props = cfg_get_surrounding_repls ('pre_rule', next_rule)
        props.update (locals())
        tools.fix_configuration (root, target_directory)

        # Apply the config
        if target_type == 'vserver':
            config = CONFIG_VSERVER%(props)
            CTK.cfg.apply_chunk (config)

        elif target_type == 'directory':
            config = CONFIG_DIR %(props)
            CTK.cfg.apply_chunk (config)
            CTK.cfg.normalize ('%s!rule'%(pre_vsrv))

        # Proceed to user details
        box += CTK.RawHTML (js = CTK.DruidContent__JS_to_goto (box.id, URL_ACCESS_DETAILS))
        return box.Render().toStr()


## User details
class Access_Details (Install_Stage):
    def __safe_call__ (self):
        notice  = CTK.Notice ()
        notice += CTK.RawHTML ('<p><b>%s:</b> %s</p>' %(_('Username'), 'admin'))
        notice += CTK.RawHTML ('<p><b>%s:</b> %s</p>' %(_('Password'), 'admin'))

        buttons = CTK.DruidButtonsPanel()
        buttons += CTK.DruidButton_Close(_('Cancel'))
        buttons += CTK.DruidButton_Goto (_('Next'), market.Install.URL_INSTALL_DONE, do_submit=True)

        box  = CTK.Box()
        box += CTK.RawHTML ('<h2>%s</h2>' %(_(ACCESS_H2)))
        box += CTK.RawHTML ('<p>%s</p>' %(_(ACCESS_P1)))
        box += notice
        box += buttons
        return box.Render().toStr()


CTK.publish ('^%s$'%(market.Install.URL_INSTALL_SETUP_EXTERNAL), Precondition)
CTK.publish ('^%s$'%(URL_TARGET),         Target)
CTK.publish ('^%s$'%(URL_DATABASE_PRE),   Database_Pre)
CTK.publish ('^%s$'%(URL_DATABASE),       Database)
CTK.publish ('^%s$'%(URL_LANGUAGE),       Language)
CTK.publish ('^%s$'%(URL_INSTALL),        Installation)
CTK.publish ('^%s$'%(URL_CONFIG_SERVER),  Server_Config)
CTK.publish ('^%s$'%(URL_ACCESS_DETAILS), Access_Details)
CTK.publish ('^%s$'%(URL_APPLY),          CTK.cfg_apply_post, method="POST")
