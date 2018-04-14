''' Various helper functions for testing '''
from datetime import datetime
import json

def errors(errors_):
    error_entries = [error.__dict__ for error in errors_]
    return {
        "errors": error_entries,
        "jsonapi": {
            "version": "1.0"
        }
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
