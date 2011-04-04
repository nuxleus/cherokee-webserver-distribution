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
Interfaces for interacting with system services.
"""

import os
import re
import popen
import SystemInfo
from market import Install_Log

def _exe (cmd, error_msg):
    Install_Log.log ("  %s" %(cmd))

    ret = popen.popen_sync (cmd)
    if ret['retcode']:
        Install_Log.log ("  ERROR: %s" %(error_msg))
        ret['command'] = cmd
        ret['error']   = error_msg

    return ret


def register_service (service, macos_plist=None):
    """Register system service so that it is started at boot time. The
    name of the service should be provided. On MacOS X, an additional
    Launchd service file must be specified.

    register_service() returns a dictionary with the following keys:
     command: command
     retcode: return code of the execution of specified command. 0 on success.
     error:   error message
     stdout:  standard output of execution
     stderr:  error buffer of execution"""

    # System info retrival
    system_info = SystemInfo.get_info()
    OS     = system_info.get('system','').lower()
    distro = system_info.get('linux_distro_id','').lower()

    # Execute command
    error_msg = _('Could not add <em>%(service)s</em> to list of system services.') %(locals())

    if distro in ('fedora', 'redhat', 'centos', 'suse', 'opensuse'):
        ret = _exe ('chkconfig --add %(service)s'%(locals()), error_msg)
        if ret['retcode']: return ret

        ret = _exe ('chkconfig %(service)s on'%(locals()), error_msg)
        if ret['retcode']:
            return ret

        # Log (do not change string, check Maintenance.py)
        Install_Log.log ('Registered system service: %(service)s'%(locals()))

        return ret

    elif OS == 'linux':
        cmd = 'ln -s /etc/init.d/%(service)s /etc/rcS.d/S99%(service)s' %(locals())
        ret = _exe (cmd, error_msg)
        if ret['retcode']:
            return ret

        # Log (do not change string, check Maintenance.py)
        Install_Log.log ('Registered system service: %(service)s'%(locals()))

        return ret

    elif OS == 'darwin':
        assert macos_plist, "Launchd service file not provided"
        cmd = 'launchctl load %(macos_plist)s' %(locals())
        ret = _exe (cmd, error_msg)
        if ret['retcode']:
            return ret

        # Log (do not change string, check Maintenance.py)
        Install_Log.log ('Registered Launchd service: %(macos_plist)s' %(locals()))

        return ret

    elif OS == 'freebsd':
        # Find out variable name for rc (coded in init script)
        cmd = None
        for path in ('/usr/local/etc/rc.d', '/etc/rc.d'):
            if os.path.exists ('%(path)s/%(service)s' %(locals())) and \
                os.access ('%(path)s/%(service)s' %(locals()), os.X_OK):
                cmd = '%(path)s/%(service)s rcvar' %(locals())

        assert cmd, "Init script not present on /etc/rc.d or /usr/local/etc/rc.d"

        ret   = _exe (cmd, error_msg)
        rcvar = re.findall('^([^#].*)=', ret['stdout'], re.M)[0]

        # Read init file (to add or modify if entry already present)
        lines = open('/etc/rc.conf','r').readlines()
        content = ''
        for line in lines:
            if re.findall (r'%(rcvar)s=.+' %(locals()), line):
                content += '%(rcvar)s="YES"\n' %(locals())
            else:
                content += line

        if content == ''.join(lines):
            content += '%(rcvar)s="YES"\n' %(locals())

        # Write
        try:
            open('/etc/rc.conf','w').write (content)
            # Log (do not change string, check Maintenance.py)
            Install_Log.log ('Registered BSD service: %(rcvar)s'%(locals()))
        except:
            raise

        return ret

    assert False, 'Unknown platform: %s' %(str(system_info))


def launch_service (service):
    """Launch the system service specified as parameter.

    launch_service() returns a dictionary with the following keys:
     command: command
     retcode: return code of the execution of specified command. 0 on success.
     error:   error message
     stdout:  standard output of execution
     stderr:  error buffer of execution"""

    # System info retrival
    system_info = SystemInfo.get_info()
    OS     = system_info.get('system','').lower()
    distro = system_info.get('linux_distro_id','').lower()

    # Select the command
    if distro in ('fedora', 'redhat', 'centos', 'suse', 'opensuse'):
        cmd = 'service %(service)s start' %(locals())
    elif OS == 'linux':
        cmd = '/etc/init.d/%(service)s start' %(locals())
    elif OS == 'darwin':
        cmd = 'launchctl start %(service)s' %(locals())
    elif OS == 'freebsd':
        if os.path.isfile ('/usr/local/etc/rc.d/%(service)s' %(locals())):
            cmd = '/usr/local/etc/rc.d/%(service)s start' %(locals())
        else:
            cmd = '/etc/rc.d/%(service)s start' %(locals())

    # Execution
    ret = _exe (cmd, _('Could not launch <em>%(service)s</em> service.') %(locals()))
    return ret
