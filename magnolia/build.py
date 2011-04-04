REVISION = 10
PY_DEPS  = ['../common/target.py', '../common/java.py']
PY_FILES = ['installer.py', 'tools.py']
INCLUDE  = ['magnolia',]

# 61MB
DOWNLOADS = [{'dir': 'magnolia',
              'url': 'http://sourceforge.net/projects/magnolia/files/magnolia/Magnolia%20CE%204.4/magnolia-tomcat-bundle-4.4-tomcat-bundle.zip',
              'mv': (('magnolia-4.4','magnolia'), ('magnolia/apache-tomcat-6.0.29', 'magnolia/apache-tomcat'),)},
             ]
