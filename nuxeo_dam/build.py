REVISION = 9

PY_DEPS  = ['../common/target.py', '../common/java.py']
PY_FILES = ['installer.py', 'tools.py']
INCLUDE  = ['nuxeo',]

# 136MB
DOWNLOADS = [{'dir': 'nuxeo',
              'mv': (('nuxeo-dam-1.2-tomcat', 'nuxeo'),),
              'url': 'http://community.nuxeo.com/static/releases/nuxeo-dam-1.2/nuxeo-dam-distribution-1.2-tomcat.zip'},]
