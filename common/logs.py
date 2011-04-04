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

import CTK
from util import *
from consts import *

URL_LOG_SELECTOR_APPLY = ""


def Log_Selector_apply():
    print CTK.post
    return {'ret': 'ok'}


class Log_Selector (CTK.Box):
    def __init__ (self):
        CTK.Box.__init__ (self)

        types = CTK.Box()
        types += CTK.RadioText (_("No log"),                {'name': 'log_type', 'value': 'nolog'})
        types += CTK.RadioText (_("Use existing log file"), {'name': 'log_type', 'value': 'use'})
        types += CTK.RadioText (_("Define a new log file"), {'name': 'log_type', 'value': 'new'})

        submit = CTK.Submitter (URL_LOG_SELECTOR_APPLY)
        self += types


CTK.publish ('^%s$'%(URL_LOG_SELECTOR_APPLY), Log_Selector_apply, method="POST")
