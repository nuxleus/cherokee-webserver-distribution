#
# Copyright (c) 2010, Octality S.L. - Eume 6, Villaviciosa de Odon,
# 28670 Madrid, SPAIN. All rights reserved.
#
# Any unauthorized dissemination, distribution or copying is strictly
# forbidden.
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
