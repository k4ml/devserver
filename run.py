#!/usr/bin/env python

from optparse import OptionParser
from os.path import join, dirname, abspath
from string import Template

import os, sys

parser = OptionParser()
parser.add_option("-a", "--address", default="127.0.0.1", help="Server address to listen")
parser.add_option("-p", "--port", default="8000", help="Server port to listen")
parser.add_option("-k", "--command", help="Apache2 command to run")
parser.add_option("-b", "--httpd", default="apache2", help="Apache2 httpd binary to run")
parser.add_option("-m", "--module", default="/usr/lib/apache2", help="Apache2 modules path")
parser.add_option("-e", "--exclude-module", default='', help="apache module to exclude")
parser.add_option("--wsgi", default=False, action='store_true', help="Enable wsgi or not")

(option, args) = parser.parse_args()

APP_ROOT = abspath(join((dirname(__file__)), '../'))
DOC_ROOT = join(APP_ROOT, 'www')
SERVER_ROOT = join(APP_ROOT, 'server')
CONFIG_FILE = join(SERVER_ROOT, 'apache2.conf')

if option.command in ('stop', 'restart'):
    ret = os.system("%s -f %s -k %s" % (option.httpd, CONFIG_FILE, option.command))
    if ret == 0:
        print "%s apache2 ..." % option.command
    sys.exit()

MODULES = (
    'alias_module',
    'auth_basic_module',
    'authn_file_module',
    'authz_default_module',
    'authz_groupfile_module',
    'authz_host_module',
    'authz_user_module',
    'autoindex_module',
    'cgi_module',
    'dir_module',
    'env_module',
    'mime_module',
    'negotiation_module',
    'php5_module',
    'rewrite_module',
    'setenvif_module',
    'status_module',
    'userdir_module',
    'log_config_module',
    'wsgi_module',
)

config_modules = list()
for module in MODULES:
    if module in option.exclude_module.split(':'):
        continue
    module_so = 'mod_%s.so' % module.replace('_module', '')
    config_modules.append('LoadModule %s modules/%s' % (module, module_so))

CONFIG_MODULES = "\n".join(config_modules)

CONFIG = """
ServerRoot $module

${modules}

TypesConfig /etc/mime.types

KeepAlive Off
Listen $address:$port
LogFormat "%h %l %u %t \\"%r\\" %>s %b \\"%{Referer}i\\" \\"%{User-Agent}i\\" \\"%{Host}i\\"" combined
CustomLog $server_root/access_log combined
ErrorLog ${server_root}/error_log

ServerName localhost
 
PidFile ${server_root}/apache2.pid

#
# Cause the PHP interpreter to handle files with a .php extension.
#
AddHandler php5-script .php
AddType text/html .php

${config_wsgi}

DirectoryIndex index.php

DocumentRoot $doc_root
<Directory />
    Options FollowSymLinks
    AllowOverride None
</Directory>
<Directory ${doc_root}>
    Options Indexes FollowSymLinks MultiViews
    AllowOverride All
    Order allow,deny
    allow from all
</Directory>
"""

CONFIG_WSGI = """
WSGIDaemonProcess dev threads=2 display-name=%{GROUP} python-path=${app_root}/lib/python2.6/site-packages:${app_root}/app
WSGIProcessGroup dev
WSGISocketPrefix ${server_root}/wsgi
WSGIScriptAlias / ${app_root}/wsgi/run.wsgi
"""

if 0:
    print "Option are: ", option
    print "Args are: ", args
    print APP_ROOT
    print CONFIG_FILE

template = Template(CONFIG)
template_wsgi = Template(CONFIG_WSGI)
template_vars = {
    'doc_root': DOC_ROOT,
    'server_root': SERVER_ROOT,
    'app_root': APP_ROOT,
    'address': option.address,
    'port': option.port,
    'httpd': option.httpd,
    'module': option.module,
    'modules': CONFIG_MODULES,
    'config_wsgi': '',
}

if option.wsgi:
    template_vars['config_wsgi'] = template_wsgi.substitute(template_vars)

f = open(CONFIG_FILE, "w")
try:
    f.write(template.substitute(template_vars))
finally:
    f.flush()
    f.close()

ret = os.system("%s -f %s -k start" % (option.httpd, CONFIG_FILE))
if ret == 0:
    print "Running apache at %s:%s" % (option.address, option.port)
