REVISION = 17
PY_DEPS  = ['../common/target.py', '../common/database.py', '../common/cc.py', '../common/ruby.py', '../common/cpp.py']
PY_FILES = ['installer.py', 'tools.py']

INCLUDE  = ['redmine', 'rake-0.8.7.gem', 'activesupport-2.3.5.gem', 'activerecord-2.3.5.gem',
            'rack-1.0.1.gem', 'actionpack-2.3.5.gem', 'actionmailer-2.3.5.gem', 'activeresource-2.3.5.gem',
            'rails-2.3.5.gem', 'daemons-1.1.0.gem', 'eventmachine-0.12.10.gem', 'thin-1.2.7.gem', 'cgi_multipart_eof_fix-2.5.0.gem',
            'i18n-0.4.2.gem',
            'mysql-2.8.1.gem', 'postgres-pr-0.6.3.gem', 'sqlite3-1.3.3.gem', 'sqlite3-ruby-1.3.3.gem']

DOWNLOADS = [
    {'dir': 'redmine',
     'url': 'http://rubyforge.org/frs/download.php/74419/redmine-1.1.2.tar.gz',
     'mv':  (('redmine-1.1.2', 'redmine'),)},
    {'url': 'http://files.rubyforge.vm.bytemark.co.uk/rake/rake-0.8.7.gem',           'copy': '.'},
    {'url': 'http://production.cf.rubygems.org/gems/activesupport-2.3.5.gem',         'copy': '.'},
    {'url': 'http://production.cf.rubygems.org/gems/activerecord-2.3.5.gem',          'copy': '.'},
    {'url': 'http://files.rubyforge.vm.bytemark.co.uk/rack/rack-1.0.1.gem',           'copy': '.'},
    {'url': 'http://production.cf.rubygems.org/gems/actionpack-2.3.5.gem',            'copy': '.'},
    {'url': 'http://production.cf.rubygems.org/gems/actionmailer-2.3.5.gem',          'copy': '.'},
    {'url': 'http://production.cf.rubygems.org/gems/activeresource-2.3.5.gem',        'copy': '.'},
    {'url': 'http://rubygems.org/downloads/rails-2.3.5.gem',                          'copy': '.'},
    {'url': 'http://production.cf.rubygems.org/gems/daemons-1.1.0.gem',               'copy': '.'},
    {'url': 'http://production.cf.rubygems.org/gems/eventmachine-0.12.10.gem',        'copy': '.'},
    {'url': 'http://production.cf.rubygems.org/gems/thin-1.2.7.gem',                  'copy': '.'},
    {'url': 'http://production.cf.rubygems.org/gems/mysql-2.8.1.gem',                 'copy': '.'},
    {'url': 'http://production.cf.rubygems.org/gems/postgres-pr-0.6.3.gem',           'copy': '.'},
    {'url': 'http://production.cf.rubygems.org/gems/sqlite3-1.3.3.gem',               'copy': '.'},
    {'url': 'http://production.cf.rubygems.org/gems/sqlite3-ruby-1.3.3.gem',          'copy': '.'},
    {'url': 'http://production.cf.rubygems.org/gems/cgi_multipart_eof_fix-2.5.0.gem', 'copy': '.'},
    {'url': 'http://production.cf.rubygems.org/gems/i18n-0.4.2.gem',                  'copy': '.'},

]

# To trace dependencies: `gem dep <gem_name>`
# To download gem files: `gem fetch <gem_name>`

## Rails
# http://files.rubyforge.vm.bytemark.co.uk/rake/rake-0.8.7.gem
# http://production.cf.rubygems.org/gems/activesupport-2.3.5.gem
# http://rubygems.org/gems/activerecord-2.3.5.gem
# http://files.rubyforge.vm.bytemark.co.uk/rack/rack-1.0.1.gem
# http://production.cf.rubygems.org/gems/actionpack-2.3.5.gem
# http://production.cf.rubygems.org/gems/actionmailer-2.3.5.gem
# http://rubygems.org/gems/activeresource-2.3.5.gem
# http://production.cf.rubygems.org/gems/activesupport-2.3.5.gem

## Thin
#*http://production.cf.rubygems.org/gems/rack-1.2.1.gem
# http://production.cf.rubygems.org/gems/daemons-1.1.0.gem
# http://production.cf.rubygems.org/gems/eventmachine-0.12.10.gem
# http://production.cf.rubygems.org/gems/thin-1.2.7.gem

## MySQL
# http://rubygems.org/gems/mysql-2.8.1.gem
