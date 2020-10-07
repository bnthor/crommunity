import os
import jwt
from crommunity import app, db, login
from time import time
from datetime import datetime
from flask_login import UserMixin
from bs4 import BeautifulSoup
from markdown import markdown

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

ROLES = {
    'guest': 0,
    'user': 1,
    'mod': 2,
    'admin': 3
}

class User(db.Model, UserMixin):
    """The User object that owns posts."""
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, nullable=False)
    confirmed = db.Column(db.Boolean, default=False)
    username = db.Column(db.Unicode, nullable=False, unique=True)
    email = db.Column(db.Unicode, nullable=False, unique=True)
    password = db.Column(db.Unicode, nullable=False)
    enabled = db.Column(db.Boolean, default=True)
    token = db.Column(db.Unicode)
    role = db.Column(db.SmallInteger, nullable=False, default=1)
    posts = db.relationship('Post', backref='author', lazy=True)
    votes = db.relationship('Vote', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)
    reports = db.relationship('Report', backref='author', lazy=True)

    def __init__(self, *args, **kwargs):
        """On construction, set date of creation."""
        super().__init__(*args, **kwargs)
        self.created = datetime.now()

    def is_admin(self):
        return self.role == ROLES['admin']

    def is_mod(self):
        return self.role == ROLES['mod']

    def allowed(self, access_level):
        return self.role >= access_level

    def get_reset_token(self, expires=500):
        payload = {
            'reset_password': self.username,
            'exp': int(time()) + expires
        }
        return jwt.encode(
            payload,
            key=app.config['SECRET_KEY'],
            algorithm='HS256'
        )
    @staticmethod
    def verify_reset_token(token):
        try:
            username = jwt.decode(token, key=app.config['SECRET_KEY'])['reset_password']
        except Exception as e:
            print(e)
            return
        return User.query.filter_by(username=username).first()

class Post(db.Model):
    """User's posts."""
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, nullable=False)
    title = db.Column(db.Unicode, nullable=False)
    picture = db.Column(db.Unicode)
    link = db.Column(db.Unicode)
    content = db.Column(db.Unicode)
    excerpt = db.Column(db.Unicode)
    vote_count = db.Column(db.Integer, default=0)
    comment_count = db.Column(db.Integer, default=0)
    reports = db.Column(db.SmallInteger)
    enabled = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    votes = db.relationship('Vote', backref='post', lazy=True)
    comments = db.relationship('Comment', backref='post', lazy=True)
    reports = db.relationship('Report', backref='post', lazy=True)

    def __init__(self, *args, **kwargs):
        """On construction, set date of creation."""
        super().__init__(*args, **kwargs)
        self.created = datetime.now()
        if self.content:
            html = markdown(self.content)
            text = ''.join(BeautifulSoup(html, features="html.parser").findAll(text=True))
            self.excerpt = text[:140] + (text[140:] and '...')

class Vote(db.Model):
    """Votes on post, upvotes when type = True"""
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, nullable=False)
    type = db.Column(db.Boolean, nullable=False, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

    def __init__(self, *args, **kwargs):
        """On construction, set date of creation."""
        super().__init__(*args, **kwargs)
        self.created = datetime.now()

class Comment(db.Model):
    """Post comments"""
    id = db.Column(db.Integer, primary_key=True)
    parent = db.Column(db.Integer)  # used when replying to a comment
    created = db.Column(db.DateTime, nullable=False)
    content = db.Column(db.Unicode, nullable=False)
    enabled = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

    def __init__(self, *args, **kwargs):
        """On construction, set date of creation."""
        super().__init__(*args, **kwargs)
        self.created = datetime.now()

class Report(db.Model):
    """Votes on post, upvotes when type = True"""
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

    def __init__(self, *args, **kwargs):
        """On construction, set date of creation."""
        super().__init__(*args, **kwargs)
        self.created = datetime.now()
