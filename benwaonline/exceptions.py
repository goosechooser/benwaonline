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