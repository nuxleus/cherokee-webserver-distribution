#
# Copyright (c) 2010, Octality S.L. - Eume 6, Villaviciosa de Odon,
# 28670 Madrid, SPAIN. All rights reserved.
#
# Any unauthorized dissemination, distribution or copying is strictly
# forbidden.
#

"""
Detection of C++ development environment.
"""

import os
import CTK
import popen
import market
from util import *

CPP_PATHS = [
    '/usr/bin',
    '/usr/local/bin',
    '/opt/local/bin',
    '/usr/ucb',
    '/opt/SUNWspro/bin'
]

CPP_BINS = [
    'g++',
    'c++',
]


CPP_NOTE  = N_("Your system doesn't seem to provide the required dependecies. Please make sure there is a C++ development environment present.")
CPP_INSTRUCTIONS = {
    'apt':      "sudo apt-get install g++",
    'yum':      "sudo yum install gcc-c++",
    'zypper':   "sudo zypper install gcc-c++",
    'macports': N_("MacOS X is shipped with a copy of the GNU C++ compiler."),
    'default':  N_("GCC is available at http://gcc.gnu.org/")
}

#
# Detection CPP
#
_cpp_bin_cache   = None
_cpp_bin_checked = False

def detect_cpp (specific_version='', cache=False):
    """Detect binary for a C++ compiler. If a specific_version string
    is provided, the check will be restricted to a matching string in
    the binarie's output.  The cache parameter determines whether
    subsequent calls will reissue the detection commands or use a
    cached value.

    detect_cpp() returns the absolute path to the binary found."""
    global _cpp_bin_cache
    global _cpp_bin_checked

    def cpp_bin_test (path_cpp):
        # Sometimes this outputs stdout info to stderr
        ret = popen.popen_sync ('%s -v'%(path_cpp), stdout=True, stderr=True)

        if specific_version and not specific_version in ret.get('stdout','')+ret.get('stderr', ''):
            return False
        return True

    # Cache miss
    if not _cpp_bin_checked or cache==False:
        _cpp_bin_checked = True
        _cpp_bin_cache   = path_find_binary (CPP_BINS, CPP_PATHS, cpp_bin_test)

        if not _cpp_bin_cache and cpp_bin_test ('c++'):
            _cpp_bin_cache = popen.popen_sync ('which c++')

    # Find the cc binary
    return _cpp_bin_cache

if __name__ == '__main__':
    print "c++", detect_cpp()
