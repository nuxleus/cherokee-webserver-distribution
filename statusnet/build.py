REVISION = 12
PY_DEPS  = ['../common/php.py', '../common/php-mods.py', '../common/target.py', '../common/database.py']
PY_FILES = ['installer.py', 'tools.py']
INCLUDE  = ['statusnet']

DOWNLOADS = [{'dir':     'statusnet',
              'mv':    (('statusnet-0.9.7fix1', 'statusnet'),),
              'url':     'http://status.net/statusnet-0.9.7.tar.gz',
              'patches': [('patch-01-populate_installer.diff', '-p1')]
            }]

