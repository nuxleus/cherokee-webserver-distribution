REVISION = 14
PY_DEPS  = ['../common/php.py',
            '../common/php-mods.py',
            '../common/target.py',
            '../common/database.py']

PY_FILES = ['installer.py', 'tools.py']
INCLUDE  = ['zencart']

DOWNLOADS = [{'dir':     'zencart',
              'mv':      (('zen-cart-v1.3.9h-full-fileset-10262010', 'zencart'),),
              'url':     'http://downloads.sourceforge.net/project/zencart/CURRENT_%20Zen%20Cart%201.3.x%20Series/Zen%20Cart%20v1.3.9%20-%20Full%20Release/zen-cart-v1.3.9h-full-fileset-10262010.zip',
              'patches': [('patch-01-rename-zc_install.diff',    '-p1'),
                          ('patch-02-tweak-admindir-check.diff', '-p1'),
                          ('patch-03-database-macros.diff',      '-p1')]
              }]


