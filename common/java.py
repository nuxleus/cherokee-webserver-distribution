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
Detection of Java binaries in the system.
"""

import os
import popen
from util import *

JAVA_BINS = [
    'java',
]

JAVA_PATHS = [
    '/usr/bin',
    '/usr/local/bin',
    '/opt/local/bin',
    '/opt/ruby*'
]

JAVA6_NOTE = N_("Your system doesn't seem to provide the required dependecies. Java 6 or later is required.")
JAVA6_INSTRUCTIONS = {
    'apt':           "sudo apt-get install sun-java6-jdk",
    'yum':           "yum install java-1.6.0-openjdk",
    'zypper':        "sudo zypper install java-1_6_0-sun",
    'macports':      "sudo port install openjdk6",
    'freebsd_pkg':   "pkg_add -r linux-sun-jdk16",
    'freebsd_ports': "cd /usr/ports/java/linux-sun-jdk16 && make install",
    'default':       N_('Please, install Java in your system')
}

#
# Detection Java
#
_java_bin_cache   = None
_java_bin_checked = False


def detect_java (specific_version='', cache=False):
    """Report Java binary of specified version. The cache parameter
    determines whether subsequent calls will reissue the detection
    commands or use a cached value.

    detect_java() returns the absolute path to the Java binary
    found."""
    global _java_bin_cache
    global _java_bin_checked

    def java_bin_test (path_java):
        # Sometimes this outputs stdout info to stderr
        ret = popen.popen_sync ('%s -version'%(path_java), stdout=True, stderr=True)

        output = ret.get('stdout','') + ret.get('stderr', '')
        if specific_version and not specific_version in output:
            return False
        return True

    # Cache miss
    if not _java_bin_checked or cache==False:
        _java_bin_checked = True
        _java_bin_cache   = path_find_binary (JAVA_BINS, JAVA_PATHS, java_bin_test)

    # Find the java binary
    return _java_bin_cache


def detect_java_home (specific_version=''):
    """Report JAVA_HOME for the system. If a specific_version string
    is provided, the check is restricted to that version only.

    detect_java_home() returns the absolute path found for
    JAVA_HOME."""

    # MacOS X
    MacOS_JAVA_HOME = "/System/Library/Frameworks/JavaVM.framework/Home"
    if os.path.exists (MacOS_JAVA_HOME):
        return MacOS_JAVA_HOME

    # Java binary
    java_bin = detect_java (specific_version)

    # Resolve symlinks
    while True:
        try:
            java_bin = os.readlink (java_bin)
        except OSError:
            break

    # A little bit of heuristic. Binary isn't always called java
    if java_bin.endswith('javavm'):
        java_home = java_bin.replace ("bin/javavm",'')
    else:
        java_home = java_bin.replace ("bin/java",'')
    return java_home


if __name__ == '__main__':
    print "java", detect_java()
    print "JAVA_HOME", detect_java_home()
