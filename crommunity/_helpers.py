import imghdr
from crommunity import app, mail
from flask import redirect, url_for, flash
from flask_mail import Message
from threading import Thread
from flask_babel import gettext
from flask_login import current_user
from functools import wraps

# Password validation rules
def validate_password(password):
    pwd_uppercase = any(x.isupper() for x in password)
    pwd_digit = any(x.isdigit() for x in password)
    pwd_length = len(password) >= 8

    if not all([pwd_uppercase, pwd_digit, pwd_length]):
        return False
    else:
        return True

# Send emails asynchronously
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

# Send emails
def send_email(subject, reply_to, sender, recipients, html_body):
    msg = Message()
    msg.subject = subject
    msg.reply_to = reply_to
    msg.sender = sender
    msg.recipients = recipients
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()

# Check if user is admin
def admin_required():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))

            elif not current_user.is_admin():
                flash(gettext("You don't have access to that page"), "danger")
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Check user's access level
def min_role_required(access_level):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))

            elif current_user.role < access_level:
                flash(gettext("You don't have access to that page"), "danger")
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_image(stream):
    header = stream.read(512)  # 512 bytes should be enough for a header check
    stream.seek(0)  # reset stream pointer
    format = imghdr.what(None, header)
    if not format:
        return None
    return '.' + (format if format != 'jpeg' else 'jpg')
