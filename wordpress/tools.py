#
# Copyright (c) 2010, Octality S.L. - Eume 6, Villaviciosa de Odon,
# 28670 Madrid, SPAIN. All rights reserved.
#
# Any unauthorized dissemination, distribution or copying is strictly
# forbidden.
#

import re
import os
import shutil
import CTK
import popen
import market
from util import *

php = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "php.pyo"), "php_util")
php_mods = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "php-mods.pyo"), "php_mods_util")

CFG_SAMPLE_SOURCE = """define('DB_NAME',"""

CFG_SAMPLE_TARGET = """define('WP_CACHE', true);
define('DB_NAME',"""


def check_modules ():
    # DB modules
    alternatives = ('mysql', 'mysqli')
    errors = php_mods.check_modules (alternatives)
    if len(errors) == len(alternatives):
        return errors[-1]


def configure_database (root):
    pre    = "tmp!market!install!db"
    dbname = CTK.cfg.get_val('%s!db_name' %(pre))
    dbuser = CTK.cfg.get_val('%s!db_user' %(pre))
    dbpass = CTK.cfg.get_val('%s!db_pass' %(pre))

    source = os.path.join (root, 'wordpress', 'wp-config-sample.php')
    target = os.path.join (root, 'wordpress', 'wp-config.php')
    popen.popen_sync ('cp -p %s %s'%(source, target))

    # Read
    lines = open(target,'r').readlines()

    # Modify DB related config entries
    content = ''
    for line in lines:
        if re.findall (r'define.+DB_NAME.+;', line):
            content += "define('DB_NAME', '%s');\n" %(dbname)
        elif re.findall (r'define.+DB_USER.+;', line):
            content += "define('DB_USER', '%s');\n" %(dbuser)
        elif re.findall (r'define.+DB_PASSWORD.+;', line):
            content += "define('DB_PASSWORD', '%s');\n" %(dbpass)
        else:
            content += line

    # Write
    try:
        open(target,'w').write (content)
        market.Install_Log.log ("DB details added to %s." %(target))
    except:
        market.Install_Log.log ("DB details were not added to %s." %(target))
        raise


def extend_sample_config_file (root):
    path = os.path.join (root, 'wordpress', 'wp-config-sample.php')
    content = open(path,'r').read()
    content = content.replace (CFG_SAMPLE_SOURCE, CFG_SAMPLE_TARGET)
    try:
        open(path,'w').write (content)
        market.Install_Log.log ("%s modified." %(path))
    except:
        market.Install_Log.log ("%s could not be modified." %(path))
        raise

def move_cache_advanced (root):
    source = os.path.join (root, 'advanced-cache.php')
    target = os.path.join (root, 'wordpress', 'wp-content', 'advanced-cache.php')

    try:
        content = open(source,'r').read()
        open(source, 'w').write (content %(locals()))
        market.Install_Log.log ("%s modified." %(source))
    except:
        market.Install_Log.log ("%s could not be modified." %(source))
        raise

    try:
        shutil.move(source, target)
        market.Install_Log.log ("advanced-cache.php successfully moved.")
    except:
        market.Install_Log.log ("advanced-cache.php could not be successfully moved.")
        raise

def move_cache_config (root):
    source = os.path.join (root, 'wp-cache-config.php')
    target = os.path.join (root, 'wordpress', 'wp-content', 'wp-cache-config.php')
    try:
        shutil.move(source, target)
        market.Install_Log.log ("wp-cache-config.php successfully moved.")
    except:
        market.Install_Log.log ("wp-cache-config.php could not be successfully moved.")
        raise
