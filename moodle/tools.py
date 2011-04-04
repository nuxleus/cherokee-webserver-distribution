#
# Copyright (c) 2010, Octality S.L. - Eume 6, Villaviciosa de Odon,
# 28670 Madrid, SPAIN. All rights reserved.
#
# Any unauthorized dissemination, distribution or copying is strictly
# forbidden.
#

import os
import random
import string

import CTK
import market
import popen
import validations
from util import *

php      = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "php.pyo"),      "php_util")
php_mods = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "php-mods.pyo"), "php_mods_util")

PHP_MOD_DEPENDENCIES = ('iconv', 'mbstring', 'curl', 'openssl', 'tokenizer', 'xmlrpc', 'ctype', 'zlib', 'simplexml', 'spl', 'pcre', 'dom', 'xml', 'xmlreader', 'xmlwriter', 'json', 'zip')

CLI_COMMAND = """%(php_cli_bin)s '%(root)s/moodle/admin/cli/install.php' \
--lang=en --wwwroot='%(wwwroot)s' --dataroot='%(root)s/moodledata' \
--dbtype='%(dbchoice)s' --dbhost='localhost' --dbname='%(dbname)s' --dbuser='%(dbuser)s' \
--dbpass='%(dbpass)s' --fullname='%(fullname)s' --shortname='%(shortname)s' \
--adminuser='%(adminuser)s' --adminpass='%(adminpass)s' --non-interactive --agree-license
"""

NOTE_NO_DB = N_("The PHP interpreter does not support any of the required database modules: 'mysql', 'mysqli', or 'pgsql'")

def check_modules ():
    errors = php_mods.check_modules (PHP_MOD_DEPENDENCIES)
    if errors:
        return errors[0]

    # GD 1 or 2
    alternatives = ('gd', 'gd2')
    errors = php_mods.check_modules (alternatives)
    if len(errors) == len(alternatives):
        return errors[-1]


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
        vphp = version_to_int ('5.2.8')
        assert ver >= vphp
    except:
        errors.append(('PHP Version', '>= 5.2.8', info.get('PHP Version')))

    # Mem limits
    try:
        memory = php.settings['memory_limit'].lower()
        memory = memory.replace('m','')
        assert float(memory) >= 40
    except:
        errors.append(('memory_limit', '>= 40M', php.settings.get('memory_limit')))

    # Settings
    check_compliance ('register_globals', 'Off')
    check_compliance ('safe_mode', 'Off')
    check_compliance ('session.save_handler', 'files')
    check_compliance ('magic_quotes_gpc', 'Off')
    check_compliance ('magic_quotes_runtime', 'Off')
    check_compliance ('file_uploads', 'On')
    check_compliance ('session.auto_start', 'Off')
    check_compliance ('session.bug_compat_warn', 'Off')

    return errors


def install_cli ():
    pre       = "tmp!market!install"

    root      = CTK.cfg.get_val ('%s!root' %(pre))
    webdir    = CTK.cfg.get_val ('%s!target!directory' %(pre),'').strip('/')
    vserver   = CTK.cfg.get_val ('%s!target!vserver'   %(pre),'').strip('/')

    dbtype    = CTK.cfg.get_val('%s!db!db_type' %(pre))
    dbname    = CTK.cfg.get_val('%s!db!db_name' %(pre))
    dbuser    = CTK.cfg.get_val('%s!db!db_user' %(pre))
    dbpass    = CTK.cfg.get_val('%s!db!db_pass' %(pre))

    fullname  = CTK.cfg.get_val('%s!moodle!fullname' %(pre))
    shortname = CTK.cfg.get_val('%s!moodle!shortname' %(pre))
    adminuser = CTK.cfg.get_val('%s!moodle!adminuser' %(pre))
    adminpass = CTK.cfg.get_val('%s!moodle!adminpass' %(pre))
    agreement = CTK.cfg.get_val('%s!moodle!agreement' %(pre))
    domain    = CTK.cfg.get_val('%s!moodle!domain'    %(pre),'').strip('/')

    # License
    if agreement != '1':
        market.Install_Log.log ("Moodle License must be accepted")
        raise ValueError, 'Moodle License must be accepted'

    # Port
    ports = []
    for b in CTK.cfg['server!bind'] or []:
        port = CTK.cfg.get_val ('server!bind!%s!port'%(b))
        if port:
            ports.append (port)

    # WWW root
    if domain:
        vserver = domain

    if not ports or '80' in ports:
        wwwroot = "http://%s" %(vserver)
    else:
        wwwroot = "http://%s:%s" %(vserver, ports[0])

    if webdir:
        wwwroot += '/%s' %(webdir)

    # DB
    if dbtype == 'postgresql':
        dbchoice = 'pgsql'
    elif dbtype == 'mysql':
        dbchoice = 'mysqli'
    else:
        market.Install_Log.log ("Unknown DB type specified")
        raise ValueError, 'Unidentified DB type specified'

    php_cli_bin = php.figure_phpcli_binary()

    cmd = CLI_COMMAND %(locals())

    market.Install_Log.log ("Performing CLI installation. Command: %s" %(cmd))

    ret = popen.popen_sync (cmd)
    if ret['retcode'] == 0:
        market.Install_Log.log ("Success: CLI installation OK")
    else:
        market.Install_Log.log ("Error: CLI installation Error.\n%s" %(ret['stderr']))

    return ret

# Validation functions
#
def validate_password (value):
    length, digits, lower, upper, nonalpha = False, False, False, False, False

    if len(value) >= 8: length = True
    for c in value:
        if c in string.digits:
            digits = True
        if c in string.lowercase:
            lower = True
        if c in string.uppercase:
            upper = True
        if c not in string.digits + string.letters:
            nonalpha = True

    errors = []
    if length   == False: errors.append(_('At least 8 characters required.'))
    if digits   == False: errors.append(_('At least 1 digit required.'))
    if lower    == False: errors.append(_('At least 1 lowercase letter required.'))
    if upper    == False: errors.append(_('At least 1 uppercase letter required.'))
    if nonalpha == False: errors.append(_('At least 1 non-alphanumeric character required.'))

    if errors:
        raise ValueError, ' '.join(errors)
    return value

def validate_username (value):
    if value != value.lower():
        raise ValueError, _('Only lower case letters allowed.')
    return value

def validate_agreement (value):
    if value != '1':
        raise ValueError, _('Must accept License')
    return value

def validate_domain (value):
    if value.lower() in ('default'):
        raise ValueError, _('The default nick name is not accessible as such from the Internet')
    if value.startswith('http:'):
        value = value.replace('http:', '')
    if value.startswith('https:'):
        value = value.replace('https:', '')
    value = value.strip('/')

    if '/' in value:
        raise ValueError, _('Web path must be omitted')

    return value
