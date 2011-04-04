# -*- coding: utf-8 -*-
#
# Cherokee Distribution
#
# Authors:
#      Alvaro Lopez Ortega <alvaro@alobbs.com>
#
# Copyright (C) 2011 Alvaro Lopez Ortega
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of version 2 of the GNU General Public
# License as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#

"""
Module to configure PHP and retrieve PHP specific information.

The only relevant GUI elements can be accessed by binding an
Install_Stage to the php.URL_PHP_CONFIG_INTRO URL.

Example:
   target_wid.bind ('goto_next_stage', CTK.DruidContent__JS_to_goto (box.id, php.URL_PHP_CONFIG_INTRO))

Public functions for information retrieval include:
    get_info: retrieve PHP-configured rule.
    figure_phpcgi_binary: retrieve path for FastCGI PHP interpreter.
    figure_phpcli_binary: retrieve path for CLI PHP interpreter.
    figure_modules: find out available PHP modules.
    figure_php_information: find out all PHP settings.
    figure_php_user: find out user and group under which PHP should run.
    check_session_save_path: determine if configured user can store PHP sessions.
"""

import re
import os
import pwd
import CTK
import subprocess
import popen
import market

from util import *
from market.Install import Install_Stage
from market.Util import InstructionBox

PHP_DEFAULT_TIMEOUT        = '30'
SAFE_PHP_FCGI_MAX_REQUESTS = '490'

FPM_BINS = ['php-fpm', 'php5-fpm']
STD_BINS = ['php-cgi', 'php']
CLI_BINS = ['php']

DEFAULT_BINS  = FPM_BINS + STD_BINS

DEFAULT_PATHS = ['/usr/bin',
                 '/opt/php',
                 '/usr/php/bin',
                 '/usr/sfw/bin',
                 '/usr/gnu/bin',
                 '/usr/local/bin',
                 '/opt/local/bin',
                 '/usr/php/*.*/bin',
                 '/usr/pkg/libexec/cgi-bin',
                 # FPM
                 '/usr/sbin',
                 '/usr/local/sbin',
                 '/opt/local/sbin',
                 '/usr/gnu/sbin']

FPM_ETC_PATHS = ['/etc/php*/fpm/*.conf',
                 '/etc/php*/fpm/*.d/*',
                 '/etc/php*-fpm.d/*',
                 # Old php-fpm
                 '/etc/php*/fpm/php*fpm.conf',
                 '/usr/local/etc/php*fpm.conf',
                 '/opt/php*/etc/php*fpm.conf',
                 '/opt/local/etc/php*/php*fpm.conf',
                 '/etc/php*/*/php*fpm.conf',
                 '/etc/php*/php*fpm.conf']

STD_ETC_PATHS = ['/etc/php.ini',
                 '/etc/php.d/*',
                 '/etc/php*/cgi/php.ini',
                 '/usr/local/etc/php.ini',
                 '/opt/php*/etc/php.ini',
                 '/opt/local/etc/php*/php.ini',
                 '/etc/php*/*/php.ini',
                 '/etc/php*/php.ini',
                 '/usr/local/lib*/php.ini']

URL_PHP_CONFIG_INTRO = "/market/install/php/config/intro"
URL_PHP_CONFIG       = "/market/install/php/config"
URL_PHP_CONFIG_DONE  = "/market/install/php/config/done"

INSTALL_NOTE_P1 = N_('PHP is required for the application to run, but it does not seem to be available in your system. Please install a FastCGI-enabled PHP interpeter to proceed.')
INSTALL_NOTE_P2 = N_('You can check if your interpreter supports FastCGI by looking for the "fcgi" string in the output of the following command: php-cgi -v')

ERROR_USER_PERM = N_('The user running PHP has no write-access to the path specified by the PHP session.save_path setting. PHP sessions will not work until either the user or the PHP settings are changed.')
ERROR_USER_CONF = N_('The user configured to run PHP is not a valid user in your system')

PHP_INSTRUCTIONS = {
    'apt':           "sudo apt-get install php5-fpm  or  sudo apt-get install php5-cgi",
    'yum':           "sudo yum install php",
    'zypper':        "sudo zypper install php5-fastcgi",
    'macports':      "sudo port install php5 +fastcgi",
    'freebsd_pkg':   "pkg_add -r php5",
    'freebsd_ports': "cd /usr/ports/lang/php5 && make WITH_FASTCGI=yes WITH_FPM=yes install distclean",
    'ips':           "pfexec pkg install 'pkg:/web/php-52'",
    'default':       N_("PHP is available at http://www.php.net/ . Remember to add the --enable-fastcgi parameter to ./configure."),
}

#
# GUI
#

class PHP_Check_Intro (Install_Stage):
    def __safe_call__ (self):
        box = CTK.Box()
        box += CTK.RawHTML ('<h2>%s</h2>' %(_("Configuring PHP")))
        box += CTK.RawHTML ('<h1>%s</h1>' %(_("Detecting a suitable PHP interpreter")))
        box += CTK.RawHTML (js = CTK.DruidContent__JS_to_goto (box.id, URL_PHP_CONFIG))
        return box.Render().toStr()


class PHP_Interpreter_Not_Found_Widget (CTK.Box):
    def __init__ (self):
        CTK.Box.__init__ (self)

        self += InstructionBox (_(INSTALL_NOTE_P1), PHP_INSTRUCTIONS)
        self += CTK.RawHTML ('<p>%s</p>' %(_(INSTALL_NOTE_P2)))

class PHP_Interpreter_Not_Found (CTK.Box):
    def __init__ (self):
        CTK.Box.__init__ (self)

        self += CTK.RawHTML ('<h1>%s</h1>' %(_("Could not find the PHP interpreter")))
        self += PHP_Interpreter_Not_Found_Widget()

        buttons = CTK.DruidButtonsPanel()
        buttons += CTK.DruidButton_Goto (_('Check Again'), URL_PHP_CONFIG, do_submit=False)
        self += buttons

class PHP_Interpreter_Config_Error (CTK.Box):
    def __init__ (self):
        CTK.Box.__init__ (self, msg)

        self += CTK.RawHTML ('<h1>%s</h1>' %(_("Internal Error while configuring PHP")))
        self += CTK.RawHTML ('<p>%s</p>' %(msg))

class PHP_Check_Configure (Install_Stage):
    def __safe_call__ (self):
        box = CTK.Box()

        # Figure the VServer it's working on?
        target_vserver_n = CTK.cfg.get_val('tmp!market!install!target!vserver_n')
        pre = 'vserver!%s' %(target_vserver_n)

        # Gather information
        source = _find_source()
        rule   = _find_rule (pre)

        # Add source if needed
        if not source:
            php_path = figure_phpcgi_binary()
            if not php_path:
                box += PHP_Interpreter_Not_Found()
                return box.Render().toStr()

            # Add the source! entry
            php_bin = php_path.split('/')[-1]
            if not php_bin in FPM_BINS:
                ret_source = _source_add_std (php_path)
            else:
                ret_source = _source_add_fpm (php_path)

            if ret_source.has_key('error'):
                box += PHP_Interpreter_Config_Error (ret_source['error'])
                return box.Render().toStr()

            source = _find_source()

        # Figure the timeout limit
        interpreter = CTK.cfg.get_val ('%s!interpreter'%(source))
        timeout     = CTK.cfg.get_val ('%s!timeout'    %(source))

        if not timeout:
            if not interpreter:
                timeout = PHP_DEFAULT_TIMEOUT
            elif 'fpm' in interpreter:
                timeout = _figure_fpm_settings()['timeout']
            else:
                timeout = _figure_std_settings()['timeout']

        # Add a new Extension PHP rule
        if not rule:
            next = CTK.cfg.get_next_entry_prefix('%s!rule'%(pre))
            src_num = source.split('!')[-1]

            CTK.cfg['%s!match' %(next)]                     = 'extensions'
            CTK.cfg['%s!match!extensions' %(next)]          = 'php'
            CTK.cfg['%s!match!check_local_file' %(next)]    = '1'
            CTK.cfg['%s!match!final' %(next)]               = '0'
            CTK.cfg['%s!handler' %(next)]                   = 'fcgi'
            CTK.cfg['%s!handler!balancer' %(next)]          = 'round_robin'
            CTK.cfg['%s!handler!balancer!source!1' %(next)] = src_num
            CTK.cfg['%s!handler!error_handler' %(next)]     = '1'
            CTK.cfg['%s!encoder!gzip' %(next)]              = '1'
            CTK.cfg['%s!timeout' %(next)]                   = timeout

        # Index files
        indexes = filter (None, CTK.cfg.get_val ('%s!directory_index' %(pre), '').split(','))
        if not 'index.php' in indexes:
            indexes.append ('index.php')
            CTK.cfg['%s!directory_index' %(pre)] = ','.join(indexes)

        # Normalization
        CTK.cfg.normalize('%s!rule'%(pre))

        # It's done, move on
        box += CTK.RawHTML (js = CTK.DruidContent__JS_to_goto (box.id, URL_PHP_CONFIG_DONE))
        return box.Render().toStr()


CTK.publish ('^%s$'%(URL_PHP_CONFIG_INTRO), PHP_Check_Intro)
CTK.publish ('^%s$'%(URL_PHP_CONFIG),       PHP_Check_Configure)


#
# Public
#

def get_info (key):
    """Given the prefix for a branch of the configuration tree, return
    a dictionary containing 'rule' and 'source'. Namely, the rule and
    information source for PHP under the specified branch."""
    rule   = _find_rule (key)
    source = _find_source ()

    rule_num = rule.split('!')[-1]

    return {'source': source, # cfg path
            'rule':   rule}   # cfg path

def figure_phpcgi_binary():
    """Return path of the FastCGI enabled PHP interpreter, if it
    exists."""
    return path_find_binary (DEFAULT_BINS,
                             extra_dirs  = DEFAULT_PATHS,
                             custom_test = _test_php_fcgi)

def figure_phpcli_binary():
    """Return path of the CLI PHP interpreter, if it exists."""
    return path_find_binary (CLI_BINS,
                             extra_dirs  = DEFAULT_PATHS,
                             custom_test = _test_php_cli)

def figure_modules():
    """Return list of modules available to PHP"""
    php_path = figure_phpcgi_binary()
    ret = popen.popen_sync ('%s -m' %(php_path))
    modules = re.findall('(^[a-zA-Z0-9].*$)', ret['stdout'], re.MULTILINE)
    return modules


def figure_php_information():
    """Parse PHP settings into a dictionary"""
    php_path = figure_phpcgi_binary()
    ret = popen.popen_sync ('%s -i' %(php_path))

    # Output can either be in HTML format or as a PHP array.
    if 'Content-type: text/html' in ret['stdout']:
        regex = """^<tr><td class="e">(.*?)</td><td class="v">(.*?)</td>(.*?)</tr>$"""
    else:
        regex = """^(.*?) => (.*?)( => .*)?$"""

    settings = {}
    tags     = re.compile(r'<.*?>')
    matches  = re.findall(regex, ret['stdout'], re.MULTILINE)

    for setting in matches:
        key, val = setting[0].strip(), setting[1].strip()
        val = tags.sub('', val)
        settings[key] = val

    # Double check PHP Version (sometimes previous pattern differs)
    if not settings.get('PHP Version'):
        tmp = re.findall('PHP Version.+(\d+\.\d+\.\d+)',ret['stdout'])
        if tmp:
            settings['PHP Version'] = tmp[0]

    return settings


def figure_php_user (pre_vsrv):
    """Determine PHP user/group accounting for config file, source UID, and server UID"""

    server_user  = CTK.cfg.get_val ('server!user',  str(os.getuid()))
    server_group = CTK.cfg.get_val ('server!group', str(os.getgid()))
    php_info     = get_info (pre_vsrv)
    interpreter  = CTK.cfg.get_val ('%s!interpreter' %(php_info['source']), '')

    if 'fpm' in interpreter:
        fpm_conf  = _figure_fpm_settings()
        php_user  = fpm_conf.get('user',  server_user)
        php_group = fpm_conf.get('group', server_group)
    else:
        php_user  = CTK.cfg.get_val ('%s!user'  %(php_info['source']), server_user)
        php_group = CTK.cfg.get_val ('%s!group' %(php_info['source']), server_group)

    return {'php_user':  php_user,
            'php_group': php_group}


def check_session_save_path (pre_vsrv):
    """Check if the PHP interpreter can store sessions with the configured user"""
    user = figure_php_user (pre_vsrv)
    info = figure_php_information()
    path = info.get('session.save_path')
    bin  = figure_phpcgi_binary()

    try:
        php_uid = pwd.getpwnam (user['php_user']).pw_uid
    except:
        return {'ret': 'error',
                'error': _(ERROR_USER_CONF),
                'path': path}

    ret = popen.popen_sync ("LC_ALL=C echo '<?php session_start(); ?>' | %s"%(bin), su=php_uid)
    if "Failed" in ret['stdout']:
        return {'ret': 'fail',
                'error': _(ERROR_USER_PERM),
                'path': path}

    return {'ret':'ok'}

#
# Private
#

def _find_source():
    for binary in FPM_BINS + STD_BINS:
        source = cfg_source_find_interpreter (binary)
        if source:
            return source

def _find_rule (key):
    return cfg_vsrv_rule_find_extension (key, 'php')


def _figure_std_settings():
    # Find config file
    paths = []
    for p in STD_ETC_PATHS:
        paths.append (p)
        paths.append ('%s-*' %(p))

    std_info = {}

    # For each configuration file
    for conf_file in path_eval_exist (paths):
        # Read
        try:
            content = open (conf_file, 'r').read()
        except:
            continue

        # Timeout
        if not std_info.get('timeout'):
            tmp = re.findall (r'^max_execution_time\s*=\s*(\d*)', content)
            if tmp:
                std_info['timeout'] = tmp[0]

            # Config file
            if not std_info.get('conf_file'):
                std_info['conf_file'] = conf_file

    # Set last minute defaults
    if not std_info.get('timeout'):
        std_info['timeout'] = PHP_DEFAULT_TIMEOUT

    if not std_info.get('listen'):
        std_info['listen'] = cfg_source_get_localhost_addr()

    return std_info


def _figure_fpm_settings():
    # Find config file
    paths = []
    for p in FPM_ETC_PATHS:
        paths.append (p)
        paths.append ('%s-*' %(p))

    fpm_info = {}

    # For each configuration file
    for conf_file in path_eval_exist (paths):
        # Read
        try:
            content = open (conf_file, 'r').read()
        except:
            continue

        # Listen
        if not fpm_info.get('listen'):
            tmp = re.findall (r'<value name="listen_address">(.*?)</value>', content)
            if tmp:
                fpm_info['listen'] = tmp[0]
            else:
                tmp = re.findall (r'^listen *= *(.+)$', content, re.M)
                if tmp:
                    fpm_info['listen']  = tmp[0]

        # Timeout
        if not fpm_info.get('timeout'):
            tmp = re.findall (r'<value name="request_terminate_timeout">(\d*)s*</value>', content)
            if tmp:
                fpm_info['timeout'] = tmp[0]
            else:
                tmp = re.findall (r'^request_terminate_timeout *= *(\d*)s*', content, re.M)
                if tmp:
                    fpm_info['timeout'] = tmp[0]

        # Filename
        if not fpm_info.get('conf_file'):
            if '.conf' in conf_file:
                fpm_info['conf_file'] = conf_file

        # User
        if not fpm_info.get('user'):
            tmp = re.findall (r'<value name="user">(.*?)</value>', content)
            if tmp:
                fpm_info['user'] = tmp[0]
            else:
                tmp = re.findall (r'^user *= *(.*)$', content, re.M)
                if tmp:
                    fpm_info['user'] = tmp[0]

        # Group
        if not fpm_info.get('group'):
            tmp = re.findall (r'<value name="group">(.*?)</value>', content)
            if tmp:
                fpm_info['group'] = tmp[0]
            else:
                tmp = re.findall (r'^group *= *(.*)$', content, re.M)
                if tmp:
                    fpm_info['group'] = tmp[0]

    # Set last minute defaults
    if not fpm_info.get('timeout'):
         fpm_info['timeout'] = PHP_DEFAULT_TIMEOUT

    if not fpm_info.get('listen'):
         fpm_info['listen'] = "127.0.0.1"

    return fpm_info


def _source_add_std (php_path):
    # Read settings
    std_info = _figure_std_settings()
    if not std_info:
        return {'error': (_('Could not determine PHP-CGI settings.'))}

    if not std_info.has_key('conf_file'):
        return {'error': (_('Could not determine PHP-CGI configuration file.'))}

    # IANA: TCP ports 47809-47999 are unassigned
    TCP_PORT = 47990
    host     = std_info['listen']

    # Add the Source
    next = CTK.cfg.get_next_entry_prefix('source')

    CTK.cfg['%s!nick'          %(next)] = 'PHP Interpreter'
    CTK.cfg['%s!type'          %(next)] = 'interpreter'
    CTK.cfg['%s!host'          %(next)] = '%(host)s:%(TCP_PORT)d' %(locals())
    CTK.cfg['%s!interpreter'   %(next)] = '%(php_path)s -b %(host)s:%(TCP_PORT)d' %(locals())
    CTK.cfg['%s!env_inherited' %(next)] = '0'

    CTK.cfg['%s!env!PHP_FCGI_MAX_REQUESTS' %(next)] = SAFE_PHP_FCGI_MAX_REQUESTS
    CTK.cfg['%s!env!PHP_FCGI_CHILDREN'     %(next)] = '5'

    return {'new_source': next}


def _source_add_fpm (php_path):
    # Read settings
    fpm_info = _figure_fpm_settings()
    if not fpm_info:
        return {'error' : (_('Could not determine PHP-fpm settings.'))}

    host      = fpm_info['listen']
    conf_file = fpm_info['conf_file']

    # Add Source
    next = CTK.cfg.get_next_entry_prefix('source')

    CTK.cfg['%s!nick'        %(next)] = 'PHP Interpreter'
    CTK.cfg['%s!type'        %(next)] = 'interpreter'
    CTK.cfg['%s!host'        %(next)] = host
    CTK.cfg['%s!interpreter' %(next)] = '%(php_path)s --fpm-config %(conf_file)s' %(locals())

    # In case FPM has specific UID/GID and differs from Cherokee's,
    # the interpreter must by spawned by root.
    #
    server_user  = CTK.cfg.get_val ('server!user',  str(os.getuid()))
    server_group = CTK.cfg.get_val ('server!group', str(os.getgid()))

    root_user    = market.InstallUtil.get_installation_UID()
    root_group   = market.InstallUtil.get_installation_GID()
    php_user     = fpm_info.get('user',  server_user)
    php_group    = fpm_info.get('group', server_group)

    if php_user != server_user or php_group != server_group:
        CTK.cfg['%s!user'  %(next)] = root_user
        CTK.cfg['%s!group' %(next)] = root_group

    return {'new_source': next}


def _test_php_fcgi (path):
    f = os.popen('%s -v' %(path), 'r')
    output = f.read()
    try: f.close()
    except: pass
    return 'fcgi' in output


def _test_php_cli (path):
    f = os.popen('%s -v' %(path), 'r')
    output = f.read()
    try: f.close()
    except: pass
    return 'cli' in output
