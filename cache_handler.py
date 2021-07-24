__all__ = ['CacheHandler', 'CacheFileHandler', 'DjangoSessionCacheHandler', 'MemoryCacheHandler']

import errno
import json
import logging
import os
from spotipy.util import CLIENT_CREDS_ENV_VARS
from spotipy.cache_handler import CacheHandler

logger = logging.getLogger(__name__)

class MemoryCacheHandler(CacheHandler):
    """
    A cache handler that simply stores the token info in memory as an
    instance attribute of this class. The token info will be lost when this
    instance is freed.
    """

    def __init__(self, token_info=None):
        """
        Parameters:
            * token_info: The token info to store in memory. Can be None.
        """
        self.token_info = token_info

    def get_cached_token(self):
        return self.token_info

    def save_token_to_cache(self, token_info):
        self.token_info = token_info


class DjangoSessionCacheHandler(CacheHandler):
    """
    A cache handler that stores the token info in the session framework
    provided by Django.
    Read more at https://docs.djangoproject.com/en/3.2/topics/http/sessions/
    """

    def __init__(self, request):
        """
        Parameters:
            * request: HttpRequest object provided by Django for every
            incoming request
        """
        self.request = request

    def get_cached_token(self):
        token_info = None
        try:
            token_info = self.request.session['token_info']
        except KeyError:
            logger.debug("Token not found in the session")

        return token_info

    def save_token_to_cache(self, token_info):
        try:
            self.request.session['token_info'] = token_info
        except Exception as e:
            logger.warning("Error saving token to cache: " + str(e))