REVISION = 19
PY_DEPS  = ['../common/php.py', '../common/php-mods.py', '../common/target.py', '../common/database.py']
PY_FILES = ['installer.py', 'tools.py']
INCLUDE  = ['phpMyAdmin', 'config.inc.php']

DOWNLOADS = [{'dir': 'phpMyAdmin',
              'url': 'http://sourceforge.net/projects/phpmyadmin/files/phpMyAdmin/3.3.10/phpMyAdmin-3.3.10-english.tar.bz2',
              'mv':   (('phpMyAdmin-3.3.10-english', 'phpMyAdmin'),),
            }]
