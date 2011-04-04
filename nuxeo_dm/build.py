REVISION = 9

PY_DEPS  = ['../common/target.py', '../common/java.py']
PY_FILES = ['installer.py', 'tools.py']
INCLUDE  = ['nuxeo-dm-5.4.0.1-tomcat', 'nuxeo-shell-5.4.0.1']

# 186MB
DOWNLOADS = [{'dir':     'nuxeo-dm-5.4.0.1-tomcat',
              'url':     'http://www.nuxeo.org/static/releases/nuxeo-5.4.0/nuxeo-dm-5.4.0_01-tomcat.zip',
              'patches': [('patch-01-default_ports.diff', '-p1')]
            }]
