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
import string
import CTK
import market
from util import *
from market import Install_Log

php      = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "php.pyo"),      "php_util")
php_mods = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "php-mods.pyo"), "php_mods_util")

PHP_MOD_DEPENDENCIES = ('pcre', 'xml', 'zlib', 'spl')
NOTE_NO_DB = N_("The PHP interpreter does not support any of the required database modules: 'mysql', 'mysqli', or 'pgsql'")

def check_modules ():
    errors = php_mods.check_modules (PHP_MOD_DEPENDENCIES)
    if errors:
        return errors[0]


def check_database_support ():
    db_errors = []

    # DB modules
    alternatives = ['mysql', 'mysqli']
    errors = php_mods.check_modules (alternatives)
    if len(errors) == len(alternatives):
        db_errors.append (errors[-1][1])

    alternatives = ['pgsql']
    errors = php_mods.check_modules (alternatives)
    if len(errors) == len(alternatives):
        db_errors.append (errors[-1][1])

    if len(db_errors) == 2:
        return (NOTE_NO_DB, db_errors)

