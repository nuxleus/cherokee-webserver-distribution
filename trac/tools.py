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

import os
import market
import popen
from util import *

PYSQLITE_INSTRUCTIONS = {
    'apt':           "sudo apt-get install python-pysqlite2",
    'yum':           "sudo yum install python-devel sqlite-devel",
    'zypper':        "sudo zypper install sqlite-devel",
    'macports':      "sudo port install py-sqlite",
    'freebsd_pkg':   "pkg_add -r py26-sqlite3",
    'freebsd_ports': "cd /usr/ports/databases/py-sqlite3 && make install",
    'default':       N_("Either a Python interface to SQLite3, or Python development files + SQLite3 development files are needed.")
}

def fix_trac_ini (root):
    try:
        path = os.path.join (root, 'project', 'conf', 'trac.ini')
        config = open(path, 'r').read()
        config = config.replace('src = site/your_project_logo.png', 'src = trac_banner.png')
        open(path, 'w').write(config)
        market.Install_Log.log ('trac.ini successfully edited.')
        return True
    except:
        market.Install_Log.log ('trac.ini could not be edited successfully.')
        return False

def install_pysqlite (root, env):
    try:
        import sqlite3
        return {'retcode':0}
    except ImportError:
        pass

    if os.path.exists ('/usr/local/include/sqlite3.h'):
        try:
            cfg_file = '%(root)s/pysqlite-2.6.0/setup.cfg'%(locals())
            cfg = open (cfg_file, 'r').read()
            cfg = cfg.replace('#include_dirs', 'include_dirs')
            cfg = cfg.replace('#library_dirs', 'library_dirs')
            open (cfg_file, 'w').write (cfg)
        except IOError, e:
            market.Install_Log.log ("Error: setup.cfg for pysqlite could not be modified.")

    env = eval(env) # it comes in as a string to prevent problems reporting errors
    cd  = '%(root)s/pysqlite-2.6.0'%(locals())
    cmd = "python setup.py install --prefix=%(root)s" %(locals())
    ret = popen.popen_sync (command=cmd, env=env, cd=cd)

    if ret['retcode'] == 0:
        market.Install_Log.log ('Success: pysqlite built.')
    else:
        ibox = market.Util.InstructionBox('')
        inst = ibox.choose_instructions (PYSQLITE_INSTRUCTIONS)[0]
        msg  = _('The pysqlite module is not available and could not be built.') + '\n'
        msg  = _('The following command might aid in solving the issue.') + '\n'
        msg += inst + '\n'
        msg += '%s:\n' %(_('Error report'))
        msg += ret['stderr']

        ret['stderr'] = msg
        market.Install_Log.log ('Error: pysqlite not built.')

    return ret

