# -*- coding: utf-8 -*-
#
# Cherokee Distribution
#
# Authors:
#      Alvaro Lopez Ortega <alvaro@alobbs.com>
#
# Copyright (C) 2011 Alvaro Lopez Ortega
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of version 2 of the GNU General Public
# License as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#

"""
Detection of PHP modules
"""

import CTK
from util import *

php = CTK.load_module_pyc (os.path.join (os.path.dirname (os.path.realpath (__file__)), "php.pyo"), "php_util")

PHP_GD_NOTE = N_("The 'gd' module is not supported by your PHP interpreter")
PHP_GD_INST = {
    'apt':           "sudo apt-get install php5-gd",
    'zypper':        "sudo zypper install php5-gd",
    'macports':      "sudo port install php5-gd",
    'yum':           "sudo yum install php-gd",
    'freebsd_pkg':   "pkg_add -r php5-gd",
    'freebsd_ports': "cd /usr/ports/graphics/php5-gd && make install",
    'default':       N_("For more about this module visit %(url)s") %({'url': 'http://php.net/manual/en/book.image.php'}),
}

PHP_MYSQL_NOTE = N_("Neither the 'mysql' nor the 'mysqli' modules are supported by your PHP interpreter")
PHP_MYSQL_INST = {
    'apt':           "sudo apt-get install php5-mysql",
    'zypper':        "sudo zypper install php5-mysql",
    'macports':      "sudo port install php5-mysql",
    'yum':           "sudo yum install php-mysql",
    'ips':           "pfexec pkg install 'pkg:/web/php*/extension/php-mysql'",
    'freebsd_pkg':   "pkg_add -r php5-mysql php5-mysqli",
    'freebsd_ports': "cd /usr/ports/databases/php5-mysql && make install",
    'default':       N_("For more about this module visit %(url)s") %({'url': 'http://php.net/manual/en/book.mysql.php'}),
}

PHP_PDOMYSQL_NOTE = N_("The 'pdo_mysql' module is not supported by your PHP interpreter")
PHP_PDOMYSQL_INST = {
    'apt':           "sudo apt-get install php5-mysql",
    'zypper':        "sudo zypper install php5-mysql",
    'macports':      "sudo port install php5-mysql",
    'yum':           "sudo yum install php-mysql",
    'ips':           "pfexec pkg install 'pkg:/web/php*/extension/php-mysql'",
    'freebsd_pkg':   "pkg_add -r php5-pdo_mysql",
    'freebsd_ports': "cd /usr/ports/databases/php5-pdo_mysql && make install",
    'default':       N_("For more about this module visit %(url)s") %({'url': 'http://php.net/manual/en/ref.pdo-mysql.php'}),
}

PHP_PGSQL_NOTE = N_("The 'pgsql' module is not supported by your PHP interpreter")
PHP_PGSQL_INST = {
    'apt':           "sudo apt-get install php5-pgsql",
    'zypper':        "sudo zypper install php5-pgsql",
    'macports':      "sudo port install php5-postgresql",
    'yum':           "sudo yum install php-pgsql",
    'ips':           "pfexec pkg install 'pkg:/web/php*/extension/php-pgsql'",
    'freebsd_pkg':   "pkg_add -r php5-pgsql",
    'freebsd_ports': "cd /usr/ports/databases/php5-pgsql && make install",
    'default':       N_("For more about this module visit %(url)s") %({'url': 'http://php.net/manual/en/book.pgsql.php'}),
}

PHP_CURL_NOTE = N_("The 'curl' module is not supported by your PHP interpreter")
PHP_CURL_INST = {
    'apt':           "sudo apt-get install php5-curl",
    'zypper':        "sudo zypper install php5-curl",
    'macports':      "sudo port install php5-curl",
    'freebsd_pkg':   "pkg_add -r php5-curl",
    'freebsd_ports': "cd /usr/ports/ftp/php5-curl && make install",
    'default':       N_("For more about this module visit %(url)s") %({'url': 'http://php.net/manual/en/book.curl.php'}),
}

PHP_SQLITE_NOTE = N_("The 'sqlite' module is not supported by your PHP interpreter")
PHP_SQLITE_INST = {
    'apt':           "sudo apt-get install php5-sqlite",
    'zypper':        "sudo zypper install php5-sqlite",
    'macports':      "sudo port install php5-sqlite",
    'freebsd_pkg':   "pkg_add -r php5-sqlite",
    'freebsd_ports': "cd /usr/ports/databases/php5-sqlite && make install",
    'default':       N_("For more about this module visit %(url)s") %({'url': 'http://php.net/manual/en/book.sqlite.php'}),
}

PHP_MCRYPT_NOTE = N_("The 'mcrypt' module is not supported by your PHP interpreter")
PHP_MCRYPT_INST = {
    'apt':           "sudo apt-get install php5-mcrypt",
    'zypper':        "sudo zypper install php5-mcrypt",
    'macports':      "sudo port install php5-mcrypt",
    'yum':           "sudo yum install php-mcrypt",
    'freebsd_pkg':   "pkg_add -r php5-mcrypt",
    'freebsd_ports': "cd /usr/ports/security/php5-mcrypt && make install",
    'default':       N_("For more about this module visit %(url)s") %({'url': 'http://php.net/manual/en/book.mcrypt.php'}),
}

PHP_INTL_NOTE = N_("The 'intl' module is not supported by your PHP interpreter")
PHP_INTL_INST = {
    'apt':           "sudo apt-get install php5-intl",
    'zypper':        "sudo zypper install php5-intl",
    'macports':      "sudo port install php5-intl",
    'yum':           "sudo yum install php-intl",
    'default':       N_("For more about this module visit %(url)s") %({'url': 'http://php.net/manual/en/book.intl.php'}),
}

PHP_ICONV_NOTE = N_("The 'iconv' module is not supported by your PHP interpreter")
PHP_ICONV_INST = {
    'yum':           "sudo yum install php-iconv",
    'zypper':        "sudo zypper install php5-iconv",
    'macports':      "sudo port install php5-iconv",
    'freebsd_pkg':   "pkg_add -r php5-iconv",
    'freebsd_ports': "cd /usr/ports/converters/php5-iconv && make install",
    'apt':           N_("The iconv module should be built-in."),
    'default':       N_("For more about this module visit %(url)s") %({'url': 'http://php.net/manual/en/book.iconv.php'}),
}

PHP_OPENSSL_NOTE = N_("The 'openssl' module is not supported by your PHP interpreter")
PHP_OPENSSL_INST = {
    'yum':           "sudo yum install php-openssl",
    'zypper':        "sudo zypper install php5-openssl",
    'macports':      "sudo port install php5-openssl",
    'freebsd_pkg':   "pkg_add -r php5-openssl",
    'freebsd_ports': "cd /usr/ports/security/php5-openssl && make install",
    'apt':           N_("The openssl module should be built-in the php interpreter."),
    'default':       N_("For more about this module visit %(url)s") %({'url': 'http://php.net/manual/en/book.openssl.php'}),
}

PHP_XMLRPC_NOTE = N_("The 'xmlrpc' module is not supported by your PHP interpreter")
PHP_XMLRPC_INST = {
    'yum':           "sudo yum install php-xmlrpc",
    'zypper':        "sudo zypper install php5-xmlrpc",
    'macports':      "sudo port install php5-xmlrpc",
    'freebsd_pkg':   "pkg_add -r php5-xmlrpc",
    'freebsd_ports': "cd /usr/ports/net/php5-xmlrpc && make install",
    'default':       N_("For more about this module visit %(url)s") %({'url': 'http://php.net/manual/en/book.xmlrpc.php'}),
}

PHP_MBSTRING_NOTE = N_("The 'mbstring' module is not supported by your PHP interpreter")
PHP_MBSTRING_INST = {
    'yum':           "sudo yum install php-mbstring",
    'zypper':        "sudo zypper install php5-mbstring",
    'macports':      "sudo port install php5-mbstring",
    'freebsd_pkg':   "pkg_add -r php5-mbstring",
    'freebsd_ports': "cd /usr/ports/converters/php5-mbstring && make install",
    'apt':           N_("The mbstring module should be built-in the php interpreter."),
    'default':       N_("For more about this module visit %(url)s") %({'url': 'http://php.net/manual/en/book.mbstring.php'}),
}

PHP_SESSION_NOTE = N_("The 'session' module is not supported by your PHP interpreter")
PHP_SESSION_INST = {
    'freebsd_pkg':   "pkg_add -r php5-session",
    'freebsd_ports': "cd /usr/ports/www/php5-session && make install",
    'default':       N_("For more about this module visit %(url)s") %({'url': 'http://php.net/manual/en/book.session.php'}),
}

PHP_CTYPE_NOTE = N_("The 'ctype' module is not supported by your PHP interpreter")
PHP_CTYPE_INST = {
    'freebsd_pkg':   "pkg_add -r php5-ctype",
    'freebsd_ports': "cd /usr/ports/textproc/php5-ctype && make install",
    'default':       N_("For more about this module visit %(url)s") %({'url': 'http://php.net/manual/en/book.ctype.php'}),
}

PHP_SPL_NOTE = N_("The Stantad PHP Library (SPL) module is not supported by your PHP interpreter")
PHP_SPL_INST = {
    'default':       N_("For more about this module visit %(url)s") %({'url': 'http://php.net/manual/en/book.spl.php'}),
}

PHP_ZLIB_NOTE = N_("The 'zlib' module is not supported by your PHP interpreter")
PHP_ZLIB_INST = {
    'freebsd_pkg':   "pkg_add -r php5-zlib",
    'freebsd_ports': "cd /usr/ports/archivers/php5-zlib && make install",
    'default':       N_("For more about this module visit %(url)s") %({'url': 'http://php.net/manual/en/book.zlib.php'}),
}

PHP_ZIP_NOTE = N_("The 'zip' module is not supported by your PHP interpreter")
PHP_ZIP_INST = {
    'freebsd_pkg':   "pkg_add -r php5-zip",
    'freebsd_ports': "cd /usr/ports/archivers/php5-zip && make install",
    'default':       N_("For more about this module visit %(url)s") %({'url': 'http://php.net/manual/en/book.zip.php'}),
}

PHP_XML_NOTE = N_("The 'xml' module is not supported by your PHP interpreter")
PHP_XML_INST = {
    'yum':           "sudo yum install php-xml",
    'freebsd_pkg':   "pkg_add -r php5-xml",
    'freebsd_ports': "cd /usr/ports/textproc/php5-xml && make install",
    'default':       N_("For more about this module visit %(url)s") %({'url': 'http://php.net/manual/en/book.xml.php'}),
}

PHP_XMLWRITER_NOTE = N_("The 'xmlwriter' module is not supported by your PHP interpreter")
PHP_XMLWRITER_INST = {
    'yum':           "sudo yum install php-xml",
    'freebsd_pkg':   "pkg_add -r php5-xmlwriter",
    'freebsd_ports': "cd /usr/ports/textproc/php5-xmlwriter && make install",
    'default':       N_("For more about this module visit %(url)s") %({'url': 'http://php.net/manual/en/book.xmlwriter.php'}),
}

PHP_XMLREADER_NOTE = N_("The 'xmlreader' module is not supported by your PHP interpreter")
PHP_XMLREADER_INST = {
    'yum':           "sudo yum install php-xml",
    'freebsd_pkg':   "pkg_add -r php5-xmlreader",
    'freebsd_ports': "cd /usr/ports/textproc/php5-xmlreader && make install",
    'default':       N_("For more about this module visit %(url)s") %({'url': 'http://php.net/manual/en/book.xmlreader.php'}),
}

PHP_SIMPLEXML_NOTE = N_("The 'SimpleXML' module is not supported by your PHP interpreter")
PHP_SIMPLEXML_INST = {
    'freebsd_pkg':   "pkg_add -r php5-simplexml",
    'freebsd_ports': "cd /usr/ports/textproc/php5-simplexml && make install",
    'default':       N_("For more about this module visit %(url)s") %({'url': 'http://php.net/manual/en/book.simplexml.php'}),
}

PHP_PCRE_NOTE = N_("The 'pcre' module is not supported by your PHP interpreter")
PHP_PCRE_INST = {
    'default':       N_("For more about this module visit %(url)s") %({'url': 'http://php.net/manual/en/book.pcre.php'}),
}

PHP_DOM_NOTE = N_("The 'dom' module is not supported by your PHP interpreter")
PHP_DOM_INST = {
    'freebsd_pkg':   "pkg_add -r php5-dom",
    'freebsd_ports': "cd /usr/ports/textproc/php5-dom && make install",
    'default':       N_("For more about this module visit %(url)s") %({'url': 'http://php.net/manual/en/book.dom.php'}),
}

PHP_JSON_NOTE = N_("The 'json' module is not supported by your PHP interpreter")
PHP_JSON_INST = {
    'freebsd_pkg':   "pkg_add -r php5-json",
    'freebsd_ports': "cd /usr/ports/devel/php5-json && make install",
    'default':       N_("For more about this module visit %(url)s") %({'url': 'http://php.net/manual/en/book.json.php'}),
}

PHP_PDO_NOTE = N_("The 'PDO' module is not supported by your PHP interpreter")
PHP_PDO_INST = {
    'freebsd_pkg':   "pkg_add -r php5-pdo",
    'freebsd_ports': "cd /usr/ports/databases/php5-pdo && make install",
    'default':       N_("For more about this module visit %(url)s") %({'url': 'http://php.net/manual/en/book.pdo.php'}),
}

PHP_ZIP_NOTE = N_("The 'zip' module is not supported by your PHP interpreter")
PHP_ZIP_INST = {
    'zypper':        "sudo zypper install php5-zip",
    'freebsd_pkg':   "pkg_add -r php5-zip",
    'freebsd_ports': "cd /usr/ports/archivers/php5-zip && make install",
    'apt':           N_("The zip module should be built-in the php interpreter."),
    'default':       N_("For more about this module visit %(url)s") %({'url': 'http://php.net/manual/en/book.zip.php'}),
}

PHP_HASH_NOTE = N_("The 'hash' module is not supported by your PHP interpreter")
PHP_HASH_INST = {
    'freebsd_pkg':   "pkg_add -r php5-hash",
    'freebsd_ports': "cd /usr/ports/security/php5-hash && make install",
    'default':       N_("For more about this module visit %(url)s") %({'url': 'http://php.net/manual/en/book.hash.php'}),
}

PHP_FILTER_NOTE = N_("The 'filter' module is not supported by your PHP interpreter")
PHP_FILTER_INST = {
    'freebsd_pkg':   "pkg_add -r php5-filter",
    'freebsd_ports': "cd /usr/ports/security/php5-filter && make install",
    'default':       N_("For more about this module visit %(url)s") %({'url': 'http://php.net/manual/en/book.filter.php'}),
}

PHP_TOKENIZER_NOTE = N_("The 'tokenizer' module is not supported by your PHP interpreter")
PHP_TOKENIZER_INST = {
    'freebsd_pkg':   "pkg_add -r php5-tokenizer",
    'freebsd_ports': "cd /usr/ports/devel/php5-filter && make install",
    'default':       N_("For more about this module visit %(url)s") %({'url': 'http://php.net/manual/en/book.tokenizer.php'}),
}

PHP_UNKNOWN_NOTE = N_("The '%(module)s' module is not supported by your PHP interpreter")
PHP_UNKNOWN_INST = {
    'freebsd_pkg':   "pkg_add -r php5-extensions",
    'freebsd_ports': "cd /usr/ports/lang/php5-extensions && make install",
    'default':       N_("For more about this module visit http://php.net/manual/en/book.%(module)s.php"),
}


def check_module (module, mods_available=None):
    """Check if specified PHP module is available. If an optional
    mods_available list is provided, perform the check among its
    contents only.

    Returns InstructionBox-suitable touples on failure: (note,
    instruction_dictionary)"""

    if not mods_available:
        mods_available = [x.lower() for x in php.figure_modules()]

    if module in mods_available:
        return

    # Modules
    if module in ('mysql', 'mysqli'):
        return (PHP_MYSQL_NOTE, PHP_MYSQL_INST)
    elif module == 'pdo_mysql':
        return (PHP_PDOMYSQL_NOTE, PHP_PDOMYSQL_INST)
    elif module in ('gd', 'gd2'):
        return (PHP_GD_NOTE, PHP_GD_INST)
    elif module == 'pgsql':
        return (PHP_PGSQL_NOTE, PHP_PGSQL_INST)
    elif module == 'curl':
        return (PHP_CURL_NOTE, PHP_CURL_INST)
    elif module == 'mcrypt':
        return (PHP_MCRYPT_NOTE, PHP_MCRYPT_INST)
    elif module == 'intl':
        return (PHP_INTL_NOTE, PHP_INTL_INST)
    elif module == 'iconv':
        return (PHP_ICONV_NOTE, PHP_ICONV_INST)
    elif module == 'openssl':
        return (PHP_OPENSSL_NOTE, PHP_OPENSSL_INST)
    elif module == 'xmlrpc':
        return (PHP_XMLRPC_NOTE, PHP_XMLRPC_INST)
    elif module == 'mbstring':
        return (PHP_MBSTRING_NOTE, PHP_MBSTRING_INST)

    # Built-in modules
    elif module == 'session':
        return (PHP_SESSION_NOTE, PHP_SESSION_INST)
    elif module == 'ctype':
        return (PHP_CTYPE_NOTE, PHP_CTYPE_INST)
    elif module == 'spl':
        return (PHP_SPL_NOTE, PHP_SPL_INST)
    elif module == 'zlib':
        return (PHP_ZLIB_NOTE, PHP_ZLIB_INST)
    elif module == 'zip':
        return (PHP_ZIP_NOTE, PHP_ZIP_INST)
    elif module == 'xml':
        return (PHP_XML_NOTE, PHP_XML_INST)
    elif module == 'xmlwriter':
        return (PHP_XMLWRITER_NOTE, PHP_XMLWRITER_INST)
    elif module == 'xmlreader':
        return (PHP_XMLREADER_NOTE, PHP_XMLREADER_INST)
    elif module == 'simplexml':
        return (PHP_SIMPLEXML_NOTE, PHP_SIMPLEXML_INST)
    elif module == 'pcre':
        return (PHP_PCRE_NOTE, PHP_PCRE_INST)
    elif module == 'dom':
        return (PHP_DOM_NOTE, PHP_DOM_INST)
    elif module == 'json':
        return (PHP_JSON_NOTE, PHP_JSON_INST)
    elif module == 'pdo':
        return (PHP_PDO_NOTE, PHP_PDO_INST)
    elif module == 'hash':
        return (PHP_HASH_NOTE, PHP_HASH_INST)
    elif module == 'filter':
        return (PHP_FILTER_NOTE, PHP_FILTER_INST)
    elif module == 'tokenizer':
        return (PHP_TOKENIZER_NOTE, PHP_TOKENIZER_INST)


    # Unknown
    note = PHP_UNKNOWN_NOTE %(locals())
    inst = PHP_UNKNOWN_INST.copy()
    inst['default'] = inst['default'] %(locals())

    return (note, inst)


def check_modules (modules):
    """Check if list of specified PHP modules is available.

    Returns a list of InstructionBox-touple for each failure, such as:
    [(note, instruction_dictionary), (note, instruction_dictionary),
    ...]"""
    mods_available = [x.lower() for x in php.figure_modules()]

    errors = []
    if type(modules) == str:
        modules = [modules]

    for module in modules:
        error = check_module (module, mods_available)
        if error:
            errors.append (error)

    return errors


def supported_db_modules (modules=None):
    """Read list of PHP supported DB-modules to be fed to
    database.py. Returns the list of all the supported modules, unless
    an input list was specified to restrict the checks to that
    list. The input list must be a subset of ['mysql', 'mysqli',
    'pgsql', 'sqlite3'].

    Returned list is a subset of: [('mysql', 'mysql'), ('pgsql',
    'postgresql'), ('sqlite3', 'sqlite3')]"""

    supported = []
    mods_available = [x.lower() for x in php.figure_modules()]

    if modules == None:
        modules = ['mysql', 'mysqli', 'pgsql', 'sqlite3']
    elif type(modules) == str:
        modules = [modules]

    def add (module, dbname):
        error = check_module (module, mods_available)
        if not error:
            if not dbname in supported:
                supported.append (dbname)

    if 'mysql' in modules or 'mysqli' in modules:
        add('mysql', 'mysql')
    if 'pgsql' in modules or 'postgresql' in modules:
        add('pgsql', 'postgresql')
    if 'sqlite3' in modules:
        add('sqlite3', 'sqlite3')

    return supported
