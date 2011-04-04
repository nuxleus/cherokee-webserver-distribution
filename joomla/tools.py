#
# Copyright (c) 2010, Octality S.L. - Eume 6, Villaviciosa de Odon,
# 28670 Madrid, SPAIN. All rights reserved.
#
# Any unauthorized dissemination, distribution or copying is strictly
# forbidden.
#

import os
import shutil
import CTK
import popen
import market
from util import *

php      = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "php.pyo"), "php_util")
php_mods = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "php-mods.pyo"), "php_mods_util")


def check_modules ():
    error_mysql  = php_mods.check_module('mysql')
    error_mysqli = php_mods.check_module('mysqli')
    if error_mysql and error_mysqli:
        return error_mysql

    errors = php_mods.check_modules (('zlib', 'xml'))
    if errors:
        return errors[0]


def configure_database (root):
    pre    = "tmp!market!install!db"
    dbname = CTK.cfg.get_val('%s!db_name' %(pre))
    dbuser = CTK.cfg.get_val('%s!db_user' %(pre))
    dbpass = CTK.cfg.get_val('%s!db_pass' %(pre))

    path  = os.path.join (root, 'joomla', 'installation', 'models', 'forms', 'database.xml')

    dbtype = 'msyqli'
    error  = php_mods.check_module('mysqli')
    if error:
        dbtype = 'mysql'

    content = open(path,'r').read()
    content = content.replace ('${dbtype}', dbtype)
    content = content.replace ('${dbname}', dbname)
    content = content.replace ('${dbuser}', dbuser)
    content = content.replace ('${dbpass}', dbpass)

    try:
        open(path,'w').write (content)
        market.Install_Log.log ("DB details added to %s." %(path))
    except:
        market.Install_Log.log ("DB details were not added to %s." %(path))
        raise
