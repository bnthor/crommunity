# Crommunity

## Requirements

- `brew install pipenv` (optional)
- clone this project and `cd` to it
- `pipenv shell` to enable a virtual environment
- `pipenv install` to install all dependencies

## Instance configuration

Create an `instance/config.py` file at the root, in which you must paste and edit these lines:

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
