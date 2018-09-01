import os
import gevent.monkey


gevent.monkey.patch_thread()
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "HalliganAvailability.settings")

from ws4redis.uwsgi_runserver import uWSGIWebsocketServer
application = uWSGIWebsocketServer()
