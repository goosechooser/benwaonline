import os
from typing import List

from requests import request as _request
from requests import Response
from requests.exceptions import ConnectionError, Timeout, HTTPError

from benwaonline.config import app_config
from benwaonline.exceptions import BenwaOnlineRequestError

cfg = app_config[os.getenv('FLASK_CONFIG')]
API_URL = cfg.API_URL
TokenAuth = 'TokenAuth'
Parameter = 'Parameter'

HEADERS = {
    'Accept': 'application/vnd.api+json',
    'Content-Type': 'application/vnd.api+json'
}

class Gateway(object):

    def _get(self, uri: str, params: Parameter = None) -> Response:
        '''
        Builds and executes a GET request.

        Args:
            uri: is the uri that the request will be sent to
            **kwargs: Arbitrary keyword arguments.

        Returns:
            a Response
        '''

        return request('get', uri, params=params)

    def _post(self, uri: str, data: dict, auth: TokenAuth, params: Parameter = None) -> Response:
        '''
        Builds and executes a POST request for a resource

        Args:
            uri: is the uri that the request will be sent to
            data: the data to be sent with the request
            include:
            **kwargs: Arbitrary keyword arguments.

        Returns:
            a Response
        '''

        return request('post', uri, data=data, params=params, auth=auth)

    def _delete(self, uri: str, auth: TokenAuth, **kwargs) -> Response:
        '''
        Builds and executes a DELETE request for a resource.

        Args:
            uri: is the uri that the request will be sent to
            auth:
            **kwargs: Arbitrary keyword arguments.

        Returns:
            a Response
        '''
        return request('delete', uri, auth=auth, **kwargs)

def request(method: str, url: str, timeout: int = 5, **kwargs) -> Response:
    '''Just wrapping request in exception handling'''
    try:
        response = _request(method, url, headers=HEADERS, timeout=timeout, **kwargs)
    except (ConnectionError, Timeout):
        raise BenwaOnlineRequestError(title='Connection timed out.', detail='Unable to connect to API service.')

    try:
        response.raise_for_status()
    except HTTPError:
        error = handle_http_error(response)
        raise BenwaOnlineRequestError(error)

    return response

def handle_http_error(response: Response) -> dict:
    error = response.json()['errors'][0]
    error['source'] = response.url
    error['headers'] = response.headers

    return error
