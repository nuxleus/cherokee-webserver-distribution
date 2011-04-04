REVISION = 15
PY_DEPS  = ['../common/php.py',
            '../common/php-mods.py',
            '../common/target.py',
            '../common/database.py']

PY_FILES = ['installer.py', 'tools.py']
INCLUDE  = ['vanilla']

DOWNLOADS = [{'dir':     'vanilla',
              'url':     'http://www.vanillaforums.org/uploads/addons/QL5HQ1LY1T6J.zip',
              'patches': [('patch-01-hide_db_block.diff', '-p1')]
            }]
