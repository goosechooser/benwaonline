import os
import json
import requests

HEADERS = {
    'Accept': 'application/vnd.api+json',
    'Content-Type': 'application/vnd.api+json'
}

def prepare_params(include=None, filters=None, page_opts=None, fields=None):
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

def get(obj, include=None, page_opts=None, fields=None):
    '''
    Builds and executes a GET request for the collection of a resource

    Args:
        obj: is the Entity of the resource desired
        include: is a list of strings containing the resources you want included
        page_opts: is a dict containing options related to pagination of results
            ex: {'size': 10}
        fields: is a dict that will restrict the fields of the result
            ex: {'<resource_type>': [<list of fields (as strings) to return>]}

    Returns:
        a Response object that can be turned into a list of Entity with the appropiate from_response() method.
    '''
    uri = obj.api_endpoint

    params = prepare_params(include=include, page_opts=page_opts, fields=fields)

    return requests.get(uri, headers=HEADERS, params=params, timeout=5)

def get_instance(obj, include=None, fields=None):
    '''
    Builds and executes a GET request for a single resource.

    Args:
        obj: is the Entity of the resource desired
        include: is a list of strings containing the resources you want included.
        fields: is a dict that will restrict the fields of the result
            ex: {'<resource_type>': [<list of fields (as strings) to return>]}

    Returns:
        a Response object that can be turned into an Entity with the appropiate from_response() method.
    '''
    uri = obj.api_endpoint + '/' + str(obj.id)
    params = prepare_params(include=include, fields=fields)

    return requests.get(uri, headers=HEADERS, params=params, timeout=5)

def get_resource(obj, resource_obj, include=None, page_opts=None):
    '''
    Builds and executes a GET request for a related resource

    Args:
        obj: the Entity instance of the resource that 'has' the resource
        resource_obj: is the Entity of the related resource
        include: is a list of strings containing additional resources you want included
        page_opts: is a dict containing options related to pagination of results
            ex: {'size': 10}

    Returns:
        a Response object that can be turned into an Entity with the appropiate from_response() method.
    '''
    # Currently gets the entire collection if it exists
    # no current need to get a single resource from a collection but
    # it could probably be done easily by passing a resource_obj with an id
    uri = obj.resource_uri(resource_obj)

    params = prepare_params(include=include, page_opts=page_opts)

    return requests.get(uri, headers=HEADERS, params=params, timeout=5)

def post(obj, auth):
    '''
    Builds and executes a POST request for a resource
    Args:
        obj: the Entity instance of the resource
        auth: a TokenAuth() representing the authentication token

    Returns:
        a Response object that can be turned into an Entity with the appropiate from_response() method.
    '''
    include = [v for v in dir(obj) if v and v in obj.relationships]
    params = {'include': ','.join(include)}
    obj.id = 666
    payload = obj.dumps()


    return requests.post(
        obj.api_endpoint,
        data=payload,
        headers=HEADERS,
        params=params,
        timeout=5,
        auth=auth
    )

def filter(obj, query, include, page_opts):
    '''
    Builds and executes a GET request for a collection of resources with a filter appended to the url.

    Args:
        obj: is the Entity of the resource collection desired
        query: a Query object that will be turned into the desired filter
        include: is a list of strings containing the resources you want included.
        page_opts: is a dict containing options related to pagination of results
            ex: {'size': 10}

    Returns:
        a Response object that can be turned into an Entity with the appropiate from_response() method.
    '''
    params = prepare_params(include=include, filters=query.to_filter(), page_opts=page_opts)

    return requests.get(obj.api_endpoint, headers=HEADERS, params=params, timeout=5)

def patch(obj, attr_obj, auth):
    '''
    Builds and executes a PATCH request for a one-to-one resource relationship

    Args:
        obj: the Entity instance of the resource containing the relationship
        attr_obj: is the Entity instance of the resource you want to relate
        auth: is a TokenAuth() representing the authentication token

    Returns:
        a Response object
    '''
    r = requests.patch(
        obj.relationship_uri(attr_obj),
        headers=HEADERS,
        data=attr_obj.dumps(),
        timeout=5,
        auth=auth
    )
    return r

def patch_many(obj, attr_objs, auth):
    '''
    Builds and executes a PATCH request for a one-to-many resource relationship

    Args:
        obj: the Entity instance of the resource containing the relationship
        attr_objs: a list of Entity instances that you want to want to replace the existing relationship with
        auth: is a TokenAuth() representing the authentication token

    Returns:
        a Response object
    '''
    ids = [{'id': str(o.id)} for o in attr_objs]
    data = attr_objs[0].dumps(many=True, data=ids)

    r = requests.patch(
        obj.relationship_uri(attr_objs[0]),
        headers=HEADERS,
        data=data,
        timeout=5,
        auth=auth
    )
    return r

def add_to(obj, attr_obj, auth):
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
    patch = attr_obj.dumps(many=True, data=[attr_obj.__dict__])
    uri = obj.relationship_uri(attr_obj)
    r = requests.post(uri, headers=HEADERS, data=patch, timeout=5, auth=auth)
    return r

def delete_from(obj, attr_obj, auth):
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
    patch = attr_obj.dumps(many=True, data=[attr_obj.__dict__])
    uri = obj.relationship_uri(attr_obj)
    r = requests.delete(uri, headers=HEADERS,
                        data=patch, timeout=5, auth=auth)
    return r

def add_many_to(obj, attr_objs, auth):
    pass

def delete(obj, auth):
    '''
    Builds and executes a DELETE request for a resource.

    Args:
        obj: is the Entity instance of the resource you want to delete
        auth: is a TokenAuth() representing the authentication token

    Returns:
        a Response object
    '''
    r = requests.delete(obj.instance_uri, headers=HEADERS, timeout=5, auth=auth)
    return r
