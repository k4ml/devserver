#!/usr/bin/env python

from optparse import OptionParser
from os.path import join, dirname, abspath
from string import Template

import os, sys

parser = OptionParser()
parser.add_option("-a", "--address", default="127.0.0.1", help="Server address to listen")
parser.add_option("-p", "--port", default="8000", help="Server port to listen")
parser.add_option("-k", "--command", help="Apache2 command to run")

(option, args) = parser.parse_args()

APP_ROOT = abspath(join((dirname(__file__)), '../'))
DOC_ROOT = join(APP_ROOT, 'www')
SERVER_ROOT = join(APP_ROOT, 'server')
CONFIG_FILE = join(SERVER_ROOT, 'apache2.conf')

if option.command in ('stop', 'restart'):
    ret = os.system("apache2 -f %s -k %s" % (CONFIG_FILE, option.command))
    if ret == 0:
        print "%s apache2 ..." % option.command
    sys.exit()

CONFIG = """
LoadModule alias_module /usr/lib/apache2/modules/mod_alias.so
LoadModule auth_basic_module /usr/lib/apache2/modules/mod_auth_basic.so
LoadModule authn_file_module /usr/lib/apache2/modules/mod_authn_file.so
LoadModule authz_default_module /usr/lib/apache2/modules/mod_authz_default.so
LoadModule authz_groupfile_module /usr/lib/apache2/modules/mod_authz_groupfile.so
LoadModule authz_host_module /usr/lib/apache2/modules/mod_authz_host.so
LoadModule authz_user_module /usr/lib/apache2/modules/mod_authz_user.so
LoadModule autoindex_module /usr/lib/apache2/modules/mod_autoindex.so
LoadModule cgi_module /usr/lib/apache2/modules/mod_cgi.so
LoadModule dir_module /usr/lib/apache2/modules/mod_dir.so
LoadModule env_module /usr/lib/apache2/modules/mod_env.so
LoadModule mime_module /usr/lib/apache2/modules/mod_mime.so
LoadModule negotiation_module /usr/lib/apache2/modules/mod_negotiation.so
LoadModule php5_module /usr/lib/apache2/modules/libphp5.so
LoadModule rewrite_module /usr/lib/apache2/modules/mod_rewrite.so
LoadModule setenvif_module /usr/lib/apache2/modules/mod_setenvif.so
LoadModule status_module /usr/lib/apache2/modules/mod_status.so
LoadModule userdir_module /usr/lib/apache2/modules/mod_userdir.so

TypesConfig /etc/mime.types

KeepAlive Off
Listen $address:$port
LogFormat "%h %l %u %t \\"%r\\" %>s %b \\"%{Referer}i\\" \\"%{User-Agent}i\\" \\"%{Host}i\\"" combined
CustomLog $server_root/access_log combined
ErrorLog ${server_root}/error_log

ServerName localhost
 
PidFile ${server_root}/apache2.pid

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

if 0:
    print "Option are: ", option
    print "Args are: ", args
    print APP_ROOT
    print CONFIG_FILE

template = Template(CONFIG)
template_vars = {
    'doc_root': DOC_ROOT,
    'server_root': SERVER_ROOT,
    'address': option.address,
    'port': option.port,
}

f = open(CONFIG_FILE, "w")
try:
    f.write(template.substitute(template_vars))
finally:
    f.flush()
    f.close()

ret = os.system("apache2 -f %s -k start" % CONFIG_FILE)
if ret == 0:
    print "Running apache at %s:%s" % (option.address, option.port)
