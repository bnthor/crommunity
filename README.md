# Crommunity

Crommunity is a minimal Flask micro community starter kit (like subreddits). There's no third party library, no analytics. Crommunity is aimed at people who want to create simple and positive communities, no thumbs down allowed.

Post pictures, markdown enabled content, comment and upvote. Adminitration and moderation are built-in.

![preview](https://image.noelshack.com/fichiers/2020/43/3/1603293184-crommunity.png)

## Requirements

- `brew install pipenv` (optional)
- `brew install postgresql`
- clone this project and `cd` to it
- if on **macOs**:
  - ensure Xcode is up to date and additional packages are installed 
  - `brew install openssl`
  - add its path to LIBRARY_PATH: `export LIBRARY_PATH=$LIBRARY_PATH:/usr/local/opt/openssl/lib/`
  - `pipenv install psycopg2`
- `pipenv shell` to enable a virtual environment
- `pipenv install` to install all dependencies

## Instance configuration

Create an `instance/config.py` file at the root, in which you must paste and edit the following lines. It's very important as the secret key is used when hashing passwords, and the `MAIL` settings are used when recovering passwords and all email communications.

```
#!/usr/bin/env python3
DEBUG = True

SECRET_KEY = '<YOUR_SECRET_KEY>'

SQLALCHEMY_ECHO = False
SQLALCHEMY_DATABASE_URI = '<DATABASE_URL>'

MAIL_SERVER = '<MAIL_SENDING_SERVER>'
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_USERNAME = "<YOUR_EMAIL>"
MAIL_PASSWORD = "<YOUR_PASSWORD>"
```

### Generating a secret key

Launch a python REPL (`python3`) and these two commands

```
import secrets
secrets.token_urlsafe(16)
```

Paste the result in `./instance/config.py` (*SECRET_KEY*).

### Database creation

#### With SQLite

In `./instance/config.py`, *DATABASE_URL* should be `'sqlite:///../my_database.db'` (at the root)

> The [sqlite browser](https://sqlitebrowser.org) app is useful to browse and edit a SQLite database.

#### With PostgreSQL

You should install postgreSQL for your OS first. Then *DATABASE_URL* should be, for example, `postgresql://username:password@localhost:5432/db_name`

#### Initializing the DB

Now you can create the project's tables by launching `python3 db_init.py` at the root. Models are defined in `crommunity/models.py`.

## Launching the dev server

First, enable the virtual env with `pipenv shell`, then use `pipenv run flask run`.

## Exiting the dev server and pipenv:

Hit `CTRL + C` to stop flask, then `exit` to exit the virtual environment.

## Freezing packages versions

`pipenv run pip freeze > requirements.txt`

## I18n

Crommunity supports the languages listed in `./config.py`, whenever you add some new translation strings, you should:

- `pipenv run  flask translate update` to update translation files for all languages.
- `pipenv run  flask translate compile` to compile translation files for all languages.

To initialize a new language, update `LANGUAGES` in `./config.py` and use:

- `pipenv run  flask translate init <language-code>` (e.g. `... init es` for spanish).

### Translating with the right tools

Editing `.po` files in a regular editor can be a pain, take a look at [poEdit](https://poedit.net).

## Customization

First, you need to edit `./config.py`, here you can set your default language (for now, English and French are supported), and the administrator's credentials.

Crommunity ships with default "privacy-policy" and "about-us" pages which should be enough for most projects. These pages are in english by default and it's **entirely up to you** to make these compliant to GDPR and area specific legislation.

### Theming

Templates are found in `./crommunity/templates`, using the Jinja engine.

Styles are found in `./crommunity/static/scss`, the basic theme is as minimal as possile and should be easy to extend.

Javascript files are in `./crommunity/static/js`, there is as few scripts and dependencies as possible. The only lib there is _highlight.js_ that handles syntax highlighting in markdown posts.

## Tracking and cookie policy

By default, crommunity only uses two cookies: the privacy consent cookie, and the session cookie. **No third party cookie**! One can share posts on social platforms but with plain html links, no GAFA lib is included. 

There's no tracking either, of course, it's entirely up to you to extend crommunity with ads and analytics... But I wouldn't!

## Roadmap

### V2 features

- Private messaging
- Nested comments (use the parent row in comments model)
- Cleanup routes.py with [blueprints](https://flask.palletsprojects.com/en/1.1.x/blueprints)
- Built-in avatar upload instead of unsing gravatar's
- Add posts tags
- Add social html tags to improve posts sharing