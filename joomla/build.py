REVISION = 25
PY_DEPS  = ['../common/php.py',
            '../common/php-mods.py',
            '../common/target.py',
            '../common/database.py']

PY_FILES = ['installer.py', 'tools.py']
INCLUDE  = ['joomla']

DOWNLOADS = [{'dir':     'joomla',
              'fence':   True,
              'url':     'http://joomlacode.org/gf/download/frsrelease/14236/62391/Joomla_1.6.1-Stable-Full_Package.tar.bz2',
              'patches': [#('patch-01-removeinstall.diff',  '-p1'), # patch no longer required
                          ('patch-02-database-model.diff', '-p1'),
                          ('patch-03-database-view.diff',  '-p1')]
            }]
