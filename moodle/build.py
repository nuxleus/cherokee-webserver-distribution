REVISION = 15

PY_DEPS  = ['../common/php.py',
            '../common/php-mods.py',
            '../common/target.py',
            '../common/database.py']

PY_FILES = ['installer.py', 'tools.py']
INCLUDE  = ['moodle']

DOWNLOADS = [{'dir':     'moodle',
              'url':     'http://downloads.sourceforge.net/project/moodle/Moodle/stable20/moodle-latest-20.tgz',
              'patches': [('patch-01-fixcli.diff', '-p1')]
            }]
