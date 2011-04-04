#
# Copyright (c) 2010, Octality S.L. - Eume 6, Villaviciosa de Odon,
# 28670 Madrid, SPAIN. All rights reserved.
#
# Any unauthorized dissemination, distribution or copying is strictly
# forbidden.
#

import os
import string
import CTK
import market
from util import *
from market import Install_Log

php      = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "php.pyo"),      "php_util")
php_mods = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "php-mods.pyo"), "php_mods_util")

PHP_MOD_DEPENCENCIES = ('curl', 'zlib', 'gd')

def check_requirements ():
    # MySQL
    error_mysqli = php_mods.check_modules (('mysqli',))
    error_mysql  = php_mods.check_modules (('mysql',))
    if error_mysqli and error_mysql:
        return error_mysql

    # Rest of dependencies
    errors = php_mods.check_modules (PHP_MOD_DEPENCENCIES)
    if errors:
        return errors[0]

def php_installer_replacements ():
    """Replace macros patched into the installer"""

    pre    = "tmp!market!install"
    root   = CTK.cfg.get_val ('%s!root' %(pre))
    dbtype = CTK.cfg.get_val('%s!db!db_type' %(pre))
    dbname = CTK.cfg.get_val('%s!db!db_name' %(pre))
    dbuser = CTK.cfg.get_val('%s!db!db_user' %(pre))
    dbpass = CTK.cfg.get_val('%s!db!db_pass' %(pre))

    if dbtype == 'postgresql':
        dbtype = 'postgres'

    path = os.path.join (root, 'zencart', 'zc_install', 'includes', 'templates', 'template_default', 'templates', 'database_setup_default.php')

    file = open (path, 'r').read()
    file = file.replace('${dbname}', dbname)
    file = file.replace('${dbuser}', dbuser)
    file = file.replace('${dbpass}', dbpass)
    file = file.replace('${dbtype}', dbtype)

    try:
        open (path, 'w').write (file)
        Install_Log.log ('Success: database_setup_default.php modified.')
    except:
        Install_Log.log ('Error: database_setup_default.php not modified.')
        raise

    return {'retcode':0}

