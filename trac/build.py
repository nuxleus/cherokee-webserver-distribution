REVISION = 20
PY_DEPS  = ['../common/target.py', '../common/cc.py', '../common/database.py']
PY_FILES = ['installer.py', 'tools.py']
INCLUDE  = ['trac', 'Genshi-0.6', 'pysqlite-2.6.0', 'flup-1.0.2']

DOWNLOADS = [
    {'url': 'http://ftp.edgewall.com/pub/trac/Trac-0.12.2.tar.gz',
     'dir': 'trac',
     'mv':  (('Trac-0.12.2', 'trac'),)},

    {'url': 'http://pysqlite.googlecode.com/files/pysqlite-2.6.0.tar.gz',
     'dir': 'pysqlite-2.6.0'},

    {'url': 'http://ftp.edgewall.com/pub/genshi/Genshi-0.6.tar.gz',
     'dir': 'Genshi-0.6'},

    {'url': 'http://www.saddi.com/software/flup/dist/flup-1.0.2.tar.gz',
     'dir': 'flup-1.0.2'},
]
