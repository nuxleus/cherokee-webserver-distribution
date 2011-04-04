REVISION = 37
PY_DEPS  = ['../common/php.py', '../common/php-mods.py', '../common/target.py', '../common/database.py']
PY_FILES = ['installer.py', 'tools.py']
INCLUDE  = ['drupal']

DOWNLOADS = [
    {'dir': 'drupal',
     'mv': (('drupal-6.20', 'drupal'),),
     'patches': [('../drupal/patch-01-installer.diff', '-p1')],
     'url': 'http://ftp.drupal.org/files/projects/drupal-6.20.tar.gz'},
]
