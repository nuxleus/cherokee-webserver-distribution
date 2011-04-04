#
# Copyright (c) 2010, Octality S.L. - Eume 6, Villaviciosa de Odon,
# 28670 Madrid, SPAIN. All rights reserved.
#
# Any unauthorized dissemination, distribution or copying is strictly
# forbidden.
#

import os
import re
import sys
import CTK
import popen
import market
import validations

from util import *
from market.Install import Install_Stage
from market.CommandProgress import CommandProgress

# Load required modules
target = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "target.pyo"), "target_util")
tools  = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "tools.pyo"),  "tools_util")
python = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "python.pyo"), "python_util")

POST_UNPACK_COMMANDS = [
    ({'command': 'mv ${app_root}/WsgiDAV-0.4.0b2 ${app_root}/wsgidav'}),
    ({'command': 'mv ${app_root}/uwsgi-0.9.6.5 ${app_root}/uwsgi'}),
    ({'command': 'chmod o+rx ${app_root}/uwsgi'}),
    ({'command': 'chown -R ${root_user}:${root_group} ${app_root}'}),
]

ERROR_DEPENDENCIES = N_('There was an error during the installation of the required dependencies.')
ERROR_RETRY        = N_('Please try again if the problem can be solved manually by issuing the following command.')
NOTE_DAV_CONFIG    = N_('The default installation will allow anonymous access to a predefined path of your choosing. This can be changed later on.')
NOTE_DIRECTORY     = N_('This is the path to the local directory that will be exported via WebDAV.')

# Cfg chunks
SOURCE = """
source!%(src_num)d!type = interpreter
source!%(src_num)d!nick = WsgiDAV %(src_num)d
source!%(src_num)d!host = %(localhost)s:%(src_port)d
source!%(src_num)d!interpreter = %(root)s/uwsgi/uwsgi -x %(root)s/uwsgi/wsgidav.xml
source!%(src_num)d!env!PYTHONPATH = %(root)s/wsgidav/installation
source!%(src_num)d!env_inherited = 0
"""

CONFIG_VSERVER = SOURCE + """
%(pre_vsrv)s!nick = %(target_vserver)s
%(pre_vsrv)s!document_root = /dev/null

%(pre_vsrv)s!rule!1!handler = uwsgi
%(pre_vsrv)s!rule!1!handler!balancer = round_robin
%(pre_vsrv)s!rule!1!handler!balancer!source!1 = %(src_num)d
%(pre_vsrv)s!rule!1!handler!in_allow_keepalive = 1
%(pre_vsrv)s!rule!1!match = default
"""

CONFIG_DIR = SOURCE + """
%(pre_rule_plus1)s!match = directory
%(pre_rule_plus1)s!match!directory = %(target_directory)s
%(pre_rule_plus1)s!handler = uwsgi
%(pre_rule_plus1)s!handler!balancer = round_robin
%(pre_rule_plus1)s!handler!balancer!source!1 = %(src_num)d
%(pre_rule_plus1)s!handler!in_allow_keepalive = 1
"""

URL_PRECONDITION  = market.Install.URL_INSTALL_SETUP_EXTERNAL
URL_TARGET        = "/market/install/wsgidav/target"
URL_INSTALL       = "/market/install/wsgidav/install"
URL_DAV_CONFIG    = "/market/install/wsgidav/dav"
URL_SERVER_CONFIG = "/market/install/wsgidav/server"
URL_APPLY         = "/market/install/wsgidav/apply"

## Preconditions
class Precondition (Install_Stage):
    def __safe_call__ (self):
        box = CTK.Box()
        box += CTK.RawHTML ('<h2>%s</h2>' %(_("Checking Dependencies")))

        error_cc  = tools.check_cc()
        error_py  = python.detect_python ("2.5.0", or_greater=True)
        error_xml = tools.check_xml2config ()

        if error_cc:
            note, inst = error_cc
        elif error_py:
            note, inst = error_py
        elif error_xml:
            note, inst = error_xml
        else:
            box += CTK.RawHTML (js = CTK.DruidContent__JS_to_goto (box.id, URL_TARGET))
            return box.Render().toStr()

        box += market.Util.InstructionBox (_(note), inst)
        buttons = CTK.DruidButtonsPanel()
        buttons += CTK.DruidButton_Close(_('Cancel'))
        buttons += CTK.DruidButton_Goto (_('Retry'), URL_PRECONDITION, do_submit=True)
        return box.Render().toStr()


## Target
class Target (Install_Stage):
    def __safe_call__ (self):
        box = CTK.Box()
        target_wid = target.TargetSelection()
        target_wid.bind ('goto_next_stage', CTK.DruidContent__JS_to_goto (box.id, URL_INSTALL))
        box += target_wid

        buttons = CTK.DruidButtonsPanel()
        buttons += CTK.DruidButton_Close(_('Cancel'))
        buttons += CTK.DruidButton_Submit (_('Next'), do_close=False)
        box += buttons

        return box.Render().toStr()


## Installation
class Installation (Install_Stage):
    def __safe_call__ (self):
        pre  = 'tmp!market!install'
        root = CTK.cfg.get_val ('%s!root' %(pre))

        # Paths
        dirpath = os.path.join (root,    'wsgidav')
        envpath = os.path.join (dirpath, 'installation')

        # Python interpreter
        py_interpreter = python.find_python("2.5", or_greater=True)

        # Create path
        ret = popen.popen_sync ('%(py_interpreter)s setup.py install --prefix=%(envpath)s'%(locals()), cd = '%(root)s/setuptools-0.6c11'%(locals()))

        err = ret['stderr']
        tmp = re.findall (r' (%(root)s.+site-packages)'%(locals()), err)

        if tmp:
            PYTHONPATH = tmp[0]
        else:
            # Something like {root}/wsgidav/installation/lib/python2.5/site-packages/
            py_version = 'pyton' + '.'.join (map(str, sys.version_info[0:2]))
            PYTHONPATH = os.path.join (envpath, lib, py_version, site-packages)

        os.makedirs (PYTHONPATH)

        # Python path
        env = os.environ.copy()
        if 'PYTHONPATH' in env:
            env['PYTHONPATH'] = '%s:%s:%s' %(envpath, PYTHONPATH, env['PYTHONPATH'])
        else:
            env['PYTHONPATH'] = '%s:%s' %(envpath, PYTHONPATH)

        # Commands
        tasks = [
            # Setuptools
            ({'command': "${py_interpreter} setup.py install --prefix=${envpath}",      'env': env, 'cd': '%(root)s/setuptools-0.6c11' %(locals())}),
            # uWSGI
            ({'command': "${py_interpreter} uwsgiconfig.py --build",                    'env': env, 'cd': os.path.join (root, 'uwsgi')}),
            # WSGIDav
            ({'command': "${py_interpreter} setup.py develop --install-dir=${envpath}", 'env': env, 'cd': dirpath})]

        box  = CTK.Box()
        box += CTK.RawHTML ('<h2>%s</h2>' %(_('Installing WsgiDAV')))
        box += CTK.RawHTML ('<p>%s</p>'   %(_('This process may take a while. Please, hold on.')))

        command = CommandProgress (tasks, URL_DAV_CONFIG)
        command['envpath']        = envpath
        command['dirpath']        = dirpath
        command['py_interpreter'] = py_interpreter
        box += command

        return box.Render().toStr()


## DAV configuration
class Dav_Config (Install_Stage):
    def __safe_call__ (self):
        box     = CTK.Box()
        buttons = CTK.DruidButtonsPanel()

        pre     = "tmp!market!install"
        submit  = CTK.Submitter (URL_APPLY)
        table   = CTK.PropsTable()
        table.Add (_('Local directory'), CTK.TextCfg('%s!webdav_dir'%(pre), False, {'class':'noauto'}), _(NOTE_DIRECTORY))
        submit += table
        submit.bind ('submit_success', CTK.DruidContent__JS_to_goto (box.id, URL_SERVER_CONFIG))

        box += CTK.RawHTML ('<h2>%s</h2>' %(_('WsgiDAV configuration')))
        box += CTK.RawHTML ('<p>%s</p>' %(_(NOTE_DAV_CONFIG)))
        box += submit

        buttons += CTK.DruidButton_Close(_('Cancel'))
        buttons += CTK.DruidButton_Submit (_('Next'), do_close=False)
        box += buttons

        return box.Render().toStr()


## Cherokee configuration
class Server_Config (Install_Stage):
    def __safe_call__ (self):
        box = CTK.Box()
        pre = 'tmp!market!install'

        # Replacements
        app_id           = CTK.cfg.get_val ('%s!app!application_id'  %(pre))
        app_name         = CTK.cfg.get_val ('%s!app!application_name'%(pre))
        root             = CTK.cfg.get_val ('%s!root'                %(pre))
        target_type      = CTK.cfg.get_val ('%s!target'              %(pre))
        target_vserver   = CTK.cfg.get_val ('%s!target!vserver'      %(pre))
        target_vserver_n = CTK.cfg.get_val ('%s!target!vserver_n'    %(pre))
        target_directory = CTK.cfg.get_val ('%s!target!directory'    %(pre))
        pre_vsrv         = 'vserver!%s' %(target_vserver_n)

        webdav_dir       = CTK.cfg.get_val ('%s!webdav_dir'          %(pre))
        user             = CTK.cfg.get_val ('%s!user'                %(pre))
        password         = CTK.cfg.get_val ('%s!password'            %(pre))

        src_num, x       = cfg_source_get_next()
        src_port         = cfg_source_find_free_port()
        localhost        = cfg_source_get_localhost_addr()

        # More replacements
        next_rule = CTK.cfg.get_next_entry_prefix('%s!rule'%(pre_vsrv))
        props = cfg_get_surrounding_repls ('pre_rule', next_rule)
        props.update (locals())
        tools.create_xml (root, localhost, src_port, webdav_dir)

        # Apply the config
        if target_type == 'vserver':
            config = CONFIG_VSERVER%(props)
            CTK.cfg.apply_chunk (config)

        elif target_type == 'directory':
            config = CONFIG_DIR %(props)
            CTK.cfg.apply_chunk (config)
            CTK.cfg.normalize ('%s!rule'%(pre_vsrv))

        # Redirect to the Thanks page
        box += CTK.RawHTML (js = CTK.DruidContent__JS_to_goto (box.id, market.Install.URL_INSTALL_DONE))
        return box.Render().toStr()

VALIDATION = [
    ('tmp!market!install!webdav_dir', validations.is_local_dir_exists),
]

CTK.publish ('^%s$'%(URL_PRECONDITION),  Precondition)
CTK.publish ('^%s$'%(URL_TARGET),        Target)
CTK.publish ('^%s$'%(URL_INSTALL),       Installation)
CTK.publish ('^%s$'%(URL_DAV_CONFIG),    Dav_Config)
CTK.publish ('^%s$'%(URL_SERVER_CONFIG), Server_Config)

# POST
CTK.publish ('^%s$'%(URL_APPLY),         CTK.cfg_apply_post, validation=VALIDATION, method="POST")
