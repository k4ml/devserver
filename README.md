Simple local apache development server. Assuming directory structure as:-

<pre>
server www
</pre>

with `www` as document root.

<pre>
$ cd server
$ ./run.py
Running apache at 127.0.0.1:8000
$ ./run.py -k stop
Stopping apache2 ...
</pre>

Enable mod_wsgi, disabling modules:-

<pre>
./run.py -e "php5_module:log_config_module" --wsgi
</pre>
