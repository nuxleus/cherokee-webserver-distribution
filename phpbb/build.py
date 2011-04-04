REVISION = 14

PY_DEPS  = ['../common/php.py',
            '../common/php-mods.py',
            '../common/target.py',
            '../common/database.py']

PY_FILES = ['installer.py', 'tools.py']
INCLUDE  = ['phpBB3']

DOWNLOADS = [{'dir':     'phpBB3',
              'url':     'http://www.phpbb.com/files/release/phpBB-3.0.8.tar.bz2',
              'patches': [('patch-01-fixinstallation.diff', '-p1')]
            }]

# Languages: 3 files per language
LANG_FILES  = ['lang_%s.tar.gz', 'subsilver2_%s.tar.gz', 'prosilver_%s.tar.gz']
LANG_CODES  = ['en_us', 'ch_cmn_hans', 'ch_cmn_hant', 'ja', 'de', 'de_x_sie', 'pt_br', 'pt', 'ru', 'fr', 'fr_x_tu', 'es', 'ar']
LANG_PREFIX = "http://www.phpbb.com/files/language_packs_30x/"
