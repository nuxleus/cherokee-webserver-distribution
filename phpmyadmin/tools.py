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
import string
import random

from util import *
from market import Install_Log

php      = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "php.pyo"),      "php_util")
php_mods = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "php-mods.pyo"), "php_mods_util")
database = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "database.pyo"), "database_util")

PHP_MOD_DEPENCENCIES = ('gd', 'mcrypt', 'session', 'spl', 'mbstring', 'ctype')

# SQL
SOURCE_SQL = """
CREATE DATABASE IF NOT EXISTS `phpmyadmin`
  DEFAULT CHARACTER SET utf8 COLLATE utf8_bin;
USE phpmyadmin;
"""

TARGET_SQL = """
CREATE DATABASE IF NOT EXISTS `%(dbname)s`
  DEFAULT CHARACTER SET utf8 COLLATE utf8_bin;
USE %(dbname)s;
"""


def check_modules ():
    errors = php_mods.check_modules (PHP_MOD_DEPENCENCIES)
    if errors:
        return errors[0]


def create_pmadb (root):
    path   = os.path.join (root, 'phpMyAdmin', 'scripts', 'create_tables.sql')
    pre    = "tmp!market!install!db"
    dbname = CTK.cfg.get_val('%s!db_name' %(pre))
    dbuser = CTK.cfg.get_val('%s!db_user' %(pre))
    dbpass = CTK.cfg.get_val('%s!db_pass' %(pre))

    sql = open(path, 'r').read()
    sql = sql.replace (SOURCE_SQL, TARGET_SQL %(locals()))

    try:
        open (path, 'w').write(sql)
    except:
        Install_Log.log ("Error: template for pmadb structure not created.")
        raise

    mysql_bin = database.mysql_bins (database.MYSQL_BIN_NAMES)
    if dbpass:
        ret = popen.popen_sync ('%(mysql_bin)s -u%(dbuser)s -p%(dbpass)s < %(path)s' %(locals()))
    else:
        ret = popen.popen_sync ('%(mysql_bin)s -u%(dbuser)s < %(path)s' %(locals()))

    if ret['retcode']:
        Install_Log.log ("Error: pmadb structure not created.")
        raise EnvironmentError, ret['stderr']
    else:
        Install_Log.log ("Success: pmadb structure created.")


def perform_config_replacements (root):
    path   = os.path.join (root, 'phpMyAdmin', 'config.inc.php')
    pre    = "tmp!market!install!db"
    dbname = CTK.cfg.get_val('%s!db_name' %(pre))
    dbuser = CTK.cfg.get_val('%s!db_user' %(pre))
    dbpass = CTK.cfg.get_val('%s!db_pass' %(pre))

    options = string.letters + string.digits
    secret  = ""
    for i in range(80):
        secret += random.choice(options)

    config = open (path, 'r').read()
    config = config.replace('${pmadb}',           dbname)
    config = config.replace('${pmauser}',         dbuser)
    config = config.replace('${pmapass}',         dbpass)
    config = config.replace('${blowfish_secret}', secret)
    config = config.replace('${upload_dir}',      os.path.join (root, 'dir_upload'))
    config = config.replace('${save_dir}',        os.path.join (root, 'dir_save'))

    try:
        open (path, 'w').write(config)
        Install_Log.log ("Success: config.inc.php customized")
    except:
        Install_Log.log ("Error: config.inc.php not customized")
        raise
