DEBUG = False
APP_ROOT = '/var/www/graveyard'

try:
    from settings_local import *
except ImportError:
    pass
