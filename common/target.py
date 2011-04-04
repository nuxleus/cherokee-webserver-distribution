#
# Copyright (c) 2010, Octality S.L. - Eume 6, Villaviciosa de Odon,
# 28670 Madrid, SPAIN. All rights reserved.
#
# Any unauthorized dissemination, distribution or copying is strictly
# forbidden.
#

"""
Interfaces for selection of installation targets.

Only the following CTK widgets are relevant for package development:
  TargetSelection
"""

import CTK
import string
import Cherokee
import validations

from util import *
from consts import *
from market.Install import Install_Stage

NOTE_CREATE_NEW     = N_("Will the package be configured in a new virtual server, or will it be configured as a directory of an existing virtual server?")
NOTE_VSERVER        = N_("Domain name of the Virtual Host you are about to create. Wildcards are allowed. For example: *.example.com")
NOTE_DIRECTORY      = N_("Specify the web directory under which the application will be accessible.")
NOTE_VSERVER_SELECT = N_("Select the target Virtual Host under which the application should be installed.")

URL_TARGET_APPLY = "/market/install/target-selection/apply"

VALIDATION = [
    ('tmp!market!install!target!directory', validations.is_dir_formatted)
]

TARGETS = [
    ('vserver',   'Virtual Server'),
    ('directory', 'Directory of an existing Virtual Server')
]


def figure_out_log_name():
    app_name     = CTK.cfg.get_val('tmp!market!install!app!application_name')
    vserver_name = CTK.cfg.get_val('tmp!market!install!target!vserver')

    def filter_string (txt):
        txt = txt.replace (' ', '_')
        return filter (lambda x: x in string.letters + string.digits + "_-", txt)

    # Find a base-directory
    log_basedir = None
    for v in CTK.cfg['vserver']:
        path = CTK.cfg.get_val('vserver!%s!logger!access!filename'%(v))
        if path:
            log_basedir = os.path.dirname (path)
            if os.path.exists (log_basedir):
                break

    if not log_basedir:
        log_basedir = '/var/log'

    # Find a suitable filename
    vserver_clean = filter_string (vserver_name)
    app_clean     = filter_string (app_name)

    return os.path.join (log_basedir, "%s-%s.log" %(app_clean, vserver_clean))


def Create_CTK_cfg():
    pre = 'tmp!market!install!target'

    target_type      = CTK.cfg.get_val(pre)
    target_vserver   = CTK.cfg.get_val('%s!vserver'%(pre))
    target_vserver_n = CTK.cfg.get_val('%s!vserver_n'%(pre))
    target_directory = CTK.cfg.get_val('%s!directory'%(pre))

    # Set the 1st target if it has not been set yet
    if not target_type:
        target_type = TARGETS[0][0]
        CTK.cfg[pre] = target_type

    if target_type == 'vserver':
        new_pre = CTK.cfg.get_next_entry_prefix ('vserver')
        CTK.cfg['%s!vserver_n'%(pre)]                     = new_pre.split('!')[-1]
        CTK.cfg['%s!nick'%(new_pre)]                      = target_vserver
        CTK.cfg['%s!match'%(new_pre)]                     = 'wildcard'
        CTK.cfg['%s!match!domain!1'%(new_pre)]            = target_vserver

        # Set the log files
        CTK.cfg['%s!logger'%(new_pre)]                 = 'combined'
        CTK.cfg['%s!logger!access!type'%(new_pre)]     = 'file'
        CTK.cfg['%s!logger!access!filename'%(new_pre)] = figure_out_log_name()

        first_vserver = CTK.cfg.get_lowest_entry('vserver')
        if CTK.cfg.get_val ('vserver!%s!error_writer!type' %(first_vserver)):
            CTK.cfg.clone ('vserver!%s!error_writer' %(first_vserver), '%s!error_writer' %(new_pre))


def Target_Details_apply():
    pre = 'tmp!market!install!target'

    target_prev = CTK.cfg.get_val(pre)
    target_now  = CTK.post.get_val(pre)
    autoset     = bool (CTK.post.pop ("autoset"))
    vserver     = CTK.post.get_val("%s!vserver"%(pre))
    vserver_n   = CTK.post.get_val("%s!vserver_n"%(pre))
    directory   = CTK.post.get_val("%s!directory"%(pre))

    # Changing Target type
    if autoset:
        target_now = 'vserver'
    else:
        if target_now:
            if target_prev and (target_now != target_prev):
                return CTK.cfg_apply_post()
            elif not target_prev:
                return CTK.cfg_apply_post()

    if not target_now:
        target_now = target_prev

    # Applying
    if target_now == 'vserver':
        # Not empty
        if not vserver:
            return {'ret': 'error', 'errors': {'%s!vserver'%(pre): _("Can not be empty")}}

        # Ensure the Domain Name in unique
        all_nicks = [CTK.cfg.get_val('vserver!%s!nick'%(k)) for k in CTK.cfg['vserver']]
        if vserver in all_nicks:
            return {'ret': 'error', 'errors': {'%s!vserver'%(pre): _("Domain Name already in use")}}

    elif target_now == 'directory' and vserver_n:
        # Directory is not empty
        if not directory:
            return {'ret': 'error', 'errors': {'%s!directory'%(pre): _("Can not be empty")}}

        if len(directory) <= 1:
            return {'ret': 'error', 'errors': {'%s!directory'%(pre): _("Root directory is not allowed")}}

        # Directory must be unique for the virtual server
        for r in CTK.cfg['vserver!%s!rule'%(vserver_n)]:
            if CTK.cfg.get_val('vserver!%s!rule!%s!match'%(vserver_n,r)) == 'directory':
                if CTK.cfg.get_val('vserver!%s!rule!%s!match!directory'%(vserver_n,r)) == directory:
                    return {'ret': 'error', 'errors': {'%s!directory'%(pre): _("Directory already configured")}}

    # Create real CTK.cfg entries
    ret = CTK.cfg_apply_post()
    Create_CTK_cfg()

    return ret


class Target_VServer (CTK.Box):
    def __init__ (self):
        CTK.Box.__init__ (self)
        pre = "tmp!market!install!target"

        table = CTK.PropsTable()
        table.Add (_('Domain Name'), CTK.TextCfg('%s!vserver'%(pre), False, {'class':'noauto'}), _(NOTE_VSERVER))
        self += table

def cmp_domain (x, y):
    d1 = CTK.cfg.get_val('vserver!%s!nick'%(x))
    d2 = CTK.cfg.get_val('vserver!%s!nick'%(y))

    x_parts = d1.split('.')
    y_parts = d2.split('.')
    x_parts.reverse()
    y_parts.reverse()

    # Not a domain: parts number
    if len(x_parts) < 2 and len(y_parts) < 2:
        return cmp (d1, d2)
    elif len(x_parts) < 2:
        return cmp (d1, y_parts[1])
    elif len(y_parts) < 2:
        return cmp (x_parts[1], d2)

    # Name domain, sort by length
    if x_parts[1] == y_parts[1]:
        return cmp (len(d1), len(d2))

    # Different domain
    return cmp (x_parts[1], y_parts[1])


class Target_Directory (CTK.Box):
    def __init__ (self):
        CTK.Box.__init__ (self)
        pre = "tmp!market!install!target"

        # Even though vserver must have a nick, there's been people
        # reporting crahes on the cmp funciontion because they have
        # vservers nick no nick property.
        vsrv_keys = []
        for k in CTK.cfg.keys('vserver'):
            if CTK.cfg.get_val('vserver!%s!nick'%(k)):
                vsrv_keys.append(k)

        vsrv_keys.sort (cmp_domain)

        vservers = []
        for v in vsrv_keys:
            vservers.append ((v, CTK.cfg.get_val("vserver!%s!nick"%(v))))

        table = CTK.PropsTable()
        table.Add (_('Virtual Server'), CTK.ComboCfg('%s!vserver_n'%(pre), vservers, {'class':'noauto'}), _(NOTE_VSERVER_SELECT))
        table.Add (_('Directory'),      CTK.TextCfg('%s!directory'%(pre),  False,    {'class':'noauto'}), _(NOTE_DIRECTORY))
        self += table


class TargetSelection_Refresh (CTK.Box):
    def __init__ (self, refresh):
        CTK.Box.__init__ (self)

        # Embed widgets on a submmitter
        submit = CTK.Submitter (URL_TARGET_APPLY)
        submit.bind ('submit_success', submit.JS_to_trigger ('goto_next_stage'))
        self += submit

        # Ensure a target type is set
        if not CTK.cfg.get_val ('tmp!market!install!target'):
            submit += CTK.Hidden ('autoset', '1')
            CTK.cfg['tmp!market!install!target'] = TARGETS[0][0]

        # Select target class
        selected = CTK.cfg.get_val ('tmp!market!install!target')
        if selected == 'vserver':
            submit += Target_VServer()
        elif selected == 'directory':
            submit += Target_Directory()
        else:
            submit += CTK.RawHTML ('<h1>%s</h1>' %(_("Unknown target")))


class TargetSelection (CTK.Box):
    """Widget to select virtual-server/web-directory deployment type.
    Upon successful execution, a goto_next_stage event is triggered.
    Once the widget has performed its task, the relevant information
    can be retrieved like this:

    target_type      = CTK.cfg.get_val ('tmp!market!install!target')
    target_vserver   = CTK.cfg.get_val ('tmp!market!install!target!vserver')
    target_vserver_n = CTK.cfg.get_val ('tmp!market!install!target!vserver_n')
    target_directory = CTK.cfg.get_val ('tmp!market!install!target!directory')
    """
    def __init__ (self):
        CTK.Box.__init__ (self, {'class': 'market-target-selection'})

        # Properties
        self.refresh = CTK.Refreshable({'id': 'market-target-selection-refresh'})
        self.refresh.register (lambda: TargetSelection_Refresh(self.refresh).Render())

        # Install as..
        combo = CTK.ComboCfg('tmp!market!install!target', trans_options(TARGETS))

        table = CTK.PropsTable()
        table.Add (_('Install as a new..'), combo, _(NOTE_CREATE_NEW))

        submit = CTK.Submitter (URL_TARGET_APPLY)

        # Refresh only when the combo changes. Do not freshes when the
        # 'Next' button is clicked (and thus all the submitters are
        # sent). In case a Submitter from within the refreshable
        # failed, the error message would be lost with the refresh.
        submit.bind ('submit_success',
                     CTK.DruidContent__JS_if_internal_submit (self.refresh.JS_to_refresh()))
        submit += table

        # Build GUI
        self += CTK.RawHTML ("<h2>%s</h2>" %(_("Deployment Type")))
        self += submit
        self += self.refresh


CTK.publish ('^%s$'%(URL_TARGET_APPLY), Target_Details_apply, validation=VALIDATION, method="POST")
