#
# Copyright (c) 2010, Octality S.L. - Eume 6, Villaviciosa de Odon,
# 28670 Madrid, SPAIN. All rights reserved.
#
# Any unauthorized dissemination, distribution or copying is strictly
# forbidden.
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
