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
Ruby and Ruby Gem detection.
"""

import os
import re
import CTK
import popen
import market
from util import *

RUBY_PATHS = [
    '/usr/bin',
    '/usr/local/bin',
    '/opt/local/bin',
    '/opt/ruby*'
]

RUBY_BINS = [
    'ruby',
    'ruby1.9',
    'ruby1.8',
    'ruby1.7'
]

GEM_BINS = [
    'gem',
    'gem1.9',
    'gem1.8',
    'gem1.7'
]

RUBY18_NOTE  = N_('The Ruby 1.8 interpreter, RubyGems, or both, could not be found on your system. Please install Ruby 1.8 and RubyGems to proceed.') # generic message
RUBY18_INSTRUCTIONS = {
    'apt':           "sudo apt-get install ruby1.8 ruby1.8-dev rake rubygems1.8 libopenssl-ruby1.8",
    'yum':           "sudo yum install ruby rubygems ruby-mysql libmysqlclient-devel ruby-sqlite3",
    'zypper':        "sudo zypper install ruby rubygems ruby-mysql libmysqlclient-devel rubygem-sqlite3",
    'macports':      "sudo port install ruby",
    'freebsd_pkg':   "pkg_add -r ruby18-gems ruby18-iconv",
    'freebsd_ports': "cd /usr/ports/lang/ruby18 && make install && cd /usr/port/devel/ruby-gems && make install && cd /usr/ports/converters/ruby-iconv && make install",
    'ips':           "pfexec pkg install pkg:/runtime/ruby-18",
    'default':       N_("Ruby is available at http://www.ruby-lang.org/")
}

# TODO
# Decouple Ruby from RubyGems instructions
#

#
# Detection Ruby
#
_ruby_bin_cache   = None
_ruby_bin_checked = False

def detect_ruby (specific_version='', cache=False):
    """Detect Ruby interpreter. If a specific_version string is
    specified, it will only check for that version string. If the
    cache parameter is enabled, it will cache the results to avoid
    making redundant system calls on successive executions.

    detect_ruby() returns the absolute path to the binary of the
    interpreter found."""

    global _ruby_bin_cache
    global _ruby_bin_checked

    def ruby_bin_test (path_ruby):
        ret = popen.popen_sync ('%s -v'%(path_ruby), stdout=True, stderr=True)
        if specific_version:
            if not 'ruby %s'%(specific_version) in ret.get('stdout',''):
                return False
        return True

    # Cache miss
    if not _ruby_bin_checked or cache==False:
        _ruby_bin_checked = True
        _ruby_bin_cache   = path_find_binary (RUBY_BINS, RUBY_PATHS, ruby_bin_test)

    # Find the ruby binary
    return _ruby_bin_cache


def ruby_version ():
    """Report version of Ruby interpreter detected on the system.

    ruby_version() will return the version found, or nothing"""

    bin = detect_ruby()
    ret = popen.popen_sync ('%s -v'%(bin), stdout=True, stderr=True)
    tmp = re.findall ('ruby ([\d.]+)', ret.get('stdout',''))
    if tmp:
        return tmp[0]


#
# Detection Gem
#
_gem_bin_cache   = None
_gem_bin_checked = False

def detect_gem (specific_version='', cache=False):
    """Detect binary for Ruby Gems. If a specific_version string is
    specified, it will only check for that version string. If the
    cache parameter is enabled, it will cache the results to avoid
    making redundant system calls on successive executions.

    detect_gem() returns the absolute path to the binary found."""

    global _gem_bin_cache
    global _gem_bin_checked

    # Cache miss
    if not _gem_bin_checked or cache==False:
        _gem_bin_checked = True

        # Ruby path
        ruby_bin_path = detect_ruby (specific_version)
        if not ruby_bin_path:
            return None

        # Gem ought to be beside Ruby
        ruby_path = os.path.dirname (ruby_bin_path)
        for bin in GEM_BINS:
            gem_bin = os.path.join (ruby_path, bin)
            if os.access (gem_bin, os.X_OK):
                if specific_version:
                    ret = popen.popen_sync ('%s -v'%(gem_bin), stdout=True, stderr=True)
                    if not specific_version in ret.get('stdout',''):
                        continue
                _gem_bin_cache = gem_bin

    # Return the binary
    return _gem_bin_cache


if __name__ == '__main__':
    print "gem",  detect_gem()
    print "ruby", detect_ruby()
