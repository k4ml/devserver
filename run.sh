#!/bin/bash

usage() {
    cat << EOF
    usage: $0 options

    This script start a single Apache server for local
    development.

    OPTIONS
        -h  Show this message
        -a  Listen address (default to 127.0.0.1)
        -p  Listen port
        -s  Shutdown
EOF
}

shutdown() {
    killall apache2
}

APP_ROOT=`pwd`
DOC_ROOT=$APP_ROOT/../www
CONFIG_FILE=$APP_ROOT/apache2.conf
PORT=8000
ADDRESS=127.0.0.1

while getopts ":ha:p:s" OPTION
    do
        case $OPTION in
            h)
                usage
                exit 1
                ;;
            a)
                ADDRESS=$OPTARG
                ;;
            p)
                PORT=$OPTARG
                ;;
            s)
                shutdown
                exit 0
                ;;
            ?)
                usage
                exit 0
                ;;
        esac
    done 

CONFIG=$( cat <<EOL
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
Listen $ADDRESS:$PORT
LogFormat "%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\"" combined
CustomLog $APP_ROOT/access_log combined
ErrorLog $APP_ROOT/error_log

ServerName localhost
 
PidFile $APP_ROOT/apache2.pid

DirectoryIndex index.php

DocumentRoot $DOC_ROOT
<Directory />
    Options FollowSymLinks
    AllowOverride None
</Directory>
<Directory $DOC_ROOT>
    Options Indexes FollowSymLinks MultiViews
    AllowOverride All
    Order allow,deny
    allow from all
</Directory>
EOL)

echo "$CONFIG" > $CONFIG_FILE
apache2 -f $CONFIG_FILE -k start && \
echo "Starting dev server at http://$ADDRESS:$PORT/ ..."
