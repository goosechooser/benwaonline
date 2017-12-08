import os

from benwaonline import create_app

app = create_app(os.getenv('FLASK_CONFIG'))
