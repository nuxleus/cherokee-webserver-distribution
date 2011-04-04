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

php = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "php.pyo"), "php_util")
php_mods = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "php-mods.pyo"), "php_mods_util")


def check_modules ():
    errors = php_mods.check_modules (('curl', 'gd', 'pdo', 'pdo_mysql'))
    if errors:
        return errors[0]


def check_settings ():
    php.settings = php.figure_php_information()
    errors = [] # store tuples (test, expected value, actual value)

    # PHP version
    try:
        info = php.figure_php_information()
        ver  = info.get('PHP Version','0').split('-')[0]
        ver  = version_to_int (ver)
        assert ver >= 500200000
    except:
        errors.append(('PHP Version', '>= 5.2.0', info.get('PHP Version')))

    # Settings
    val = php.settings.get('file_uploads','')
    if val.lower() != 'on':
        errors.append(('file_uploads', 'On', val))

    return errors


def set_default_settings ():
    pre    = "tmp!market!install"
    root   = CTK.cfg.get_val ('%s!root' %(pre))
    dbname = CTK.cfg.get_val('%s!db!db_name' %(pre))
    dbuser = CTK.cfg.get_val('%s!db!db_user' %(pre))
    dbpass = CTK.cfg.get_val('%s!db!db_pass' %(pre))

    path = os.path.join (root, 'vanilla', 'conf', 'config-defaults.php')

    file = open (path, 'r').read()
    src = "$Configuration['Database']['Host']                             = 'dbhost';"
    dst = "$Configuration['Database']['Host']                             = 'localhost';"
    file = file.replace(src, dst)
    src = "$Configuration['Database']['Name']                             = 'dbname';"
    dst = "$Configuration['Database']['Name']                             = '%s';" %(dbname)
    file = file.replace(src, dst)
    src = "$Configuration['Database']['User']                             = 'dbuser';"
    dst = "$Configuration['Database']['User']                             = '%s';" %(dbuser)
    file = file.replace(src, dst)
    src = "$Configuration['Database']['Password']                         = '';"
    dst = "$Configuration['Database']['Password']                         = '%s';" %(dbpass)
    file = file.replace(src, dst)

    src = "$Configuration['Garden']['RewriteUrls']                         = FALSE;"
    dst = "$Configuration['Garden']['RewriteUrls']                         = TRUE;"
    file = file.replace(src, dst)

    try:
        open (path, 'w').write (file)
        Install_Log.log ('Success: config-defaults.php modified.')
    except:
        Install_Log.log ('Error: config-defaults.php not modified.')
        raise
