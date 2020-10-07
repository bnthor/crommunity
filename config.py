#!/usr/bin/env python3
APP_NAME = 'Crommunity'

DEBUG = False
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = False

BABEL_DEFAULT_LOCALE = 'en'
LANGUAGES = ['en', 'fr']

POSTS_PER_PAGE = 10

OWNER_NAME = "John Doe"
OWNER_EMAIL = "bnrtro@gmail.com"
OWNER_ADDRESS = "1 main street, New Amsterdam, NY"

HOST_NAME = "OhMyHost"
HOST_ADDRESS = "43 second street, New York, NY"

# File uploads
UPLOAD_FOLDER = 'crommunity/uploads'
UPLOAD_EXTENSIONS = ['.jpg', '.png', '.gif']
MAX_CONTENT_LENGTH = 16 * 1024 * 1024