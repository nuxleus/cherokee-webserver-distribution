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

php_mods = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "php-mods.pyo"), "php_mods_util")

CFG_TEMPLATE = """<?php
// phpBB 3.0.x auto-generated configuration file
// Do not change anything in this file!
$dbms = '%(dbdriver)s'; // mysqli, mysql, postgres
$dbhost = 'localhost';
$dbport = '';
$dbname = '%(dbname)s';
$dbuser = '%(dbuser)s';
$dbpasswd = '%(dbpass)s';
$table_prefix = 'phpbb_';
$acm_type = 'file';
$load_extensions = '';

@define('PHPBB_INSTALLED', true);
// @define('DEBUG', true);
// @define('DEBUG_EXTRA', true);
?>
"""

NOTE_NO_DB = N_("The PHP interpreter does not support any of the required database modules: 'mysql', 'mysqli', or 'pgsql'")
PHP_MOD_DEPENCENCIES = ('zlib', 'xml')

def check_modules ():
    errors = php_mods.check_modules (PHP_MOD_DEPENCENCIES)
    if errors:
        return errors[0]


def check_database_support ():
    db_errors = []

    # DB modules
    alternatives = ['mysql', 'mysqli']
    errors = php_mods.check_modules (alternatives)
    if len(errors) == len(alternatives):
        db_errors.append (errors[-1][1])

    alternatives = ['pgsql']
    errors = php_mods.check_modules (alternatives)
    if len(errors) == len(alternatives):
        db_errors.append (errors[-1][1])

    if len(db_errors) == 2:
        return (NOTE_NO_DB, db_errors)


def write_initial_config ():
    pre     = "tmp!market!install"
    root    = CTK.cfg.get_val ('%s!root' %(pre))
    dbtype  = CTK.cfg.get_val('%s!db!db_type' %(pre))
    dbname  = CTK.cfg.get_val('%s!db!db_name' %(pre))
    dbuser  = CTK.cfg.get_val('%s!db!db_user' %(pre))
    dbpass  = CTK.cfg.get_val('%s!db!db_pass' %(pre))

    dbdriver = None
    if dbtype == 'postgresql':
        dbdriver = 'postgres'
    elif dbtype == 'mysql':
        if php_mods.check_module ('mysqli') == None:
            dbdriver = 'mysqli'
        elif php_mods.check_module ('mysql') == None:
            dbdriver = 'mysql'

    if dbdriver == None:
        market.Install_Log.log ("Unknown DB type specified")
        raise ValueError, 'Unidentified DB type specified'

    try:
        path = os.path.join (root, 'phpBB3', 'config.php')
        config = CFG_TEMPLATE %(locals())
        open (path, 'w').write (config)
        market.Install_Log.log ("Initial config.php successfully  written")
    except Exception, e:
        market.Install_Log.log ("Error writing initial config.php")
        raise e


def patch_phpbb_installer ():
    """Patches get_submitted_data function to feed data"""

    pre     = "tmp!market!install"
    root    = CTK.cfg.get_val ('%s!root' %(pre))
    dbtype  = CTK.cfg.get_val('%s!db!db_type' %(pre))
    dbname  = CTK.cfg.get_val('%s!db!db_name' %(pre))
    dbuser  = CTK.cfg.get_val('%s!db!db_user' %(pre))
    dbpass  = CTK.cfg.get_val('%s!db!db_pass' %(pre))

    dbdriver = None
    if dbtype == 'postgresql':
        dbdriver = 'postgres'
    elif dbtype == 'mysql':
        if php_mods.check_module ('mysqli') == None:
            dbdriver = 'mysqli'
        elif php_mods.check_module ('mysql') == None:
            dbdriver = 'mysql'

    if dbdriver == None:
        market.Install_Log.log ("Unknown DB type specified")
        raise ValueError, 'Unidentified DB type specified'

    try:
        path = os.path.join (root, 'phpBB3', 'install', 'install_install.php')
        config = open (path, 'r').read()
        config = config.replace("request_var('dbms', ''),",           "request_var('dbms', '%(dbdriver)s')," %(locals()))
        config = config.replace("request_var('dbhost', ''),",         "request_var('dbhost', 'localhost'),")
        config = config.replace("request_var('dbuser', ''),",         "request_var('dbuser', '%(dbuser)s')," %(locals()))
        config = config.replace("request_var('dbpasswd', '', true),", "request_var('dbpasswd', '%(dbpass)s', true)," %(locals()))
        config = config.replace("request_var('dbname', ''),",         "request_var('dbname', '%(dbname)s')," %(locals()))
        open (path, 'w').write (config)
        market.Install_Log.log ("install_install.php patched successfully")
    except Exception, e:
        market.Install_Log.log ("Error patching install_install.php")
        raise e
