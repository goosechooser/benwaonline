from flask import json, current_app, request

#: The Content-Type we expect for most requests to APIs.
#:
#: The JSON API specification requires the content type to be
#: ``application/vnd.api+json``.
JSONAPI_MIMETYPE = 'application/vnd.api+json'

#: The Content-Type for Javascript data.
#:
#: This is used, for example, in JSONP responses.
JAVASCRIPT_MIMETYPE = 'application/javascript'

#: The highest version of the JSON API specification supported by
#: Flask-Restless.
JSONAPI_VERSION = '1.0'

class BenwaOnlineException(Exception):
    '''
    Based off flask-restless's ProcessingException
    '''
    def __init__(self, id_=None, links=None, status=500, code=None, title=None,
                 detail=None, source=None, meta=None, *args, **kw):
        self.id_ = id_
        self.links = links
        self.status = status
        self.code_ = code
        self.code = status
        self.title = title
        self.detail = detail
        self.source = source
        self.meta = meta

class BenwaOnlineRequestException(BenwaOnlineException):
    ''' Requests error '''

def jsonpify(data):
    """Creates a HTTP response containing JSON or JSONP data.
    `data` is a dictionary representing a JSON object.
    If the incoming HTTP request has no query parameter ``callback``,
    then the body of the response will be a JSON document and the
    :http:header:`Content-Type` will be ``application/vnd.api+json``,
    the JSON API mimetype. If the request has a query parameter
    ``callback=foo``, then the body of the response will be
    ``foo(<json>)``, where ``<json>`` is the JSON object that would have
    been returned, and the :http:header:`Content-Type` will be
    ``application/javascript``.
    """
    document = json.dumps(data)
    mimetype = JSONAPI_MIMETYPE
    callback = request.args.get('callback', False)
    if callback:
        document = '{0}({1})'.format(callback, document)
        mimetype = JAVASCRIPT_MIMETYPE
    response = current_app.response_class(document, mimetype=mimetype)
    return response

'''
Taken from https://github.com/jfinkels/flask-restless/blob/master/flask_restless/views/base.py
'''

def error_response(status=400, cause=None, **kw):
    """Returns a correctly formatted error response with the specified
    parameters.
    This is a convenience function for::
        errors_response(status, [error(**kw)])
    For more information, see :func:`errors_response`.
    """
    if cause is not None:
        current_app.logger.exception(str(cause))
    kw['status'] = status
    return errors_response(status, [error(**kw)])


def errors_response(status, errors):
    """Return an error response with multiple errors.
    `status` is an integer representing an HTTP status code corresponding to an
    error response.
    `errors` is a list of error dictionaries, each of which must satisfy the
    requirements of the JSON API specification.
    This function returns a two-tuple whose left element is a dictionary
    representing a JSON API response document and whose right element is
    simply `status`.
    The keys within each error object are described in the `Errors`_
    section of the JSON API specification.
    .. _Errors: http://jsonapi.org/format/#errors
    """
    # TODO Use an error serializer.
    document = {'errors': errors, 'jsonapi': {'version': JSONAPI_VERSION}}
    return jsonpify(document), status


def error(id_=None, links=None, status=None, code=None, title=None,
          detail=None, source=None, meta=None):
    """Returns a dictionary representation of an error as described in the
    JSON API specification.
    Note: the ``id_`` keyword argument corresponds to the ``id`` element
    of the JSON API error object.
    For more information, see the `Errors`_ section of the JSON API
    specification.
    .. Errors_: http://jsonapi.org/format/#errors
    """
    # HACK We use locals() so we don't have to list every keyword argument.
    if all(kwvalue is None for kwvalue in locals().values()):
        raise ValueError('At least one of the arguments must not be None.')
    return {'id': id_, 'links': links, 'status': status, 'code': code,
            'title': title, 'detail': detail, 'source': source, 'meta': meta}
