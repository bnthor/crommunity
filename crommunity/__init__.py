from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_babel import Babel, format_datetime, format_date, gettext
from jinja2 import Environment as JinjaEnv
from flask_assets import Environment as AssetsEnv, Bundle
from flask_login import LoginManager
from flask_gravatar import Gravatar
from flask_mail import Mail
from flask_misaka import Misaka
from datetime import datetime

# App config
app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py')

# Database
db = SQLAlchemy(app)

# Flask login
login = LoginManager()
login.init_app(app)
login.login_view = 'login'
login.login_message = gettext(u'Please log in to access this page.')
login.login_message_category = "error"

# Assets bundles
assets = AssetsEnv(app)
assets.url = app.static_url_path
js = Bundle('js/highlight.pack.js', 'js/app.js', filters='jsmin', output='bundle.js')
css = Bundle('scss/styles.scss', depends=('scss/**/*.scss'), filters='pyscss', output='bundle.css')
assets.register('js_all', js)
assets.register('css_all', css)

# Babel for i18n
babel = Babel(app)

@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(app.config['LANGUAGES'])

# Jinja
@app.context_processor
def inject_variables():
    return {
        "app_name": app.config['APP_NAME'],
        "now": datetime.utcnow()
    }

jinja_env = JinjaEnv(extensions=['jinja2.ext.i18n'])
app.jinja_env.filters['datetime'] = format_datetime
app.jinja_env.filters['date'] = format_date
app.jinja_env.globals['get_locale'] = get_locale

# Gravatar profile pics
gravatar = Gravatar(app, size=100, rating='g', default='retro', force_default=False)

# Flask mail
mail = Mail(app)

# Markdown support
md = Misaka(fenced_code=1, tables=1, highlight=1, strikethrough=1, wrap=1, footnotes=1)
md.init_app(app)

# Import routes
import crommunity.routes
