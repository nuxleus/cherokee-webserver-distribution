REVISION = 21

PY_DEPS  = ['../common/php.py',
            '../common/target.py']

PY_FILES = ['installer.py']
INCLUDE  = ['mediawiki']

DOWNLOADS = [{'dir':     'mediawiki',
              'mv':      (('mediawiki-1.16.2', 'mediawiki'),),
              'url':     'http://download.wikimedia.org/mediawiki/1.16/mediawiki-1.16.2.tar.gz',
              'patches': [('patch-01-fixinstallation.diff', '-p1')]
            }]
