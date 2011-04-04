REVISION = 9

PY_DEPS  = ['../common/target.py', '../common/java.py']
PY_FILES = ['installer.py', 'tools.py']
INCLUDE  = ['liferay',]

# 215MB
DOWNLOADS = [
    {'dir': 'liferay',
     'mv': (('liferay-portal-6.0.6', 'liferay'),
            ('liferay/tomcat-6.0.29', 'liferay/tomcat'),),
     'url': 'http://sourceforge.net/projects/lportal/files/Liferay Portal/6.0.6/liferay-portal-tomcat-6.0.6-20110225.zip'},]
