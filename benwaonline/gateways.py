import os
import json
import requests
from benwaonline.config import app_config

API_ENDPOINT = app_config[os.getenv('FLASK_CONFIG')].API_URL
HEADERS = {
    'Accept': 'application/vnd.api+json',
    'Content-Type': 'application/vnd.api+json'
}
class RequestFactory(object):
    def get(self, obj, _id=None, sort_by=None, include=None):
        '''
        Builds and executes a GET request for a single resource or the collection of them.

        Args:
            obj: is the Entity of the resource desired
            _id: is the id of the resource you want to get, otherwise returns a collection.
            include: is a list of strings containing the resources you want included.

        Returns:
            a Response object that can be turned into an Entity with the appropiate from_response() method.
        '''
        # could split this out into 2-3 different methods actually
        # get, get_collection, get_by_[attr] etc?
        # or could pass the id of the obj you want in obj and remove it from method header
        if _id:
            uri = '/'.join([obj.api_endpoint, str(_id)])
        else:
            uri = obj.api_endpoint

        params = {}
        if sort_by:
            params['sort'] = ','.join(sort_by)

        if include:
            params['include'] = ','.join(include)

        return requests.get(uri, headers=HEADERS, params=params, timeout=5)

    def get_resource(self, obj, resource_obj, include=None):
        '''
        Builds and executes a GET request for a related resource

        Args:
            obj: the Entity instance of the resource that 'has' the resource
            resource_obj: is the Entity of the related resource
            include: is a list of strings containing additional resources you want included

        Returns:
            a Response object that can be turned into an Entity with the appropiate from_response() method.
        '''
        # Currently gets the entire collection if it exists
        # no current need to get a single resource from a collection but
        # it could probably be done easily by passing a resource_obj with an id
        uri = obj.resource_uri(resource_obj)

        try:
            params = {'include': ','.join(include)}
        except TypeError:
            params = {}

        return requests.get(uri, headers=HEADERS, params=params, timeout=5)


    @staticmethod
    def post(obj, auth, include=None):
        '''
        Builds and executes a POST request for a resource
        Args:
            obj: the Entity instance of the resource
            auth: a TokenAuth() representing the authentication token

        Returns:
            a Response object that can be turned into an Entity with the appropiate from_response() method.
        '''
        params = {}
        if include:
            params['include'] = ','.join(include)

        payload = obj.dumps()
        return requests.post(
            obj.api_endpoint,
            data=payload,
            headers=HEADERS,
            params=params,
            timeout=5,
            auth=auth
        )

    def filter(self, obj, filters, single=False, include=None):
        '''
        Builds and executes a GET request for a collection of resources with a filter appended to the url.

        Args:
            obj: is the Entity of the resource collection desired
            filters: the filters to append to the url
            single: if True, returns a single resource or a 404 if the resource doesn't exist OR if more than 1 object exists
            include: is a list of strings containing the resources you want included.

        Returns:
            a Response object that can be turned into an Entity with the appropiate from_response() method.
        '''
        # Since all this does is add entries to params
        # could just pass in a request object and modify it
        # this would require splitting the request builder and the request executor into seperate parts
        # could do the same with include tbh
        # params = {'filter[{}]'.format(k): v
        #         for (k, v) in filters.items()}

        params = {'filter': json.dumps(filters)}

        if include:
            params['include'] = ','.join(include)

        if single:
            params['filter[single]'] = 1

        r = requests.get(obj.api_endpoint, headers=HEADERS, params=params, timeout=5)
        return r

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def add_many_to(obj, attr_objs, auth):
        pass

    @staticmethod
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
