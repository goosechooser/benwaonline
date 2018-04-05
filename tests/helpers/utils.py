''' Various helper functions for testing '''
from datetime import datetime
import json

def benwa_resp():
    return {
        "access_token": "LnUwYsyKvQgo8dLOeC84y-fsv_F7bzvZ",
        'refresh_token': 'refresh_me_thanks',
        "expires_in": 3600,
        "scope": "openid email",
        "token_type": "Bearer"
    }

def auth_payload():
    return {
        "iss": "https://choosegoose.benwa.com/",
        "sub": "59866964",
        "aud": "1LX50Fa2L80jfr9P31aSZ5tifrnLFGDy",
        "iat": 1511860306,
        "exp": 1511896306
    }

def test_user():
    return {
        'id': '1',
        "active": True,
        "created_on": datetime.utcnow(),
        "user_id": "666",
        "username": "Beautiful Benwa Aficionado"
    }

def error_response(type_, id_):
    return {
        "errors": [
            {
                "detail": {
                    "parameter": "id"
                },
                "source": "{}: {} not found".format(type_, id_),
                "status": "404",
                "title": "Object not found"
            }
        ],
        "jsonapi": {
            "version": "1.0"
        }
    }


def load_test_data(fname):
    base = 'tests/data/'
    with open(base + fname) as f:
        return json.load(f)
