REVISION = 11
PY_DEPS  = ['../common/target.py', '../common/python.py', '../common/cc.py']
PY_FILES = ['installer.py', 'tools.py']
INCLUDE  = ['WsgiDAV-0.4.0b2', 'uwsgi-0.9.6.5', 'setuptools-0.6c11']

DOWNLOADS = [{'dir': 'WsgiDAV-0.4.0b2',   'url': 'http://pypi.python.org/packages/source/W/WsgiDAV/WsgiDAV-0.4.0b2.zip'},
             {'dir': 'uwsgi-0.9.6.5',     'url': 'http://projects.unbit.it/downloads/uwsgi-0.9.6.5.tar.gz'},
             {'dir': 'setuptools-0.6c11', 'url': 'http://pypi.python.org/packages/source/s/setuptools/setuptools-0.6c11.tar.gz'}]

# Still in beta. Mercurial repository is beta 4 (Oct/4).
