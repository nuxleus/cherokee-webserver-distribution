REVISION = 9
PY_DEPS  = ['../common/target.py',
            '../common/php.py',
            '../common/php-mods.py',
            '../common/database.py']

PY_FILES = ['installer.py', 'tools.py']
INCLUDE  = ['silverstripe',]

DOWNLOADS = [{'dir':     'silverstripe',
              'mv':      (('SilverStripe-v2.4.5', 'silverstripe'),),
              'url':     'http://www.silverstripe.org/assets/downloads/SilverStripe-v2.4.5.tar.gz',
              'patches': [('patch-01-detect_url_redir.diff', '-p1'),
                          ('patch-02-hide_db_block.diff',    '-p1')]
            }]

