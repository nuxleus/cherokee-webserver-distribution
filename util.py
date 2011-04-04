# -*- coding: utf-8 -*-
#
# Cherokee-distro
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
import subprocess

def run (command, want='output', print_stdout=False, cwd=None):
    print command
    p = subprocess.Popen (command, cwd=cwd, shell=True, stdout=subprocess.PIPE, close_fds=True)
    output = p.stdout.read()
    p.stdout.close()
    retcode = p.wait()

    if print_stdout:
        print output

    if want == 'output':
        return output
    return retcode

def cp (origin, target, if_not_equal=True):
    exists = True

    origin_stat = os.stat (origin)
    try:
        target_stat = os.stat (target)
    except:
        exists = False

    if (exists and
        origin_stat.st_size  == target_stat.st_size and
        origin_stat.st_ctime <= target_stat.st_ctime):
        print "cp '%s' '%s' - Skipped" %(origin, target)
        return 0

    cmd = "cp '%s' '%s'" %(origin, target)
    return run (cmd, want='retcode')

