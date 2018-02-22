
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
