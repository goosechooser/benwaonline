import os
import functools
from config import app_config
from flask import session, redirect, url_for, request

class back(object):
    """To be used in views.

    Use `anchor` decorator to mark a view as a possible point of return.

    `url()` is the last saved url.

    Use `redirect` to return to the last return point visited.
    """
    cfg = app_config[os.getenv('FLASK_CONFIG')]
    cookie = cfg.REDIRECT_BACK_COOKIE if hasattr(cfg, 'REDIRECT_BACK_COOKIE') else 'back'
    default_view = cfg.REDIRECT_BACK_DEFAULT if hasattr(cfg, 'REDIRECT_BACK_DEFAULT') else 'index'

    @staticmethod
    def anchor(func, cookie=cookie):
        @functools.wraps(func)
        def result(*args, **kwargs):
            session[cookie] = request.url
            return func(*args, **kwargs)
        return result

    @staticmethod
    def url(default=default_view, cookie=cookie):
        return session.get(cookie, url_for(default))

    @staticmethod
    def redirect(default=default_view, cookie=cookie):
        return redirect(back.url(default, cookie))

back = back()
