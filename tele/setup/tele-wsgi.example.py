# WSGI Handler sample configuration file.
#
# Change the appropriate settings below, in order to provide the parameters
# that would normally be passed in the command-line.
# (at least conf['applets_path'])
#
# For generic wsgi handlers a global application is defined.
# For uwsgi this should work:
#   $ uwsgi_python --http :9090 --pythonpath . --wsgi-file tele-wsgi.py
#
# For gunicorn additional globals need to be defined in the Gunicorn section.
# Then the following command should run:
#   $ gunicorn tele:service.wsgi_server.application -c tele-wsgi.py

import tele

#----------------------------------------------------------
# Common
#----------------------------------------------------------
tele.multi_process = True # Nah!

# Equivalent of --load command-line option
tele.conf.server_wide_modules = ['base', 'web']
conf = tele.tools.config

# Path to the tele Applets repository (comma-separated for
# multiple locations)

conf['applets_path'] = '../../applets/trunk,../../web/trunk/applets'

# Optional database config if not using local socket
#conf['db_name'] = 'mycompany'
#conf['db_host'] = 'localhost'
#conf['db_user'] = 'foo'
#conf['db_port'] = 5432
#conf['db_password'] = 'secret'

#----------------------------------------------------------
# Generic WSGI handlers application
#----------------------------------------------------------
application = tele.service.wsgi_server.application

tele.service.server.load_server_wide_modules()

#----------------------------------------------------------
# Gunicorn
#----------------------------------------------------------
# Standard tele XML-RPC port is 8069
bind = '127.0.0.1:8069'
pidfile = '.gunicorn.pid'
workers = 4
timeout = 240
max_requests = 2000
