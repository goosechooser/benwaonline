import datetime
import json

post = {
    'preview': '1', 'id': 1,
    'comments': [
        {'id': '1', 'post': '1', 'created_on': datetime.datetime(2017, 12, 6, 6, 1, 38), 'content': 'heloo!', 'user': '1'}
    ],
    'tags': [
        {'id': '1', 'posts': ['1', '2'], 'created_on': datetime.datetime(2017, 11, 30, 6, 44, 22), 'name': 'benwa'},
        {'id': '2', 'posts': ['1'], 'created_on': datetime.datetime(2017, 12, 5, 2, 3, 7), 'name': 'rufus'},
        {'id': '3', 'posts': ['1'], 'created_on': datetime.datetime(2017, 12, 5, 2, 3, 7), 'name': 'not benwa'}
    ],
    'created_on': datetime.datetime(2017, 12, 5, 2, 3, 7),
    'title': 'test',
    'image': {'id': '1', 'filepath': 'imgs/c81e24ede61e48bb878844dcf6521f8a.png'},
    'user': '1'
}

posts = {'data': [{'attributes': {'created_on': '2017-12-07T04:51:02',
                          'title': 'akuma_spagh'},
           'id': '1',
           'links': {'self': 'http://127.0.0.1:5001/api/posts/1'},
           'relationships': {'comments': {'data': [],
                                          'links': {'related': '/api/posts/1/comments',
                                                    'self': '/api/posts/1/relationships/comments'}},
                             'image': {'data': {'id': '1', 'type': 'images'},
                                       'links': {'related': '/api/posts/1/image',
                                                 'self': '/api/posts/1/relationships/image'}},
                             'preview': {'data': {'id': '1',
                                                  'type': 'previews'},
                                         'links': {'related': '/api/posts/1/preview',
                                                   'self': '/api/posts/1/relationships/preview'}},
                             'tags': {'data': [{'id': '1', 'type': 'tags'}],
                                      'links': {'related': '/api/posts/1/tags',
                                                'self': '/api/posts/1/relationships/tags'}},
                             'user': {'data': {'id': '1', 'type': 'users'},
                                      'links': {'related': '/api/posts/1/user',
                                                'self': '/api/posts/1/relationships/user'}}},
           'type': 'posts'},
          {'attributes': {'created_on': '2017-12-07T05:33:38', 'title': 'ayy'},
           'id': '2',
           'links': {'self': 'http://127.0.0.1:5001/api/posts/2'},
           'relationships': {'comments': {'data': [{'id': '1',
                                                    'type': 'comments'}],
                                          'links': {'related': '/api/posts/2/comments',
                                                    'self': '/api/posts/2/relationships/comments'}},
                             'image': {'data': {'id': '2', 'type': 'images'},
                                       'links': {'related': '/api/posts/2/image',
                                                 'self': '/api/posts/2/relationships/image'}},
                             'preview': {'data': {'id': '2',
                                                  'type': 'previews'},
                                         'links': {'related': '/api/posts/2/preview',
                                                   'self': '/api/posts/2/relationships/preview'}},
                             'tags': {'data': [{'id': '1', 'type': 'tags'}],
                                      'links': {'related': '/api/posts/2/tags',
                                                'self': '/api/posts/2/relationships/tags'}},
                             'user': {'data': {'id': '1', 'type': 'users'},
                                      'links': {'related': '/api/posts/2/user',
                                                'self': '/api/posts/2/relationships/user'}}},
           'type': 'posts'}],
 'included': [{'attributes': {'created_on': '2017-12-07T04:51:02',
                              'filepath': 'thumbs/893a9b6467c843b19ba0f8fbbb83b24d.png'},
               'id': '1',
               'links': {'self': 'http://127.0.0.1:5001/api/previews/1'},
               'relationships': {'post': {'data': {'id': '1', 'type': 'posts'},
                                          'links': {'related': '/api/previews/1/post',
                                                    'self': '/api/previews/1/relationships/post'}}},
               'type': 'previews'},
              {'attributes': {'created_on': '2017-12-07T05:33:38',
                              'filepath': 'thumbs/cf777c4ab8314ab8a29ee129e0a7ae78.png'},
               'id': '2',
               'links': {'self': 'http://127.0.0.1:5001/api/previews/2'},
               'relationships': {'post': {'data': {'id': '2', 'type': 'posts'},
                                          'links': {'related': '/api/previews/2/post',
                                                    'self': '/api/previews/2/relationships/post'}}},
               'type': 'previews'}],
 'jsonapi': {'version': '1.0'},
 'links': {'first': 'http://127.0.0.1:5001/api/posts?page%5Bsize%5D=10&include=preview&page%5Bnumber%5D=1',
           'last': 'http://127.0.0.1:5001/api/posts?page%5Bsize%5D=10&include=preview&page%5Bnumber%5D=1',
           'next': None,
           'prev': None,
           'self': '/api/posts'},
 'meta': {'total': 2}}

def datetime_handler(x):
    if isinstance(x, datetime.datetime):
        return x.isoformat()
    raise TypeError("Unknown type")

def test_write_out():
    with open('tests\\data\\postclient_get_single.json', 'w') as f:
        json.dump(post, f, default=datetime_handler)