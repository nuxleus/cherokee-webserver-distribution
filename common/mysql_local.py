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

import re
import popen
from util import *

def figure_connection_params (username, password):
    ret = popen.popen_sync ("mysqladmin '-u%(username)s' '-p%(password)s' variables"%(locals()))

    # Socket
    tmp = re.findall (r' socket +\| (.+?) ', ret['stdout'], re.M)
    if tmp:
        return tmp[0]

    # Port
    tmp = re.findall (r' port +\| (.+?) ', ret['stdout'], re.M)
    if tmp:
        port = tmp[0]
        return ("localhost", port)
