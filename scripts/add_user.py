from benwaonline.database import db
from benwaonline.models import user_datastore, Role, User
from run import app

def add_user():
    with app.app_context():
        username = 'Cosmic Benwa Rutabega'
        user_id = '420'
        user = user_datastore.create_user(user_id=user_id, username=username)
        db.session.commit()



if __name__ == '__main__':
    add_user()