import json
import os

from requests import request as _request
from requests import Response
from requests.exceptions import ConnectionError, Timeout, HTTPError

from benwaonline.config import app_config
from benwaonline.exceptions import BenwaOnlineRequestError

cfg = app_config[os.getenv('FLASK_CONFIG')]
API_URL = cfg.API_URL

HEADERS = {
    'Accept': 'application/vnd.api+json',
    'Content-Type': 'application/vnd.api+json'
}

def request(method: str, url: str, **kwargs) -> Response:
    '''Just wrapping request in exception handling'''
    try:
        response = _request(method, url, headers=HEADERS, timeout=5, **kwargs)
    except (ConnectionError, Timeout):
        raise BenwaOnlineRequestError(title='Connection timed out.', detail='Unable to connect to API service.')

    try:
        response.raise_for_status()
    except HTTPError:
        errors = response.json()['errors']
        raise BenwaOnlineRequestError(errors[0])

    return response

def prepare_params(include=None, filters=None, page_opts=None, fields=None, **kwargs):
    '''
    Formats an variety of parameters related to FLASK-REST-JSONAPI.

    Args:
        include: is a list of strings containing the resources you want included
        filters: is a list of dicts of ??
        page_opts: is a dict containing options related to pagination of results
            ex: {'size': 10}
        fields: is a dict that will restrict the fields of the result
            ex: {'<resource_type>': [<list of fields (as strings) to return>]}

    Returns:
        a dict.
    '''
    params = {}

    if include:
        params['include'] = ','.join(include)

    if filters:
        params['filter'] = json.dumps(filters)

    if page_opts:
        for k, v in page_opts.items():
            params['page[{}]'.format(k)] = v

    if fields:
        for k, v in fields.items():
            params['fields[{}]'.format(k)] = ','.join(v)

    return params

def get(uri: str, **kwargs) -> Response:
    '''
    Builds and executes a GET request for the collection of a resource

    Args:
        obj: is the Entity of the resource desired
        **kwargs: Arbitrary keyword arguments.

    Returns:
        a Response object that can be turned into a list of Entity with the appropiate from_response() method.
    '''

    params = prepare_params(**kwargs)

    return request('get', uri, params=params)

def get_instance(uri: str, **kwargs) -> Response:
    '''
    Builds and executes a GET request for a single resource.

    Args:
        obj: is the Entity of the resource desired
        **kwargs: Arbitrary keyword arguments

    Returns:
        a Response object that can be turned into an Entity with the appropiate from_response() method.
    '''
    params = prepare_params(**kwargs)

    return request('get', uri, params=params)

def get_resource(uri: str, **kwargs) -> Response:
    '''
    Builds and executes a GET request for a related resource

    Args:
        obj: the Entity instance of the resource that 'has' the resource
        resource_obj: is the Entity of the related resource
        **kwargs: Arbitrary keyword arguments

    Returns:
        a Response object that can be turned into an Entity with the appropiate from_response() method.
    '''
    params = prepare_params(**kwargs)

    return request('get', uri, params=params)

def post(uri, data, include, auth):
    '''
    Builds and executes a POST request for a resource
    Args:
        obj: the Entity instance of the resource
        auth: a TokenAuth() representing the authentication token

    Returns:
        a Response object that can be turned into an Entity with the appropiate from_response() method.
    '''
    params = {'include': ','.join(include)}

    return request('post', uri, data=data, params=params, auth=auth)

def filter(uri, query, **kwargs):
    '''
    Builds and executes a GET request for a collection of resources with a filter appended to the url.

    Args:
        obj: is the Entity of the resource collection desired
        query: a Query object that will be turned into the desired filter
        **kwargs: Arbitrary keyword arguments

    Returns:
        a Response object that can be turned into an Entity with the appropiate from_response() method.
    '''
    params = prepare_params(filters=query.to_filter(), **kwargs)

    return request('get', uri, params=params)

# def patch(obj, attr_obj, auth):
#     '''
#     Builds and executes a PATCH request for a one-to-one resource relationship

#     Args:
#         obj: the Entity instance of the resource containing the relationship
#         attr_obj: is the Entity instance of the resource you want to relate
#         auth: is a TokenAuth() representing the authentication token

#     Returns:
#         a Response object
#     '''
#     uri = API_URL + obj.relationship_uri(attr_obj)
#     data = attr_obj.dumps()
#     return request('patch', uri, data=data, auth=auth)

# def patch_many(obj, attr_objs, auth):
#     '''
#     Builds and executes a PATCH request for a one-to-many resource relationship

#     Args:
#         obj: the Entity instance of the resource containing the relationship
#         attr_objs: a list of Entity instances that you want to want to replace the existing relationship with
#         auth: is a TokenAuth() representing the authentication token

#     Returns:
#         a Response object
#     '''
#     uri = obj.relationship_uri(attr_objs[0])
#     ids = [{'id': str(o.id)} for o in attr_objs]
#     data = attr_objs[0].dumps(many=True, data=ids)

#     return request('patch', uri, data=data, auth=auth)

def add_to(uri: str, data: dict, auth) -> Response:

    '''
    Builds and executes a POST request for a one-to-many resource relationship.
    Use this if you want to add a resource to a one-to-many relationship, instead of replacing it completely.

    Args:
        obj: is the Entity instance of the resource with the relationship you want to add to
        attr_obj: is the Entity instance of the resource you want to add
        auth: is a TokenAuth() representing the authentication token

    Returns:
        a Response object
    '''
    return request('post', uri, data=data, auth=auth)

def delete_from(uri: str, data: dict, auth) -> Response:
    '''
    Builds and executes a DELETE request for a to-many resource relationship.
    Use this if you want to remove a resource to a to-many relationship.

    Args:
        obj: is the Entity instance of the resource with the relationship you want to add to
        attr_obj: is the Entity instance of the resource you want to add
        auth: is a TokenAuth() representing the authentication token

    Returns:
        a Response object
    '''
    return request('delete', uri, data=data, auth=auth)

def add_many_to(obj, attr_objs, auth):
    pass

def delete(uri, auth):
    '''
    Builds and executes a DELETE request for a resource.

    Args:
        obj: is the Entity instance of the resource you want to delete
        auth: is a TokenAuth() representing the authentication token

    Returns:
        a Response object
    '''
    return request('delete', uri, auth=auth)
