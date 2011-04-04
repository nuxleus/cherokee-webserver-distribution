REVISION = 5
PY_DEPS  = ['../common/php.py', '../common/php-mods.py', '../common/target.py', '../common/database.py']
PY_FILES = ['installer.py', 'tools.py']
INCLUDE  = ['drupal', 'drush']

DOWNLOADS = [{'dir': 'drupal',
              'url': 'http://ftp.drupal.org/files/projects/drupal-7.0.tar.gz',
              'mv':  (('drupal-7.0', 'drupal'),),},
             {'dir': 'drush',
              'patches': [('../drupal7/patch-01-drush-mysql.diff', '-p1')],
              'url': 'http://ftp.drupal.org/files/projects/drush-All-versions-4.2.tar.gz'},]
