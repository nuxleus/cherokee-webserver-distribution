#
# Copyright (c) 2010, Octality S.L. - Eume 6, Villaviciosa de Odon,
# 28670 Madrid, SPAIN. All rights reserved.
#
# Any unauthorized dissemination, distribution or copying is strictly
# forbidden.
#

import os
import CTK
import market

from util import *
from market import Install_Log

pwd_grp = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "pwd_grp.pyo"),  "pwd_grp_util")
cc      = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "cc.pyo"),       "cc_util")

DEP_NOTE  = N_("Your system doesn't seem to provide the required dependecies. Please make sure there is a C development environment and the development libraries for the <a href='http://www.boutell.com/gd/'>GD Graphics Library</a>")
DEP_INSTRUCTIONS = cc.CC_INSTRUCTIONS.copy()
DEP_INSTRUCTIONS['apt'] = '%s libgd2-xpm-dev || %s libgd2-dev' %(DEP_INSTRUCTIONS['apt'], DEP_INSTRUCTIONS['apt'])
DEP_INSTRUCTIONS['yum'] = '%s gd gd-devel' %(DEP_INSTRUCTIONS['yum'])

def check_cc ():
    return cc.detect_cc()

def create_credentials (nagiosuser, nagiosgroup, nagioscmd, root):
    """Add users in each platform's specific fashion"""

    if not pwd_grp.group_exists (nagiosgroup):
        ret = pwd_grp.add_group (nagiosgroup)
        if ret['retcode'] == 0:
            market.Install_Log.log ("Success: %s group added to system." %(nagiosgroup))
        else:
            market.Install_Log.log ("Error: %s group not added to system." %(nagiosgroup))
            return ret

    if not pwd_grp.group_exists (nagioscmd):
        ret = pwd_grp.add_group (nagioscmd)
        if ret['retcode'] == 0:
            market.Install_Log.log ("Success: %s group added to system." %(nagioscmd))
        else:
            market.Install_Log.log ("Error: %s group not added to system." %(nagioscmd))
            return ret

    if not pwd_grp.user_exists (nagiosuser):
        path = os.path.join(root, 'nagios')
        ret = pwd_grp.add_user_and_group (user=nagiosuser, group=nagiosgroup, homedir=path)
        if ret['retcode'] == 0:
            market.Install_Log.log ("Success: %s user added to system." %(nagiosuser))
        else:
            market.Install_Log.log ("Error: %s user not added to system." %(nagiosuser))
            return ret

    server_user  = CTK.cfg.get_val ('server!user', 'root')
    ret = pwd_grp.add_user_to_group (server_user, nagioscmd)
    if ret['retcode'] == 0:
        market.Install_Log.log ("Success: %s user added to %s system group." %(server_user, nagioscmd))
    else:
        market.Install_Log.log ("Error: %s user not added to %s system group." %(server_user, nagioscmd))
        return ret

    ret = pwd_grp.add_user_to_group (nagiosuser, nagioscmd)
    if ret['retcode'] == 0:
        market.Install_Log.log ("Success: %s user added to %s system group." %(nagiosuser, nagioscmd))
    else:
        market.Install_Log.log ("Error: %s user not added to %s system group." %(nagiosuser, nagioscmd))
        return ret

    return {'ret':True, 'retcode':0}
