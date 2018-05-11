import os
from flask_caching import Cache
from benwaonline.config import app_config

cfg = app_config[os.getenv('FLASK_CONFIG')]

cache = Cache(config={
    'CACHE_TYPE': 'redis',
    'CACHE_DEFAULT_TIMEOUT': 5,
    'CACHE_REDIS_HOST': cfg.REDIS_HOST,
    'CACHE_KEY_PREFIX': 'benwaonline:'
})
