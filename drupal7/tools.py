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
from util import *

php      = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "php.pyo"),      "php_util")
php_mods = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "php-mods.pyo"), "php_mods_util")
database = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "database.pyo"), "database_util")

NOTE_NO_DB = N_("The PHP interpreter does not support any of the required database modules: 'mysql', 'mysqli', or 'sqlite3'")

PHP_MOD_DEPENDENCIES = ('xml', 'gd', 'pdo', 'hash', 'dom', 'filter', 'json', 'simplexml')

def check_modules ():
    errors = php_mods.check_modules (PHP_MOD_DEPENDENCIES)
    if errors:
        return errors[0]


def check_database_support ():
    db_errors = []

    # DB modules
    alternatives = ['mysql', 'mysqli']
    errors = php_mods.check_modules (alternatives)
    if len(errors) == len(alternatives):
        db_errors.append (errors[-1][1])

    alternatives = ['sqlite3']
    errors = php_mods.check_modules (alternatives)
    if len(errors) == len(alternatives):
        db_errors.append (errors[-1][1])

    if len(db_errors) == 2:
        return (NOTE_NO_DB, db_errors)


def check_settings ():
    php.settings = php.figure_php_information()
    errors = [] # store tuples (test, expected value, actual value)

    def check_compliance (key, expected):
        val = php.settings.get(key,'')
        if val.lower() != expected.lower():
            errors.append((key, expected, val))

    # PHP version
    try:
        info = php.figure_php_information()
        ver  = info.get('PHP Version','0').split('-')[0]
        ver  = version_to_int (ver)
        vphp = version_to_int ('5.2.4')
        assert ver >= vphp
    except:
        errors.append(('PHP Version', '>= 5.2.4', info.get('PHP Version')))

    # Mem limits
    try:
        memory = php.settings['memory_limit'].lower()
        memory = memory.replace('m','')
        assert float(memory) >= 32
    except:
        errors.append(('memory_limit', '>= 32M', php.settings.get('memory_limit')))

    # Settings
    check_compliance ('register_globals', 'Off')
    check_compliance ('safe_mode', 'Off')
    check_compliance ('file_uploads', 'On')

    return errors


def cli_installation_command ():
    pre      = "tmp!market!install"
    app_root = CTK.cfg.get_val ('%s!root'%(pre))

    sitename  = CTK.cfg.get_val('%s!drupal7!sitename' %(pre))
    adminuser = CTK.cfg.get_val('%s!drupal7!adminuser' %(pre))
    adminpass = CTK.cfg.get_val('%s!drupal7!adminpass' %(pre))
    adminmail = CTK.cfg.get_val('%s!drupal7!adminmail' %(pre))
    locale    = CTK.cfg.get_val('%s!drupal7!locale' %(pre), 'en')

    dbtype  = CTK.cfg.get_val('%s!db!db_type' %(pre))
    dbname  = CTK.cfg.get_val('%s!db!db_name' %(pre))
    dbuser  = CTK.cfg.get_val('%s!db!db_user' %(pre))
    dbpass  = CTK.cfg.get_val('%s!db!db_pass' %(pre))
    dbauser = CTK.cfg.get_val('%s!db!admin_user' %(pre))
    dbapass = CTK.cfg.get_val('%s!db!admin_pass' %(pre))

    dburl = None

    # Environment
    env = os.environ.copy()
    env['DRUSH_PHP']  = php.figure_phpcli_binary()
    env['MYSQL_PATH'] = database.mysql_bins (database.MYSQL_BIN_NAMES)

    # Database access
    if dbtype == 'postgresql': # Diabled ATM. Only works with root credentials.
        dburl = 'pgsql://%(dbuser)s:%(dbpass)s@localhost/%(dbname)s' %(locals())
        env['PGUSER']     = dbauser
        env['PGPASSWORD'] = dbapass

    elif dbtype == 'mysql':
        dburl = 'mysql://%(dbuser)s:%(dbpass)s@localhost/%(dbname)s' %(locals())

        # MySQL might be outside the path
        mysql_path = database.mysql_path()
        if env.get('PATH'):
            env['PATH'] = '%s:%s' %(env['PATH'], mysql_path)
        else:
            env['PATH'] = mysql_path

    elif dbtype == 'sqlite3':
        dburl = 'sqlite:%(app_root)s/drush/drupal_database.sqlite' %(locals())

    if dburl == None:
        market.Install_Log.log ("Unknown DB type specified: %s" %(dbtype))
        raise ValueError, 'Unidentified DB type specified'

    # "drush --uri=http://example.com <parameters>" recommended for multisite installs
    cmd = '%(app_root)s/drush/drush site-install standard --locale=%(locale)s --db-url=%(dburl)s --account-name="%(adminuser)s" --account-pass="%(adminpass)s" --account-mail="%(adminmail)s" --site-name="%(sitename)s" -y' %(locals())

    return {'command': cmd, 'cd': '%(app_root)s/drupal/sites/default'%(locals()), 'env': env}


def drush_site_install():
    dbtype = CTK.cfg.get_val('tmp!market!install!db!db_type')
    kwargs = cli_installation_command()

    ret = popen.popen_sync (**kwargs)
    if ret['retcode'] != 0 and dbtype == 'mysql':
        #
        # Workaround -- http://drupal.org/node/898152
        # "trying to connect via unix:///var/mysql/mysql.sock"
        # By some reason, PDO uses the wrong socket to access MySQL.
        #

        # 1.- Find out what PHP's PDO tried to access
        pdo_path_re = re.findall (r'\(trying to connect via unix\:\/\/(.+?)\)', ret['stdout']+ret['stderr'], re.M)

        # 2.- Check where MySQL's socket is actually
        dbuser = CTK.cfg.get_val('tmp!market!install!db!db_user')
        dbpass = CTK.cfg.get_val('tmp!market!install!db!db_pass')

        mysqladmin_bin = database.mysql_bins (database.MYSQLADMIN_BIN_NAMES)
        ret_vars = popen.popen_sync ("%(mysqladmin_bin)s '-u%(dbuser)s' '-p%(dbpass)s' variables"%(locals()))

        mysql_vars_re = re.findall (r' socket +\| (.+?) ', ret_vars['stdout'], re.M)
        if mysql_vars_re:
            mysql_sock = mysql_vars_re[0]
        else:
            mysql_sock = "/tmp/mysql.sock"

        # 3.- Create a link
        if pdo_path_re:
            pdo_sock     = pdo_path_re[0]
            pdo_sock_dir = os.path.dirname(pdo_sock)

            if os.path.exists(mysql_sock) and not os.path.exists(pdo_sock):
                popen.popen_sync ("mkdir -p '%s'" %(pdo_sock_dir))
                popen.popen_sync ("ln -s '%s' '%s'" %(mysql_sock, pdo_sock))

                ret = popen.popen_sync (**kwargs)

    return ret
