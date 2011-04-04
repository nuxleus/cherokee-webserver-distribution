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
Interfaces for creating system users and groups
"""

import os
import pwd
import grp
import popen
import SystemInfo
from market import Install_Log

## MacOS X:
# dscl . -list /Groups - Lists groups
# dscl . -list /Users  - Lists users

def _exe (cmd, error_msg):
    """Wrap system calls, adding a reference to the executed command
    and possible error message to the returned value.

    exe() returns a dictionary with the following keys:
     command: command
     retcode: return code of the execution of specified command. 0 on
              success.
     error:   error message
     stdout:  standard output of execution
     stderr:  error buffer of execution"""

    Install_Log.log ("  %s" %(cmd))

    ret = popen.popen_sync (cmd)
    if ret['retcode']:
        Install_Log.log ("  ERROR: %s" %(error_msg))
        ret['command'] = cmd
        ret['error']   = error_msg

    return ret


# Exists
def user_exists (user):
    all_users = [x[0] for x in pwd.getpwall()]
    return user in all_users

def group_exists (group):
    all_groups = [x[0] for x in grp.getgrall()]
    return group in all_groups

def UID_exists (uid):
    all_UIDs = [x[2] for x in pwd.getpwall()]
    return uid in all_UIDs

def GID_exists (gid):
    all_GIDs = [x[2] for x in grp.getgrall()]
    return gid in all_GIDs

# to ID
def user_to_UID (user):
    for entry in pwd.getpwall():
        if user == entry[0]:
            return entry[2]
    assert False, "Did not find user '%s'" %(user)

def group_to_GID (group):
    for entry in grp.getgrall():
        if group == entry[0]:
            return entry[2]
    assert False, "Did not find group '%s'" %(group)

# Groups
def is_user_in_group (user, group):
    try:
        udata = pwd.getpwnam (user)
        gdata = grp.getgrnam (group)
    except KeyError:
        return False

    if (udata.pw_gid == gdata.gr_gid) or  udata.pw_name in gdata.gr_mem:
        return True

    return False

def find_new_UID (start=1000):
    all_UIDs = [x[2] for x in pwd.getpwall()]

    for n in xrange (start, 65535):
        if not n in all_UIDs:
            return n

    assert False, "Did not find a suitable UID"

def find_new_UID_GID_pair():
    GIDs = [x[2] for x in grp.getgrall()]
    UIDs = [x[2] for x in pwd.getpwall()]

    for n in xrange(1000,65535):
        if not n in GIDs and not n in UIDs:
            return n

    assert False, "Did not find a suitable ID"


def add_user_to_group (user, group, primary_group=True):
    """Add user to an existing group on the system, in a platform
    independent manner. Currently supports Linux, MacOS X, and
    FreeBSD. A primary group can be provided optionally, which will be
    used for MacOS X systems.

    Returns the result of a call to _exe()
    """
    # Error message
    error = _('Could not add <em>%(user)s</em> user to <em>%(group)s</em> group.') %(locals())

    # Build system command
    system_info = SystemInfo.get_info()
    OS = system_info.get('system','').lower()

    if OS == 'linux':
        cmd = '/usr/sbin/usermod -a -G %(group)s %(user)s' %(locals())
        ret = _exe (cmd, error)
        if ret['retcode'] == 2: # some distros don't need the -a parameter (some SUSE versions)
            return _exe (cmd.replace('/usermod -a -G', '/usermod -G'), error)
        return ret

    elif OS == 'darwin':
        if primary_group:
            id_group = group_to_GID (group)
            cmd = 'dscl localhost -create /Local/Default/Users/%(user)s PrimaryGroupID %(id_group)s' %(locals())
        else:
            cmd = 'dscl localhost -append /Groups/%(group)s GroupMembership %(user)s' %(locals())

        ret = _exe (cmd, error)
        return ret

    elif OS == 'freebsd':
        cmd = '/usr/sbin/pw usermod %(user)s -G %(group)s' %(locals())
        ret = _exe (cmd, error)
        return ret

    else:
        assert False, "Not implemented"


def add_group (group_name, group_id=None):
    """Add group to the system in a platform independent
    manner. Currently supports Linux, MacOS X, and FreeBSD. A group ID
    can be specified optionally.

    Returns the result of a call to _exe()
    """
    error_msg = _('Could not create group.')

    # Build system command
    system_info = SystemInfo.get_info()
    OS = system_info.get('system','').lower()

    if OS == 'linux':
        raw = '/usr/sbin/groupadd %(group_name)s'
        if group_id:
            raw += ' --gid %(group_id)s'
        cmd = raw %(locals())

        ret = _exe (cmd, error_msg)
        return ret

    elif OS == 'darwin':
        if not group_id:
            group_id  = find_new_UID_GID_pair()

        ret = _exe ('dscl . -create /Groups/%(group_name)s' %(locals()), error_msg)
        if ret['retcode']: return ret
        ret = _exe ('dscl . -create /Groups/%(group_name)s PrimaryGroupID %(group_id)s' %(locals()), error_msg)
        if ret['retcode']: return ret
        ret = _exe ('dscl . -create /Groups/%(group_name)s RecordName %(group_name)s' %(locals()), error_msg)
        if ret['retcode']: return ret

        return ret

    elif OS == 'freebsd':
        raw = '/usr/sbin/pw groupadd %(group_name)s'
        if group_id:
            raw += ' -g %(group_id)s'
        cmd = raw %(locals())

        ret = _exe (cmd, error_msg)
        return ret

    else:
        assert False, "Not implemented"


def add_user_and_group (user, **kw):
    """Add user and group to the system in a platform independent
    manner. Currently supports Linux, MacOS X, and FreeBSD. If only a
    user-name is specified, it will also be used as group-name. The
    following named arguments are taken into account: group, homedir,
    shell.

    Returns the result of a call to _exe()
    """

    assert user
    error_msg = _('Could not create user.')

    # Extract parameters
    group   = kw.get('group', user)
    homedir = kw.get('homedir')
    shell   = kw.get('shell')

    # Build system command
    system_info = SystemInfo.get_info()
    OS = system_info.get('system','').lower()

    if OS == 'linux':
        # Ensure group is present.
        if not group_exists (group):
            ret = add_group (group)
            if ret['retcode']:
                return ret

        # Create the user
        raw = '/usr/sbin/useradd --gid %(group)s -r %(user)s' # -r == --system, but --system is not supported everywhere
        if homedir:
            raw += ' -d %(homedir)s ' # --home-dir not recognized on SuSE
        if shell:
            raw += ' -s %(shell)s ' # --shell not recognized on SuSE
        cmd = raw %(locals())

        # Run it
        ret = _exe (cmd, error_msg)
        if ret['retcode']:
            return ret

    elif OS == 'darwin':
        # Take care of the GID
        if not group_exists (group):
            dual_id  = find_new_UID_GID_pair()
            id_user  = dual_id
            id_group = dual_id

            # Create Group
            ret = add_group (group, id_group)
            if ret['retcode']: return ret
        else:
            id_group = group_to_GID (group)

            # Figure the new UID
            if not UID_exists (id_group):
                id_user = id_group
            else:
                id_user = find_new_UID (start = id_group)

        # Create user
        shell = shell or '/usr/bin/false'
        base  = 'dscl localhost -create /Local/Default/Users/%(user)s'

        ret = _exe (base %locals(), error_msg)
        if ret['retcode']: return ret

        # Set user details
        ret = _exe ((base + ' UniqueID %(id_user)s') %locals(), error_msg)
        if ret['retcode']: return ret
        ret = _exe ((base + ' PrimaryGroupID %(id_group)s') %locals(), error_msg)
        if ret['retcode']: return ret
        ret = _exe ((base + ' RecordName %(user)s') %locals(), error_msg)
        if ret['retcode']: return ret
        ret = _exe ((base + ' UserShell %(shell)s') %locals(), error_msg)
        if ret['retcode']: return ret

    elif OS == 'freebsd':
        # Ensure group is present.
        if not group_exists (group):
            ret = add_group (group)
            if ret['retcode']:
                return ret

        # Create the user
        raw = '/usr/sbin/pw useradd %(user)s -g %(group)s'
        if homedir:
            raw += ' -d %(homedir)s '
        if shell:
            raw += ' -s %(shell)s '
        cmd = raw %(locals())

        # Run it
        ret = _exe (cmd, error_msg)
        return ret

    else:
        assert False, "Not implemented"

    return ret


