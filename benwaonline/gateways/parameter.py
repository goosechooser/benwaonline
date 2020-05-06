import json

class Parameter(object):
    '''
    Container for a variety of parameters related to FLASK-REST-JSONAPI/requests.

    Args:
        include: is a list of strings containing the resources you want included
        filters: is a list of dicts forming the filter query (see query.py)
        page_size: is an str related to how many results to return
        page_number: is the number of the paginated results to get
        fields[name_of_resource]: is a list containing the fields to return /only/
        sort: list of strings that describes how the results are to be sorted
        
    '''
    def __init__(self, include=None, filters=None, page_size=None, page_number=None, fields=None, sort=None):
        self._params = {
            'include': include,
            'filter': filters,
            'page_size': page_size,
            'page_number': page_number,
            'fields': fields,
            'sort': sort
        }

    def dump(self):
        dumping = {
            'include': ','.join(self.include) if self.include else None,
            'sort': ','.join(self.sort) if self.sort else None,
            'filter': json.dumps(self.filter) if self.filter else None,
            'page[size]': self.page_size,
            'page[number]': self.page_number,
        }

        if self.fields:
            f = {'fields[{}]'.format(k): ','.join(v) for k,v in self.fields.items()}
            dumping.update(f)

        return dumping

    def __getattr__(self, name):
        if name in self._params:
            return self._params[name]
        else:
            raise AttributeError(name)

    def __setattr(self, name, value):
        if name in self._params:
            self._params[name] = value
        else:
            raise AttributeError(name)

    @property
    def params(self):
        return self._params
