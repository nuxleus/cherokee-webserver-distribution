#
# Copyright (c) 2010, Octality S.L. - Eume 6, Villaviciosa de Odon,
# 28670 Madrid, SPAIN. All rights reserved.
#
# Any unauthorized dissemination, distribution or copying is strictly
# forbidden.
#

"""
Interfaces for database management. The module provides both GUI
elements and worker classes.

Only the following CTK widgets are relevant for package development:
  MethodSelection
  PreconditionError
"""

import CTK
import re
import time
import popen
import random
import string
import Cherokee
import validations

from util import *
from consts import *
from market import Install_Log
from market.Install import Install_Stage
from market.Util import InstructionBox

NOTE_METHOD       = N_("The application requires a database to work. Please choose how to configure it.")
NOTE_ADMINUSER    = N_("Specify the name of a privileged DB user. It will be used to automatically create the required user and database.")
NOTE_ADMINPASS    = N_("Specify the password for this user account.")
NOTE_DBUSER       = N_("Specify the name of an existing database user.")
NOTE_DBPASS       = N_("Specify the password for the database user account.")
NOTE_DBTYPE       = N_("Specify the type of database that you want to use.")
NOTE_DBNAME       = N_("Specify the existing database that you want to use. The specified user must have privileges to use it.")
NOTE_INTRO_AUTO   = N_("Please, provide an administrative user/password pair to connect to a database.")
NOTE_INTRO_MANUAL = N_("Please, provide details of an existing database and user/password pair to a database.")
NOTE_INTRO_COMMON = N_("Bare in mind that the database server must be running on the host.")

URL_MANUAL_APPLY = "/market/install/db/method_manual/apply"
URL_AUTO_APPLY   = "/market/install/db/method_auto/apply"
URL_METHOD_APPLY = "/market/install/db/method/apply"
URL_DBTYPE_APPLY = "/market/install/db/type/apply"

VALIDATION = [
    ('tmp!market!install!db!admin_user', validations.is_not_empty),
    ('tmp!market!install!db!db_name',    validations.is_not_empty),
    ('tmp!market!install!db!db_user',    validations.is_not_empty),
    ('tmp!market!install!db!db_pass',    validations.is_not_empty),
]

METHODS = [
    ('automatic', _('Automatic')),  # provide admin user details: create db and user details
    ('manual',    _('Manual')),     # provide existing user, password and dbname
]

DATABASES = [
    ('sqlite3',    'SQLite 3'),
    ('mysql',      'MySQL'),
    ('postgresql', 'PostgreSQL'),
    ('oracle',     'Oracle'),
    ('sqlserver',  'SQL Server'),
]

KEY_PRE = "tmp!market!install!db"

MYSQL5_NOTE  = N_('MySQL 5 could not be found on your system.')
MYSQL5_INSTRUCTIONS = {
    'apt':           "sudo apt-get install mysql-server",
    'yum':           "sudo yum install mysql-server",
    'zypper':        "sudo zypper install mysql",
    'macports':      "sudo port install mysql5",
    'freebsd_pkg':   "pkg_add -r mysql51-server",
    'freebsd_ports': "cd /usr/ports/databases/mysql51-server && make install",
    'ips':           "pfexec pkg install pkg:/database/mysql-51",
    'default':       N_("MySQL is available at http://www.mysql.com/")
}

MYSQL_DEV_NOTE  = N_('MySQL development files could not be found on your system.')
MYSQL_DEV_INSTRUCTIONS = {
    'apt':           "sudo apt-get install libmysqlclient-dev",
    'default':       N_("MySQL is available at http://www.mysql.com/")
}

PGSQL8_NOTE  = N_('PostgreSQL 8 could not be found on your system.')
PGSQL8_INSTRUCTIONS = {
    'apt':           "sudo apt-get install postgresql",
    'yum':           "sudo yum install postgresql-server",
    'zypper':        "sudo zypper install postgresql-server",
    'macports':      "sudo port install postgresql84-server",
    'freebsd_pkg':   "pkg_add -r postgresql84-server",
    'freebsd_ports': "cd /usr/ports/databases/postgresql84-server && make install",
    'ips':           "pfexec pkg install pkg:/database/postgres-84",
    'default':       N_("PostgreSQL is available at http://www.postgresql.org/")
}


PYSQLITE3_NOTE  = N_('Sqlite3 could not be found on your system.')
PYSQLITE3_INSTRUCTIONS = {
    'apt':           "sudo apt-get install sqlite3",
    'yum':           "sudo yum install sqlite",
    'zypper':        "sudo zypper install sqlite3",
    'macports':      "sudo port install sqlite3",
    'freebsd_pkg':   "pkg_add -r sqlite3",
    'freebsd_ports': "cd /usr/ports/databases/sqlite3 && make install",
    'ips':           "pfexec pkg install pkg:/database/sqlite-3",
    'default':       N_("SQLite3 is available at http://www.sqlite.org/")
}

MYSQL_BIN_NAMES      = ['mysql', 'mysql5']
MYSQLADMIN_BIN_NAMES = ['mysqladmin', 'mysqladmin5']

MYSQL_PATHS = [
    '/usr/bin',
    '/opt/local/bin',
    '/usr/local/bin',
    '/usr/mysql*/bin',
    '/opt/mysql*/bin',
    '/opt/local/lib/mysql*/bin',
    '/usr/local/mysql*/bin',
]

MYSQL_DEV_PATHS = [
    '/usr/include',
    '/usr/local/include',
    '/usr/include/mysql*',
    '/usr/local/include/mysql*/mysql',
    '/usr/local/include/mysql*',
    '/opt/mysql*/include',
    '/opt/local/include/mysql*/mysql',
    '/usr/local/mysql*/include',
    '/usr/local/mysql*/include/mysql',
    '/usr/mysql/*/include/mysql'
]

SQLITE3_PATHS = [
    '/usr/lib/libsqlite3*',
    '/usr/local/lib/libsqlite3*',
    '/usr/sfw/lib/libsqlite3*',
    '/usr/gnu/lib/libsqlite3*',
    '/opt/local/lib/libsqlite3*',
    '/usr/pkg/lib/libsqlite3*',
    '/usr/lib64/libsqlite3*',
]

MYSQL_PRIVILEGES = [
    'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP',
    'REFERENCES', 'INDEX', 'ALTER', 'CREATE TEMPORARY TABLES',
    'LOCK TABLES', 'EXECUTE', 'CREATE VIEW', 'SHOW VIEW',
    'CREATE ROUTINE', 'ALTER ROUTINE', 'EVENT', 'TRIGGER',
]


PGSQL_PRIVILEGES = [
    'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'REFERENCES', 'TRIGGER',
    'CREATE', 'CONNECT', 'TEMPORARY', 'TEMP', 'EXECUTE', 'USAGE'
]


def stderr_to_error (txt):
    error = CTK.escape_html (txt)
    error = error.replace('\n', '<br/>')
    error = error.replace('\x07', '')
    error = error.replace('\r', '')
    return error

def run (cmd, *args, **kwargs):
    Install_Log.log ("DB: %s" %(cmd))
    return popen.popen_sync (cmd, *args, **kwargs)

def mysql_bins (bin_names):
    # List
    if type(bin_names) == list:
        for name in bin_names:
            re = path_find_binary (name, MYSQL_PATHS)
            if re:
                return re

    # String
    return path_find_binary (bin_names, MYSQL_PATHS)

def mysql_path():
    mysql_bin = mysql_bins (MYSQL_BIN_NAMES)
    n = mysql_bin.find ('/bin')
    if n > 0:
        return mysql_bin[:n+4]

def mysql_dev_path():
    return path_find_binary ('mysql.h', MYSQL_DEV_PATHS)

class DatabaseDetector:
    """Detect database engines supported on the system. Currently
    detects MySQL, PostgreSQL, and SQLite3.
    """
    def __init__ (self):
        self.supported = []

    def get_supported (self):
        """Return list of supported engines. The list is comprised of
        entries, each with the following keys:
          db:      one of 'mysql', 'postgresql', and 'sqlite3'
          name:    one of 'MySQL', 'PostgreSQL', and 'SQLite 3'
          version: version of the engine"""

        if not self.supported:
            self.__detect_mysql()
            self.__detect_postgresql()
            self.__detect_sqlite3()

        return self.supported

    def get_supported_from_list (self, potentially_supported):
        """Return list of supported engines among the provided list of
        potentially_supported (a subset of ['mysql', 'postgresql',
        'sqlite3']). The returned list of results is a subset of the
        one returned by get_supported()"""

        found = self.get_supported()
        return filter (lambda x: x['db'] in potentially_supported, found)

    def __detect_mysql (self):
        ret = run ('%s -V' %(mysql_bins (MYSQL_BIN_NAMES)))
        tmp = re.findall ('mysql.+?([\d.]+).+?([\d.]+)', ret.get('stdout'), re.M)
        if tmp:
            self.supported += [{'db': 'mysql', 'name': 'MySQL', 'version': tmp[0][1]}]

    def __detect_postgresql (self):
        ret = run ('psql -V')
        tmp = re.findall ('PostgreSQL.+?([\d.]+)', ret.get('stdout'), re.M)
        if tmp:
            self.supported += [{'db': 'postgresql', 'name': 'PostgreSQL', 'version': tmp[0]}]

    def __detect_sqlite3 (self):
        # Prefered method, more verbose
        ret = run ('sqlite3 -version')
        tmp = re.findall ('([\d.]+)', ret.get('stdout'), re.M)
        if tmp:
            self.supported += [{'db': 'sqlite3', 'name': 'SQLite3', 'version': tmp[0]}]
        else:
            # Try at least libary detection if no binary is found
            lib = path_find_w_default (SQLITE3_PATHS)
            if lib:
                self.supported += [{'db': 'sqlite3', 'name': 'SQLite3', 'version': '3'}]


def get_supported_dbs (dbtypes):
    detector = DatabaseDetector()
    return detector.get_supported_from_list (dbtypes)


class BaseDB:
    """Base class for database worker classes.
    """
    def __init__ (self, **kwargs):
        self.admin_user = None # Privileged user
        self.admin_pass = None
        self.db_user    = None # Regular user
        self.db_pass    = None
        self.db_name    = None # Database name

        for n in ('db_name', 'db_user', 'db_pass', 'admin_user', 'admin_pass'):
            if n in kwargs.keys():
                self.__dict__[n] = kwargs[n]

    def has_admin_rights (self):
        return self.admin_user != None

    def fill_out_auto (self):
        self.db_name = self._get_canonical_name()
        self.db_user = 'mkt_' + self._get_canonical_name()[-12:] # 16 chrs max
        self.db_pass = self._generate_random_password()

    def _get_canonical_name (self):
        root  = CTK.cfg.get_val('tmp!market!install!root')
        stamp = root.split('/')[-1].replace('.','_')
        return 'market_%s'%(stamp)

    def _generate_random_password (self):
        opts = string.letters + string.digits
        return ''.join ([random.choice(opts) for x in range(32)])


class MySQL (BaseDB):
    """Worker class for MySQL engine.
    """
    def __init__ (self, **kwargs):
        BaseDB.__init__ (self, **kwargs)

    def is_dbuser_present (self, username, password=None):
        """Ensure provided database user and password are
        valid. Returns an error otherwise."""

        mysqladmin_bin = mysql_bins(MYSQLADMIN_BIN_NAMES)

        if password:
            cmd = "%(mysqladmin_bin)s '-u%(username)s' '-p%(password)s' version" %(locals())
        else:
            cmd = "%(mysqladmin_bin)s '-u%(username)s' version" %(locals())

        ret = run (cmd)
        if ret['retcode']:
            return stderr_to_error (ret['stderr'])

    def is_dbname_present (self, db_name):
        """Ensure provided database name is present. Returns an error
        otherwise."""

        # Check with privileged / unprivileged user
        if self.admin_user:
            user_name = self.admin_user
            user_pass = self.admin_pass
        else:
            user_name = self.db_user
            user_pass = self.db_pass

        # Build command
        mysql_bin = mysql_bins (MYSQL_BIN_NAMES)

        if user_pass:
            cmd = "%(mysql_bin)s '-u%(user_name)s' '-p%(user_pass)s' << EOF\n"
        else:
            cmd = "%(mysql_bin)s '-u%(user_name)s' << EOF\n"

        cmd += "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '%(db_name)s';\n"
        cmd += "EOF\n"
        cmd = cmd%(locals())

        # Execute it
        ret = run (cmd)
        if ret['retcode']:
            return stderr_to_error (ret['stderr'])

        if not db_name in ret['stdout']:
            return _('Database not present')

    def create (self):
        """Create the database. The values for creation are set as
        properties of the object."""

        # Create the database
        params = self.__dict__.copy()
        params['mysql_bin']      = mysql_bins(MYSQL_BIN_NAMES)
        params['mysqladmin_bin'] = mysql_bins(MYSQLADMIN_BIN_NAMES)

        if self.admin_pass:
            cmd = "%(mysqladmin_bin)s '-u%(admin_user)s' '-p%(admin_pass)s' create '%(db_name)s' --default-character-set=utf8" %(params)
        else:
            cmd = "%(mysqladmin_bin)s '-u%(admin_user)s' create '%(db_name)s' --default-character-set=utf8" %(params)

        ret = run (cmd)
        if ret['retcode']:
            return stderr_to_error (ret['stderr'])

        Install_Log.log ("DB: Created MySQL database %s" %(self.db_name))

        # Modify collation and grant permissions
        if self.admin_pass:
            cmd = "%(mysql_bin)s '-u%(admin_user)s' '-p%(admin_pass)s' << EOF\n" %(params)
        else:
            cmd = "%(mysql_bin)s '-u%(admin_user)s' << EOF\n" %(params)

        sql = """ALTER DATABASE %(db_name)s DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci;\nEOF\n""" %(params)
        ret = run (cmd + sql)
        if ret['retcode'] == 0:
            Install_Log.log ("DB: Modified collation on %s" %(self.db_name))

            sql = """GRANT ALL PRIVILEGES ON %(db_name)s.* TO %(db_user)s@localhost IDENTIFIED BY '%(db_pass)s'; FLUSH PRIVILEGES;\nEOF\n""" %(params)
            ret = run (cmd + sql)
            if ret['retcode'] == 0:
                Install_Log.log ("DB: Granted privileges on %s to user %s" %(self.db_name, self.db_user))
                return


        # Drop DB if it could not set the permissions
        Install_Log.log ("DB: Deleted MySQL database %s" %(self.db_name))
        if self.admin_pass:
            cmd = "%(mysqladmin_bin)s --force '-u%(admin_user)s' '-p%(admin_pass)s' drop '%(db_name)s'" %(params)
        else:
            cmd = "%(mysqladmin_bin)s --force '-u%(admin_user)s' drop '%(db_name)s'" %(params)

        run (cmd)

        # Report the 'Grant permissions' error
        return stderr_to_error (ret['stderr'])

    def check_privileges (self, privs):
        """Ensure the specified privileges are granted for this
        user/password/database combination. Returns an error
        otherwise."""
        to_check = []
        for priv in privs:
            if   priv == 'create_table':
                to_check.append ('CREATE')
            elif priv == 'write':
                to_check.append ('INSERT')
            elif priv == 'read':
                to_check.append ('SELECT')
            else:
                raise ValueError, '%s: %s' %(_('Unknown privilege'), priv)

        # Build command
        params        = self.__dict__.copy()
        params['sql'] = "SELECT privilege_type FROM schema_privileges WHERE table_schema='%(db_name)s';" %(params)
        params['bin'] = mysql_bins (MYSQL_BIN_NAMES)

        if params.get('db_user'):
            cmd = """%(bin)s '-u%(db_user)s' '-p%(db_pass)s' 'information_schema' -s -e "%(sql)s" """
        else:
            cmd = """%(bin)s '-u%(db_user)s' 'information_schema' -s -e "%(sql)s" """
        cmd = cmd%(params)

        # Execute it
        ret = run (cmd)
        if ret['retcode']:
            Install_Log.log ("DB: Error checking MySQL privileges")
            return stderr_to_error (ret['stderr'])

        # Check
        provided_privs = ret['stdout'].splitlines()
        missing_privs  = []
        for priv in to_check:
            if not priv in provided_privs:
                missing_privs.append (priv)

        if missing_privs:
            Install_Log.log ("DB: Unsuccessfull MySQL privilege check: %s" %(', '.join(missing_privs)))
            msg = _('User %(db_user)s is missing the following privileges on database %(db_name)s') %(params)
            return '%s: %s' %(msg, ', '.join(missing_privs))

        Install_Log.log ("DB: Successfull MySQL privilege check")


class PostgreSQL (BaseDB):
    def __init__ (self, **kwargs):
        BaseDB.__init__ (self, **kwargs)

    def _cmd_auth (self, cmd, user, password):
        return "PGUSER=%(user)s PGPASSWORD=%(password)s %(cmd)s" %(locals())

    def is_dbuser_present (self, username, password=None):
        """Ensure provided database user and password are
        valid. Returns an error otherwise."""

        cmd = """psql --tuples-only --command="select usename from pg_user where usename='%(username)s'" """ %(locals())

        ret = run (self._cmd_auth(cmd, username, password))
        if ret['retcode']:
            return stderr_to_error (ret['stderr'])

        if not username in ret['stdout']:
            return _('Username does not exist')

    def is_dbname_present (self, db_name):
        """Ensure provided database name is present. Returns an error
        otherwise."""

        # Check with privileged / unprivileged user
        if self.admin_user:
            user_name = self.admin_user
            user_pass = self.admin_pass
        else:
            user_name = self.db_user
            user_pass = self.db_pass

        # Run command
        cmd = "psql --list --tuples-only --no-align"

        ret = run (self._cmd_auth(cmd, user_name, user_pass))
        if ret['retcode']:
            return stderr_to_error (ret['stderr'])

        # Parse output
        data = re.findall('^(.*?)\|(.*?)\|.*$', ret['stdout'], re.MULTILINE)
        for dbset in data:
            if dbset[0] == db_name and dbset[1] == user_name:
                return None
            elif dbset[0] == db_name and dbset[1] != user_name:
                return _('The specified user is not the owner of the database')

        return _('Database not present')

    def create (self):
        """Create the database. The values for creation are set as
        properties of the object."""

        # Create the user
        ret = self.create_user()
        if ret:
            return ret

        # Create the database
        cmd = "createdb '%(db_name)s' --encoding=utf8 --owner='%(db_user)s'" %(self.__dict__)

        ret = run (self._cmd_auth (cmd, self.admin_user, self.admin_pass))
        if ret['retcode']:
            Install_Log.log ("DB: Problem creating PostgreSQL database %s" %(self.db_name))
            return stderr_to_error (ret['stderr'])

        Install_Log.log ("DB: Created PostgreSQL database %s" %(self.db_name))

    def create_user (self):
        """Create the database user that is set as property of the
        object."""
        cmd = """psql  --command="CREATE USER %(db_user)s WITH PASSWORD '%(db_pass)s'" """%(self.__dict__)

        ret = run (self._cmd_auth (cmd, self.admin_user, self.admin_pass))
        if ret['retcode']:
            Install_Log.log ("DB: Problem creating PostgreSQL user %s" %(self.db_user))
            return stderr_to_error (ret['stderr'])

        Install_Log.log ("DB: Created PostgreSQL user %s" %(self.db_user))


    def check_privileges (self, privs):
        """Ensure the specified privileges are granted for this
        user/password/database combination. Returns an error
        otherwise."""
        to_check = []
        # Accepted privileges for has_database_privilege: CREATE, CONNECT, TEMPORARY, TEMP
        for priv in privs:
            if priv in ['create_table', 'write']:
                if not 'CREATE' in to_check:
                    to_check.append ('CREATE')
            elif priv == 'read':
                to_check.append ('CONNECT')
            else:
                raise ValueError, '%s: %s' %(_('Unknown privilege'), priv)

        # Check
        missing_privs  = []
        for priv in to_check:
            cmd = """psql --list --tuples-only --no-align --command="SELECT has_database_privilege ('%s', '%s');" """ %(self.db_name, priv)
            ret = run (self._cmd_auth (cmd, self.db_user, self.db_pass))
            if ret['retcode']:
                Install_Log.log ("DB: Error checking PostgreSQL privilege: %s" %(priv))
                return stderr_to_error (ret['stderr'])

            if 'f' in ret['stdout']:
                missing_privs.append (priv)

        if missing_privs:
            Install_Log.log ("DB: Unsuccessfull PostgreSQL privilege check: %s" %(', '.join(missing_privs)))
            msg = _('User %(db_user)s is missing the following privileges on database %(db_name)s') %(params)
            return '%s: %s' %(msg, ', '.join(missing_privs))

        Install_Log.log ("DB: Successfull PostgreSQL privilege check")

#
# GUI: Classes that are not instanced outside of this module's scope
#

class Database_Type (CTK.Box):
    class Apply:
        def __call__ (self):
            return CTK.cfg_apply_post()

    def __init__ (self, refresh, dbtypes):
        CTK.Box.__init__ (self)

        # Collect data
        supported = get_supported_dbs (dbtypes)
        types     = [(x['db'], x['name']) for x in supported]

        # Populate cfg with the current type
        if not CTK.cfg.get_val('%s!db_type'%(KEY_PRE)):
            CTK.cfg['%s!db_type' %(KEY_PRE)] = types[0][0]

        # Build widget
        combo = CTK.ComboCfg ('%s!db_type'%(KEY_PRE), trans_options(types))

        table = CTK.PropsTable()
        table.Add (_('Engine'), combo, _(NOTE_DBTYPE))

        submit = CTK.Submitter (URL_DBTYPE_APPLY)
        submit.bind ('submit_success',
                     CTK.DruidContent__JS_if_internal_submit (refresh.JS_to_refresh()))

        submit += table
        self += submit


class Method_Chooser (CTK.Box):
    class Apply:
        def __call__ (self):
            return CTK.cfg_apply_post()

    def __init__ (self, refresh):
        CTK.Box.__init__ (self)

        # Populate cfg with the current type
        if not CTK.cfg.get_val('%s!method'%(KEY_PRE)):
            CTK.cfg['%s!method'%(KEY_PRE)] = METHODS[0][0]

        # Build widget
        combo = CTK.ComboCfg ('%s!method' %(KEY_PRE), trans_options(METHODS))

        table = CTK.PropsTable()
        table.Add (_('Configuration method'), combo, _(NOTE_METHOD))

        submit = CTK.Submitter (URL_METHOD_APPLY)
        submit.bind ('submit_success',
                     CTK.DruidContent__JS_if_internal_submit (refresh.JS_to_refresh()))
        submit += table
        self += submit


class Method_Automatic (CTK.Box):
    class Apply:
        def __call__ (self):
            admin_user = CTK.post.get_val('%s!admin_user' %(KEY_PRE))
            admin_pass = CTK.post.get_val('%s!admin_pass' %(KEY_PRE))
            db_type    = CTK.cfg.get_val ('%s!db_type'    %(KEY_PRE))

            # DB access obj
            params = {'db_type':    db_type,
                      'admin_user': admin_user,
                      'admin_pass': admin_pass}

            if db_type == 'mysql':
                db = MySQL (**params)
            elif db_type == 'postgresql':
                db = PostgreSQL (**params)
            elif db_type == 'sqlite3':
                return CTK.cfg_apply_post()
            else:
                raise ValueError, "Unsupported: %s" %(str(db_type))

            # Generate fields
            db.fill_out_auto()

            # The user and password pair
            error = db.is_dbuser_present (admin_user, admin_pass)
            if error:
                errors = {'%s!admin_pass' %(KEY_PRE): error}
                return {'ret':'fail', 'errors': errors}

            # Create Database
            error = db.create()
            if error:
                errors = {'%s!admin_pass' %(KEY_PRE): error}
                return {'ret':'fail', 'errors': errors}

            # If creation was successful, store generated values
            CTK.cfg['%s!db_name' %(KEY_PRE)] = db.db_name
            CTK.cfg['%s!db_pass' %(KEY_PRE)] = db.db_pass
            CTK.cfg['%s!db_user' %(KEY_PRE)] = db.db_user

            return CTK.cfg_apply_post()

    def __init__ (self, refresh, dbtypes):
        CTK.Box.__init__ (self)

        # Ensure there a suitable DB
        supported = get_supported_dbs (dbtypes)
        if not supported:
            self += CTK.RawHTML ('<h1>%s</h1>' %(_("No supported database engines were detected.")))
            self += CTK.RawHTML ('<p>%s: %s</p>' %(_('The available options are'), ', '.join(dbtypes)))
            return

        # DB Type
        self += Database_Type (refresh, dbtypes)

        # DB Details
        db_type = CTK.cfg.get_val ('%s!db_type' %(KEY_PRE), dbtypes)

        table  = CTK.PropsTable()
        submit = CTK.Submitter (URL_AUTO_APPLY)
        submit.bind ('submit_success', table.JS_to_trigger('goto_next_stage'))
        submit += table

        if db_type in ('mysql', 'postgresql', 'oracle', 'sqlserver'):
            self += Method_Chooser (refresh)
            self += CTK.RawHTML ('<p>%s %s</p>' %(_(NOTE_INTRO_AUTO), _(NOTE_INTRO_COMMON)))

            table.Add (_('Admin Username'), CTK.TextCfg        ('%s!admin_user'%(KEY_PRE), False, {'class':'noauto'}), _(NOTE_ADMINUSER))
            table.Add (_('Admin Password'), CTK.TextCfgPassword('%s!admin_pass'%(KEY_PRE), False, {'class':'noauto'}), _(NOTE_ADMINPASS))
        else:
            submit += CTK.Hidden('%s!empty_db'%(KEY_PRE),'1')

        self += submit


class Method_Manual (CTK.Box):
    class Apply:
        def __call__ (self):
            db_user     = CTK.post.get_val('%s!db_user' %(KEY_PRE))
            db_pass     = CTK.post.get_val('%s!db_pass' %(KEY_PRE))
            db_name     = CTK.post.get_val('%s!db_name' %(KEY_PRE))
            db_type     = CTK.cfg.get_val ('%s!db_type' %(KEY_PRE))
            check_privs = CTK.post.get_val ('%s!privs_to_check' %(KEY_PRE))

            # DB access obj
            params = {'db_user': db_user, 'db_pass': db_pass,
                      'db_name': db_name, 'db_type': db_type}

            if db_type == 'mysql':
                db = MySQL (**params)
            elif db_type == 'postgresql':
                db = PostgreSQL (**params)
            elif db_type == 'sqlite3':
                return CTK.cfg_apply_post()
            else:
                raise ValueError, "Unsupported %s" %(str(db_type))

            # The user and password pair
            error = db.is_dbuser_present (db_user, db_pass)
            if error:
                errors = {'%s!db_pass' %(KEY_PRE): error}
                return {'ret':'fail', 'errors': errors}

            # Verify database exists
            error = db.is_dbname_present (db_name)
            if error:
                errors = {'%s!db_name' %(KEY_PRE): _('Database does not exist.')}
                return {'ret':'fail', 'errors': errors}

            # Check priviledges
            privs  = check_privs.split(',')
            errors = db.check_privileges (privs)

            if errors:
                error = {'%s!db_pass' %(KEY_PRE): errors}
                return {'ret':'fail', 'errors': error}

            return CTK.cfg_apply_post()

    def __init__ (self, refresh, dbtypes, privs_to_check):
        CTK.Box.__init__ (self)

        # Ensure there a suitable DB
        supported = get_supported_dbs (dbtypes)
        if not supported:
            self += CTK.RawHTML ('<h1>%s</h1>' %(_("No supported database engines were detected.")))
            self += CTK.RawHTML ('<p>%s: %s</p>' %(_('The available options are'), ', '.join(dbtypes)))
            return

        # DB Type
        self += Database_Type (refresh, dbtypes)

        # DB Details
        db_type = CTK.cfg.get_val ('%s!db_type' %(KEY_PRE))

        table = CTK.PropsTable()
        submit = CTK.Submitter (URL_MANUAL_APPLY)
        submit.bind ('submit_success', table.JS_to_trigger('goto_next_stage'))
        submit += table

        # Privs to check
        submit += CTK.Hidden ('%s!privs_to_check'%(KEY_PRE), ','.join(privs_to_check))

        if db_type in ('mysql', 'postgresql', 'oracle', 'sqlserver'):
            self += Method_Chooser (refresh)
            self += CTK.RawHTML ('<p>%s %s</p>' %(_(NOTE_INTRO_MANUAL), _(NOTE_INTRO_COMMON)))

            table.Add (_('Database'), CTK.TextCfg        ('%s!db_name'%(KEY_PRE), False, {'class':'noauto'}), _(NOTE_DBNAME))
            table.Add (_('Username'), CTK.TextCfg        ('%s!db_user'%(KEY_PRE), False, {'class':'noauto'}), _(NOTE_DBUSER))
            table.Add (_('Password'), CTK.TextCfgPassword('%s!db_pass'%(KEY_PRE), False, {'class':'noauto'}), _(NOTE_DBPASS))

        else:
            submit += CTK.Hidden('%s!empty_db'%(KEY_PRE),'1')

        self += submit


class MethodSelection_Refresh (CTK.Container):
    def __init__ (self, refresh, parent_widget):
        CTK.Container.__init__ (self)

        dbtypes        = parent_widget.dbtypes
        privs_to_check = parent_widget.privs_to_check

        default = METHODS[0][0]
        method  = CTK.cfg.get_val ('%s!method'%(KEY_PRE), default)

        if method == 'automatic':  # provide root password and it creates DB + user
            self += Method_Automatic (refresh, dbtypes)
        elif method == 'manual':   # provide existing user, password and db_name
            self += Method_Manual (refresh, dbtypes, privs_to_check)
        else:
            self += CTK.RawHTML ('<h1>%s</h1>' %(_("Unknown method")))


#
# GUI: Classes that are instanced from within package installer
#

class MethodSelection (CTK.Box):
    """Widget to select manual/automatic configuration for the
    provided dbtypes that are available to the system.

    It must be instanced with a list of database engines supported by
    the application, and only the ones available on the system will
    actually be considered. The list must be a subset of ['mysql',
    'postgresql', 'sqlite3']

    Upon successful execution, a goto_next_stage event is triggered.
    Once the widget has performed its task, the relevant information
    can be retrieved like this:

    admin_user = CTK.cfg.get_val('tmp!market!install!db!admin_user')
    admin_pass = CTK.cfg.get_val('tmp!market!install!db!admin_pass')
    dbtype     = CTK.cfg.get_val('tmp!market!install!db!db_type')
    dbname     = CTK.cfg.get_val('tmp!market!install!db!db_name')
    dbuser     = CTK.cfg.get_val('tmp!market!install!db!db_user')
    dbpass     = CTK.cfg.get_val('tmp!market!install!db!db_pass')
    """
    def __init__ (self, dbtypes=[]):
        CTK.Box.__init__ (self)

        self.dbtypes        = dbtypes[:]
        self.privs_to_check = ['create_table', 'write']

        refresh = CTK.Refreshable({'id': 'market-db-method-selection-refresh'})
        refresh.register (lambda: MethodSelection_Refresh (refresh, self).Render())

        self += CTK.RawHTML ("<h2>%s</h2>" %(_("Database configuration")))
        self += refresh


class PreconditionError (CTK.Box):
    """Widget that displays an error when database preconditions are
    not met. It must be instanced with a list of database entries such
    as the one provided by DatabaseDetector.get_supported().

    It also displays an InstructionBox with relevant installation
    information for the current platform.
    """
    def __init__ (self, dbtypes):
        CTK.Box.__init__ (self)

        self += CTK.RawHTML ('<h1>%s</h1>' %(_("No supported database engines were detected.")))

        if not dbtypes:
            note = _("This installer doesn't seem to support any databases.")
        elif len(dbtypes) == 1:
            note = '%s %s.' %(_('The only database supported by this installer is'), dbtypes[0])
        else:
            note = '%s: %s.' %(_('The database options supported by this installer are'), ', '.join(dbtypes))

        instructions = []
        for db in dbtypes:
            if db == 'mysql':
                instructions.append (MYSQL5_INSTRUCTIONS)
            elif db == 'postgresql':
                instructions.append (PGSQL8_INSTRUCTIONS)
            elif db == 'sqlite3':
                instructions.append (PYSQLITE3_INSTRUCTIONS)

        self += InstructionBox (note, instructions)



CTK.publish ('^%s$'%(URL_DBTYPE_APPLY), Database_Type.Apply,    method="POST")
CTK.publish ('^%s$'%(URL_METHOD_APPLY), Method_Chooser.Apply,   method="POST")
CTK.publish ('^%s$'%(URL_AUTO_APPLY),   Method_Automatic.Apply, method="POST")
CTK.publish ('^%s$'%(URL_MANUAL_APPLY), Method_Manual.Apply,    method="POST")
