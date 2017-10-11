import sys
from benwaonline.database import db
from benwaonline.models import user_datastore, Role, User
from run import app

def me_mod(user_id):
    with app.app_context():
        user = User.query.get(user_id)
        role = Role.query.get(1)
        user_datastore.add_role_to_user(user, role)
        db.session.commit()

if __name__ == '__main__':
    me_mod(sys.argv[1])