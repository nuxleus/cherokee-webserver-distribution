REVISION = 12
PY_DEPS  = ['../common/php.py',     '../common/target.py',
            '../common/pwd_grp.py', '../common/services.py',
            '../common/cc.py']

PY_FILES = ['installer.py', 'tools.py']
INCLUDE  = ['nagios-3.2.3', 'nagios-plugins-1.4.15', 'nrpe.plist.pre']

DOWNLOADS = [
    {'dir':'nagios-3.2.3',          'url':'http://ovh.dl.sourceforge.net/project/nagios/nagios-3.x/nagios-3.2.3/nagios-3.2.3.tar.gz'},
    {'dir':'nagios-plugins-1.4.15', 'url':'http://prdownloads.sourceforge.net/sourceforge/nagiosplug/nagios-plugins-1.4.15.tar.gz'},
]
