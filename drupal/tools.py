#
# Copyright (c) 2010, Octality S.L. - Eume 6, Villaviciosa de Odon,
# 28670 Madrid, SPAIN. All rights reserved.
#
# Any unauthorized dissemination, distribution or copying is strictly
# forbidden.
#

import os
import CTK
from util import *
from market import Install_Log

php      = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "php.pyo"),      "php_util")
php_mods = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "php-mods.pyo"), "php_mods_util")

NOTE_NO_DB = N_("The PHP interpreter does not support any of the required database modules: 'mysql', 'mysqli', or 'pgsql'")

def check_php_database_support ():
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


def preload_installer (root):
    path = os.path.join (root, 'drupal', 'install.php')
    pre  = "tmp!market!install!db"

    dbtype = CTK.cfg.get_val('%s!db_type' %(pre))
    dbname = CTK.cfg.get_val('%s!db_name' %(pre))
    dbuser = CTK.cfg.get_val('%s!db_user' %(pre))
    dbpass = CTK.cfg.get_val('%s!db_pass' %(pre))

    if dbtype == "postgresql":
        dbtype = 'pgsql'
    else: # mysql
        modules = [x.lower() for x in php.figure_modules()]
        if 'mysqli' in modules:
            dbtype = 'mysqli'
        else:
            dbtype = 'mysql'

    subst = [('${dbtype}', dbtype),
             ('${dbname}', dbname),
             ('${dbuser}', dbuser),
             ('${dbpass}', dbpass)]

    data  = open(path, 'r').read()
    for s in subst:
        data = data.replace (s[0], s[1])

    try:
        open(path, 'w').write(data)
        Install_Log.log ("Success: install.php customized")
    except:
        Install_Log.log ("Error: install.php not customized")
        raise
