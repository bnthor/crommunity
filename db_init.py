from crommunity import db
import os

if bool(os.environ.get('DEBUG', '')):
    db.drop_all()
db.create_all()
