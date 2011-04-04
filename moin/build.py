REVISION = 15
PY_DEPS  = ['../common/target.py']
PY_FILES = ['installer.py']
INCLUDE  = ['moin-1.9.3']

DOWNLOADS = [{'dir':     'moin-1.9.3',
              'url':     'http://static.moinmo.in/files/moin-1.9.3.tar.gz',
              'patches': [('patch-01-replaceconfig.diff', '-p1')]
            }]
