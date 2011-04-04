#
# Copyright (c) 2010, Octality S.L. - Eume 6, Villaviciosa de Odon,
# 28670 Madrid, SPAIN. All rights reserved.
#
# Any unauthorized dissemination, distribution or copying is strictly
# forbidden.
#

"""
Detection of Python interpreter in the system.
"""

import os
import re
import CTK
import popen
import market
from util import *

PYTHON_BINS = [
    'python',
    'python2',
    'python2.7',
    'python2.6',
    'python2.5',
    'python2.4',
]

DEFAULT_PATHS = [
    '/usr/bin',
    '/usr/sfw/bin',
    '/usr/gnu/bin',
    '/usr/local/bin',
    '/opt/local/bin',
    '/opt/python*/bin',
    '/usr/local/python*/bin',
    '/usr/python*/bin',
]


PYTHON_NOTE = N_("Python %(version2)s or later is required.")
PYTHON_INST = {
    'apt':           "sudo apt-get install python%(version2)s",
    'yum':           "sudo yum install python",
    'zypper':        "sudo zypper install python",
    'macports':      "sudo port install python%(version2s)s",
    'freebsd_pkg':   "pkg_add -r python%(version2s)s",
    'freebsd_ports': "cd /usr/ports/lang/python%(version2s)s && make install",
    'default':       N_('Please, install Python %(version2)s in your system: http://www.python.com/')
}


def _is_bin_version (bin, required_version):
    ret = popen.popen_sync ("'%s' -V"%(bin))

    tmp = re.findall (r'Python ([\d.]+)', ret['stderr'], re.M)
    if not tmp: return

    v_int = version_to_int (tmp[0])
    r_int = version_to_int (required_version)

    return v_int >= r_int


def _test_py24(s):
    return _is_bin_version (s, '2.4.0')

def _test_py25(s):
    return _is_bin_version (s, '2.5.0')

def _test_py26(s):
    return _is_bin_version (s, '2.6.0')

def _test_py27(s):
    return _is_bin_version (s, '2.7.0')


def find_python (version, or_greater):
    """Report Python interpeter of specified version. The or_greater
    parameter indicates whether higher versions should also be
    accepted or not.

    find_python() returns the absolute path to the binary of the
    interpreter found."""

    tmp = version.split('.')
    ver = int(''.join(tmp[0:2]))

    if ver <= 27 or or_greater:
        python27 = path_find_binary (PYTHON_BINS,
                                     extra_dirs  = DEFAULT_PATHS,
                                     custom_test = _test_py27)
        if python27:
            return python27

    if ver <=26 or or_greater:
        python26 = path_find_binary (PYTHON_BINS,
                                     extra_dirs  = DEFAULT_PATHS,
                                     custom_test = _test_py26)
        if python26:
            return python26

    if ver <= 25 or or_greater:
        python25 = path_find_binary (PYTHON_BINS,
                                     extra_dirs  = DEFAULT_PATHS,
                                     custom_test = _test_py25)
        if python25:
            return python25

    if ver <= 24 or or_greater:
        python24 = path_find_binary (PYTHON_BINS,
                                     extra_dirs  = DEFAULT_PATHS,
                                     custom_test = _test_py24)
        if python24:
            return python24


def detect_python (version, or_greater=True):
    """Ensure a Python interpreter of specified version is present. By
    default, it also accepts versions greater than the one specified.

    detect_python() returns a tuple (note, instruction_dictionary)
    suitable to use with the market.Util.InstructionBox widget."""

    def get_error (version):
        version2  = '.'.join (version.split('.')[:-1])
        version2s = ''.join (version.split('.')[:-1])

        inst = PYTHON_INST.copy()
        for k in inst:
            inst[k] = inst[k]%(locals())

        return (PYTHON_NOTE%(locals()), inst)


    interpreter = find_python (version, or_greater)
    if not interpreter:
        return get_error (version)
