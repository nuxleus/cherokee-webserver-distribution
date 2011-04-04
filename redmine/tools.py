#
# Copyright (c) 2010, Octality S.L. - Eume 6, Villaviciosa de Odon,
# 28670 Madrid, SPAIN. All rights reserved.
#
# Any unauthorized dissemination, distribution or copying is strictly
# forbidden.
#

import os
import CTK
import popen
import market
from util import *

EOF_STR = """ << EOF
%(lang)s
EOF
"""

OPTS_LANG  = [
('bg',   _('Bulgarian')),
('bs',   _('Bosnian')),
('ca',   _('Catalan')),
('cs',   _('Czech')),
('da',   _('Danish')),
('de',   _('German')),
('el',   _('Greek')),
('en',   _('English')),
('en-GB',_('English (GB)')),
('es',   _('Spanish')),
('eu',   _('Basque')),
('fi',   _('Finnish')),
('fr',   _('French')),
('gl',   _('Galician')),
('he',   _('Hebrew')),
('hr',   _('Croatian')),
('hu',   _('Hungarian')),
('id',   _('Indonesian')),
('it',   _('Italian')),
('ja',   _('Japanese')),
('ko',   _('Korean')),
('lt',   _('Lithuanian')),
('lv',   _('Latvian')),
('mn',   _('Mongolian')),
('nl',   _('Dutch')),
('no',   _('Norwegian')),
('pl',   _('Polish')),
('pt',   _('Portuguese')),
('pt-BR',_('Portuguese (BR)')),
('ro',   _('Romanian')),
('ru',   _('Russian')),
('sk',   _('Slovak')),
('sl',   _('Slovenian')),
('sr',   _('Serbian')),
('sr-YU',_('Serbian (YU)')),
('sv',   _('Swedish')),
('th',   _('Thai')),
('tr',   _('Turkish')),
('uk',   _('Ukrainian')),
('vi',   _('Vietnamese')),
('zh',   _('Chinese')),
('zh-TW',_('Chinese (TW)'))
]

ruby = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "ruby.pyo"),     "ruby_util")

def get_ruby_env():
    root = os.path.dirname (os.path.realpath (__file__))

    env_path    = os.getenv('PATH',     '')
    env_rubylib = os.getenv('RUBYLIB',  '')
    env_gempath = os.getenv('GEM_PATH', '')

    rb_env = {}
    rb_env['PATH']     = ':'.join ([os.path.join (root, 'bin'), os.path.join (root, '.gem/bin'), env_path])
    rb_env['RUBYLIB']  = ':'.join ([os.path.join (root, 'lib'), env_rubylib])
    rb_env['GEM_PATH'] = ':'.join ([os.path.join (root, '.gem'), env_gempath])
    rb_env['GEM_HOME'] = os.path.join (root, '.gem')
    return rb_env

def run_ruby_env (command):
    ruby_env = get_ruby_env()
    return popen.popen_sync (command, ruby_env)


ADDITIONAL_ENVIRONMENT_PATH = """ENV['GEM_PATH'] = '%(gem_path)s'
"""
ADDITIONAL_ENVIRONMENT_URL = """ActionController::Base.relative_url_root = '%(target_directory)s'
"""

def fix_configuration (root, target_directory):
    path = '%s:%s' %(os.path.join (root, '.gem'), os.path.join ('usr', 'lib', 'ruby', 'gems'))
    path_prev = os.getenv("GEM_PATH")
    gem_path = ':'.join(filter(lambda x:x, [path, path_prev]))

    config = ADDITIONAL_ENVIRONMENT_PATH %(locals())
    if target_directory:
        config += ADDITIONAL_ENVIRONMENT_URL %(locals())

    try:
        path = os.path.join (root, 'redmine', 'config', 'additional_environment.rb')
        open(path, 'w').write(config)
        market.Install_Log.log ("Success: additional_environment.rb customized")
        return True
    except:
        market.Install_Log.log ("Error: additional_environment.rb not customized")
        return False


DB_MYSQL = """
production:
  adapter: mysql
  database: %(dbname)s
  host: localhost
  username: %(dbuser)s
  password: %(dbpass)s
  encoding: utf8
"""

DB_PGSQL = """
production:
  adapter: postgresql
  database: %(dbname)s
  host: localhost
  username: %(dbuser)s
  password: %(dbpass)s
"""

DB_SQLITE = """
production:
  adapter: sqlite3
  database: db/cherokee_market.db
"""

def write_database_configuration (root):
    path = os.path.join (root, 'redmine', 'config', 'database.yml')
    pre  = "tmp!market!install!db"

    dbtype = CTK.cfg.get_val('%s!db_type' %(pre))
    dbname = CTK.cfg.get_val('%s!db_name' %(pre))
    dbuser = CTK.cfg.get_val('%s!db_user' %(pre))
    dbpass = CTK.cfg.get_val('%s!db_pass' %(pre))

    if   dbtype == 'mysql':
        config = DB_MYSQL  %(locals())
    elif dbtype == 'postgresql':
        config = DB_PGSQL  %(locals())
    elif dbtype == 'sqlite3':
        config = DB_SQLITE %(locals())
    else:
        raise EnvironmentError

    try:
        open(path, 'w').write(config)
        market.Install_Log.log ("Success: database.yml customized")
    except:
        market.Install_Log.log ("Error: database.yml not customized")
        raise EnvironmentError
