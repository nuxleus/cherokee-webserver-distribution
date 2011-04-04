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
import popen
from util import *
from market import Install_Log

php = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "php.pyo"), "php_util")
php_mods = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "php-mods.pyo"), "php_mods_util")


def check_modules ():
    errors = php_mods.check_modules (('dom', 'hash', 'iconv', 'mbstring', 'mysql', 'session', 'simplexml', 'tokenizer', 'xml'))
    if errors:
        return errors[0]

    # GD alternatives
    alternatives = ('gd', 'gd2')
    errors = php_mods.check_modules (alternatives)
    if len(errors) == len(alternatives):
        return errors[-1]


def check_settings ():
    php.settings = php.figure_php_information()
    errors = [] # store tuples (test, expected value, actual value)

    def check_compliance (key, expected):
        val = php.settings.get(key,'')
        if val.lower() != expected.lower():
            errors.append((key, expected, val))

    # PHP version
    try:
        info = php.settings
        ver  = info.get('PHP Version','0').split('-')[0]
        ver  = version_to_int (ver)
        assert ver >= 500200000
    except:
        errors.append(('PHP Version', '>= 5.2.0', info.get('PHP Version')))

    # Mem limits
    try:
        memory = php.settings['memory_limit'].lower()
        memory = memory.replace('m','')
        assert float(memory) >= 48
    except:
        errors.append(('memory_limit', '>= 48M', php.settings.get('memory_limit')))

    # Settings
    check_compliance ('safe_mode', 'Off')

    return errors


def modify_installer (root):
    path = os.path.join (root, 'silverstripe', 'install.php')
    pre  = "tmp!market!install!db"

    dbtype = CTK.cfg.get_val('%s!db_type' %(pre))
    dbname = CTK.cfg.get_val('%s!db_name' %(pre))
    dbuser = CTK.cfg.get_val('%s!db_user' %(pre))
    dbpass = CTK.cfg.get_val('%s!db_pass' %(pre))

    installer = open(path, 'r').read()
    installer = installer.replace('SS_DATABASE_USERNAME : "root"', 'SS_DATABASE_USERNAME : "%s"'%(dbuser))
    installer = installer.replace('SS_DATABASE_PASSWORD : ""',     'SS_DATABASE_PASSWORD : "%s"'%(dbpass))
    installer = installer.replace('"SS_mysite"',                   '"%s"'%(dbname))

    try:
        open(path, 'w').write(installer)
        Install_Log.log ("Success: install.php customized")
    except:
        Install_Log.log ("Error: install.php not customized")
        return False

    return True
