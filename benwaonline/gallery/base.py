import os
import uuid
import json
from urllib import parse

import requests
from marshmallow import pprint

from flask import current_app
from benwaonlineapi import schemas

def create_tag(r, *args, **kwargs):
    if not r.ok:
        o = parse.urlsplit(r.url)
        tagname = parse.unquote(o.path).split('/')[-1]
        payload = schemas.TagSchema().dumps({'id': '420', 'name': tagname}).data
        uri = '/'.join([current_app.config['API_URL'], 'tags'])
        r = requests.post(uri, headers=r.headers, data=payload, timeout=5)

    return r
