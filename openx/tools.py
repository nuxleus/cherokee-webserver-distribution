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

PHP_MOD_DEPENDENCIES = ('pcre', 'xml', 'zlib', 'spl')
NOTE_NO_DB = N_("The PHP interpreter does not support any of the required database modules: 'mysql', 'mysqli', or 'pgsql'")

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

    alternatives = ['pgsql']
    errors = php_mods.check_modules (alternatives)
    if len(errors) == len(alternatives):
        db_errors.append (errors[-1][1])

    if len(db_errors) == 2:
        return (NOTE_NO_DB, db_errors)

