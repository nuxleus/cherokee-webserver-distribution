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
Detection of C development environment.
"""

import os
import CTK
import popen
import market
from util import *

CC_PATHS = [
    '/usr/bin',
    '/usr/local/bin',
    '/opt/local/bin',
    '/usr/ucb',
    '/opt/SUNWspro/bin'
]

CC_BINS = [
    'gcc',
    'cc',
]

CC_NOTE  = N_("Your system doesn't seem to provide the required dependecies. Please make sure there is a C development environment present.")
CC_INSTRUCTIONS = {
    'apt':      "sudo apt-get install build-essential",
    'zypper':   "sudo zypper install gcc glibc-devel",
    'yum':      "sudo yum install gcc glibc glibc-common",
    'macports': N_("MacOS X is shipped with a copy of GCC."),
    'default':  N_("GCC is available at http://gcc.gnu.org/")
}

#
# Detection CC
#
_cc_bin_cache   = None
_cc_bin_checked = False

def detect_cc (specific_version='', cache=False):
    """Detect binary for a C compiler. If a specific_version string is
    provided, the check will be restricted to a matching string in the
    binarie's output.  The cache parameter determines whether
    subsequent calls will reissue the detection commands or use a
    cached value.

    detect_cc() returns the absolute path to the binary found."""
    global _cc_bin_cache
    global _cc_bin_checked

    def cc_bin_test (path_cc):
        # Sometimes this outputs stdout info to stderr
        ret = popen.popen_sync ('%s -v'%(path_cc), stdout=True, stderr=True)

        if specific_version and not specific_version in ret.get('stdout','')+ret.get('stderr', ''):
            return False
        return True

    # Cache miss
    if not _cc_bin_checked or cache==False:
        _cc_bin_checked = True
        _cc_bin_cache   = path_find_binary (CC_BINS, CC_PATHS, cc_bin_test)

        if not _cc_bin_cache and cc_bin_test ('cc'):
            _cc_bin_cache = popen.popen_sync ('which cc')

    # Find the cc binary
    return _cc_bin_cache

if __name__ == '__main__':
    print "cc", detect_cc()
