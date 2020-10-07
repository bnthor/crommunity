import os
from datetime import datetime
from flask import render_template, redirect, request, session, jsonify, flash, url_for, jsonify, send_from_directory
from crommunity import app, db
from sqlalchemy import or_
from sqlalchemy.sql.expression import func
from ._helpers import validate_password, send_email, admin_required, min_role_required, validate_image
from .models import User, Post, Comment, Vote, Report, ROLES
from werkzeug.urls import url_parse
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
from flask_babel import gettext
from flask_login import current_user, login_user, logout_user, login_required
from email_validator import validate_email, EmailNotValidError

# --------------
# API ROUTES
# --------------
@app.route('/api/test')
def api_test():
    output = {'msg': 'registered'}
    return jsonify(output)


# ------------
# ERROR ROUTES
# ------------
@app.errorhandler(400)
def bad_request(e):
    return render_template('_errors.html', code=400), 400

@app.errorhandler(401)
def unauthorized(e):
    return render_template('_errors.html', code=401), 401

@app.errorhandler(403)
def forbidden(e):
    return render_template('_errors.html', code=403), 403

@app.errorhandler(404)
def page_not_found(e):
    return render_template('_errors.html', code=404), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('_errors.html', code=500), 500


# --------------
# REGULAR ROUTES
# --------------
@app.route('/')
def index():
    user_count = User.query.count()
    page = request.args.get('page', 1, type=int)
    posts = Post.query\
            .filter(Post.enabled==True)\
            .order_by(Post.created.desc())\
            .paginate(page, app.config['POSTS_PER_PAGE'], False)

    next_url = url_for('index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) if posts.has_prev else None

    posts = False if posts.total == 0 else posts.items

    return render_template(
        "index.html",
        sort='recent',
        user_count=user_count,
        posts=posts,
        next_url=next_url,
        prev_url=prev_url
    )

@app.route('/top')
def top_posts():
    user_count = User.query.count()
    page = request.args.get('page', 1, type=int)
    posts = Post.query\
            .filter(Post.enabled==True)\
            .order_by(Post.vote_count.desc())\
            .paginate(page, app.config['POSTS_PER_PAGE'], False)

    next_url = url_for('top_posts', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('top_posts', page=posts.prev_num) if posts.has_prev else None

    posts = False if posts.total == 0 else posts.items

    return render_template(
        "index.html",
        sort='top',
        user_count=user_count,
        posts=posts,
        next_url=next_url,
        prev_url=prev_url
    )

@app.route('/random')
def random_posts():
    user_count = User.query.count()
    posts = Post.query\
            .filter(Post.enabled==True)\
            .order_by(func.random())\
            .paginate(1, app.config['POSTS_PER_PAGE'], False)

    # order_by(func.random()) # for PostgreSQL, SQLite
    # order_by(func.rand()) # for MySQL
    # order_by('dbms_random.value') # For Oracle

    posts = False if posts.total == 0 else posts.items

    return render_template(
        "index.html",
        sort='random',
        user_count=user_count,
        posts=posts
    )

@app.route('/search', methods=['POST'])
def search():
    query = request.form["query"]
    search = "%{}%".format(query)
    posts = Post.query.filter(
            or_(
                Post.title.like(search),
                Post.content.like(search)
            )).all()

    return render_template("search.html", posts=posts)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    # User submitted registration form
    if request.method == "POST":

        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        trap = request.form.get("trp")

        # Email validation
        try:
            valid = validate_email(email)
            email = valid.email
        except EmailNotValidError:
            flash(gettext("Email is invalid"), "danger")
            return redirect(url_for('register'))

        if trap:
            flash(gettext("Humans only!"), "danger")
            return redirect(url_for('register'))

        if not username:
            flash(gettext("Username is required"), "danger")
            return redirect(url_for('register'))

        user_exists = bool(User.query.filter_by(username=username).first())

        if user_exists:
            flash(gettext("Username is already taken"), "danger")
            return redirect(url_for('register'))

        email_exists = bool(User.query.filter_by(email=email).first())

        if email_exists:
            flash(gettext("Email is already taken"), "danger")
            return redirect(url_for('register'))

        if not password:
            flash(gettext("Password is required"), "danger")
            return redirect(url_for('register'))

        if not password == confirmation:
            flash(gettext("Passwords did not match"), "danger")
            return redirect(url_for('register'))

        # Password validation
        valid_password = validate_password(password)
        if not valid_password:
            flash(gettext("Password must contain an uppercase letter, a digit and at least 8 characters."), "danger")
            return redirect(url_for('register'))

        new_user = User(
            username = username,
            email = email,
            password = generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()

        # Flash the registration success and redirect to login
        flash(gettext("Successfully Registered"), "success")
        return redirect(url_for('login'))

    else:  # GET
        return render_template("register.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        # Forget any user_id

        email = request.form.get("email")
        password = request.form.get("password")
        remember = request.form.get("remember")
        next_page = request.form.get("next")

        if not email:
            flash(gettext("Email is required"), "danger")
            return redirect(url_for('login'))

        if not password:
            flash(gettext("Password is required"), "danger")
            return redirect(url_for('login'))

        user = User.query.filter_by(email=email).first()

        if not user:
            flash(gettext("User was not found"), "danger")
            return redirect(url_for('login'))

        if not check_password_hash(user.password, password):
            flash(gettext("Wrong password"), "danger")
            return redirect(url_for('login'))

        if not user.enabled:
            flash(gettext("Your account has been suspended"), "danger")
            return redirect(url_for('login'))

        # If all went well
        login_user(user, remember=remember)

        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)

    else:  # GET
        return render_template("login.html")

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/forgotten-password", methods=['GET', 'POST'])
def forgotten_password():
    if request.method == 'POST':

        user = User.query.filter_by(email=request.form.get("email")).first()
        user_exists = bool(user)

        if not user_exists:
            flash(gettext("Email doesn't exist"), "danger")
            return redirect(url_for('forgotten_password'))

        token = user.get_reset_token()
        user.token = token

        send_email(app.config['APP_NAME'] + " - " + gettext("Password reset"),
           sender = app.config['MAIL_USERNAME'],
           recipients = [user.email],
           reply_to = None,
           html_body = render_template('emails/reset_email.html', user=user, token=token))

        return render_template("link_sent.html")

    else:  # GET
        return render_template("forgotten_password.html")

@app.route("/new-password/<token>", methods=['GET', 'POST'])
def new_password(token):

    user = User.verify_reset_token(token)

    if not user:
        flash(gettext("Link has expired"), "danger")
        return redirect(url_for('login'))

    password = request.form.get('password')

    if password:
        valid_password = validate_password(password)

        if not valid_password:
            flash(gettext("Password must contain an uppercase letter, a digit and at least 8 characters."), "danger")
            return redirect(url_for('new_password', token=token))

        # Update user's password
        user.password = generate_password_hash(password)
        db.session.commit()

        flash(gettext("Successfully updated password"), "success")
        return redirect(url_for('login'))

    return render_template('new_password.html')

@app.route("/account")
@login_required
def account():
    return render_template("account.html", user=current_user)

@app.route("/update-account", methods=['POST'])
@login_required
def update_account():
    username = request.form.get("username")
    email = request.form.get("email")
    old_password = request.form.get("old_password")
    new_password = request.form.get("new_password")
    confirm_password = request.form.get("confirm_password")

    if username and username != current_user.username:
        user_exists = bool(User.query.filter_by(username=username).first())

        if user_exists:
            flash(gettext("Username is already taken"), "danger")
            return redirect(url_for('account'))

        current_user.username = username
        db.session.commit()

    if email and email != current_user.email:
        email_exists = bool(User.query.filter_by(email=email).first())

        if email_exists:
            flash(gettext("Email is already taken"), "danger")
            return redirect(url_for('account'))

        current_user.email = email
        db.session.commit()

    if old_password and new_password and confirm_password:

        if not check_password_hash(current_user.password, old_password):
            flash(gettext("Wrong password"), "danger")
            return redirect(url_for('account'))

        valid_password = validate_password(new_password)

        if not valid_password:
            flash(gettext("Password must contain an uppercase letter, a digit and at least 8 characters."), "danger")
            return redirect(url_for('account'))

        if not new_password == confirm_password:
            flash(gettext("Passwords did not match"), "danger")
            return redirect(url_for('account'))

        # Update user's password
        current_user.password = generate_password_hash(new_password)
        db.session.commit()

    flash(gettext("Successfully updated your account"), "success")
    return redirect(url_for('account'))

@app.route("/delete-account/<id>")
@login_required
def delete_account(id):

    if int(current_user.id) == int(id):
        logout_user()
        user = User.query.filter_by(id=id).first()

        # Delete all user's activity
        db.session.query(Post).filter_by(user_id=id).delete()
        db.session.query(Vote).filter_by(user_id=id).delete()
        db.session.query(Comment).filter_by(user_id=id).delete()
        db.session.query(Report).filter_by(user_id=id).delete()

        # Finaly delete user and commit changes
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for('index'))

    else:
        flash(gettext("Couldn't delete your account, please try again."), "danger")
        return redirect(url_for('account'))

@app.route("/profile")
@login_required
def profile():
    return 'profile'

@app.route("/about-us")
def about_us():
    website = app.config['APP_NAME']
    owner = {
        "name": app.config['OWNER_NAME'],
        "email": app.config['OWNER_EMAIL'],
        "address": app.config['OWNER_ADDRESS']
    }
    host = {
        "name": app.config['HOST_NAME'],
        "address": app.config['HOST_ADDRESS']
    }
    return render_template("about.html", website=website, owner=owner, host=host)

@app.route("/privacy-policy")
def privacy_policy():
    website = app.config['APP_NAME']
    owner = {
        "name": app.config['OWNER_NAME'],
        "email": app.config['OWNER_EMAIL'],
        "address": app.config['OWNER_ADDRESS']
    }
    host = {
        "name": app.config['HOST_NAME'],
        "address": app.config['HOST_ADDRESS']
    }
    return render_template("privacy_policy.html", website=website, owner=owner, host=host)

@app.route("/privacy-consent", methods = ['POST'])
def privacy_consent():
    resp = app.make_response("Setting consent cookie")
    resp.set_cookie("privacy_consent", "ok")
    return resp

@app.route("/admin")
@min_role_required(ROLES["mod"])
def admin():
    return render_template("admin/dashboard.html")

@app.route("/admin/users")
@min_role_required(ROLES["mod"])
def admin_users():
    user_count = User.query.count()
    users = User.query.all()

    return render_template("admin/users.html", user_count=user_count, users=users, roles=ROLES)

@app.route("/admin/reports")
@min_role_required(ROLES["mod"])
def admin_reported_posts():
    reported_posts = Post.query.filter_by(enabled=False).all()

    return render_template("admin/reported_posts.html", reports=reported_posts)

@app.route("/admin/comments")
@min_role_required(ROLES["mod"])
def admin_reported_comments():
    reported_comments = Comment.query.filter_by(enabled=False).all()

    return render_template("admin/reported_comments.html", reports=reported_comments)

@app.route("/post", methods=['GET', 'POST'])
@login_required
def new_post():
    if request.method == 'POST':

        title = request.form.get("title")
        picture = request.files["picture"]
        link = request.form.get("link")
        content = request.form.get("content")

        if not title:
            flash(gettext("Title is required"), "danger")
            return redirect(url_for('new_post'))

        if not link and not content:
            flash(gettext("Posts should contain a least a link or some content"), "danger")
            return redirect(url_for('new_post'))

        filename = secure_filename(picture.filename)
        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS'] or \
                    file_ext != validate_image(picture.stream):
                flash(gettext("Invalid image format"), "danger")
            filename = str(datetime.now()).replace(":", "-") + file_ext
            picture.save(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename))

        post = Post(
            title = title,
            picture = filename,
            link = link,
            content = content,
            user_id = current_user.id
        )
        db.session.add(post)
        db.session.commit()

        # Flash the creation success
        flash(gettext("Post successfully created"), "success")
        return redirect(url_for('index'))

    else:  # GET
        return render_template("new_post.html")

@app.route('/post/<id>', methods=['GET', 'POST'])
def post(id):

    if request.method == 'POST':
        post = Post.query.filter_by(id=id).first()

        title = request.form.get("title")
        picture = request.files["picture"]
        link = request.form.get("link")
        content = request.form.get("content")

        if not current_user.id == post.user_id:
            flash(gettext("You're not the author of this post!"), "danger")
            return redirect(url_for('index'))

        if not title:
            flash(gettext("Title is required"), "danger")
            return redirect(url_for('edit_post', id=id))

        if not link and not content:
            flash(gettext("Posts should contain a least a link or some content"), "danger")
            return redirect(url_for('edit_post', id=id))

        filename = secure_filename(picture.filename)

        # If filename is empty or different from the existing one
        if filename != '' and filename != post.picture:
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS'] or \
                    file_ext != validate_image(picture.stream):
                flash(gettext("Invalid image format"), "danger")
            filename = str(datetime.now()).replace(":", "-") + file_ext
            picture.save(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename))

        # Else, delete the existing picture
        if (filename == '' or filename != post.picture) and post.picture:
            os.remove(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], post.picture))

        post.title = title
        post.picture = filename
        post.link = link
        post.content = content
        db.session.commit()

        # Flash the update success
        flash(gettext("Post successfully updated"), "success")
        return redirect(url_for('index'))

    else:  # GET
        post = Post.query.filter_by(id=id).first()

        if not post.enabled:
            flash(gettext("This post is disabled"), "danger")
            return redirect(url_for('index'))

        user_count = User.query.count()

        comments = Comment.query.filter_by(post_id=id, enabled=True).all()

        return render_template("view_post.html", post=post, user_count=user_count, comments=comments)

@app.route('/edit-post/<id>')
@login_required
def edit_post(id):
    post = Post.query.filter_by(id=id).first()

    if not current_user.id == post.user_id:
        flash(gettext("You're not the author of this post!"), "danger")
        return redirect(url_for('index'))

    return render_template('edit_post.html', post=post)

@app.route('/delete-post/<id>', methods=['GET', 'POST'])
@login_required
def delete_post(id):
    post = Post.query.filter_by(id=id).first()

    if request.method == 'POST':

        if not current_user.id == post.user_id and not current_user.is_admin():
            flash(gettext("You're not the author of this post!"), "danger")
            return redirect(url_for('index'))

        # Delete post picture
        if post.picture:
            os.remove(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], post.picture))

        # Delete all post activity
        db.session.query(Vote).filter_by(post_id=id).delete()
        db.session.query(Comment).filter_by(post_id=id).delete()
        db.session.query(Report).filter_by(post_id=id).delete()

        # Now delete post
        db.session.delete(post)
        db.session.commit()

        # Flash the deletion success
        flash(gettext("Post successfully deleted"), "success")
        return redirect(url_for('index'))

    else:  # GET
        return render_template('delete_post.html', post_id=post.id)

@app.route('/upvote-post/<id>')
@login_required
def upvote_post(id):
    userid = current_user.id
    post = Post.query.filter_by(id=id).first()
    vote = Vote.query.filter_by(post_id=post.id, user_id=userid).first()

    if not vote:
        new_vote = Vote(
            user_id = userid,
            post_id = post.id
        )
        db.session.add(new_vote)
        post.vote_count = post.vote_count + 1
        db.session.commit()
    else:
        db.session.delete(vote)
        post.vote_count = post.vote_count - 1
        db.session.commit()
    return redirect(request.referrer)

@app.route('/report-post/<id>')
@login_required
def report_post(id):
    userid = current_user.id
    post = Post.query.filter_by(id=id).first()
    report = Report.query.filter_by(post_id=post.id, user_id=userid).first()

    if not report:
        reportsCount = Report.query.filter_by(post_id=post.id).count()
        if reportsCount > 4 or \
           current_user.is_admin() or \
           current_user.is_mod():
            post.enabled = False

        new_report = Report(
            user_id = userid,
            post_id = post.id
        )
        db.session.add(new_report)
        db.session.commit()

    # Flash the reporting success
    flash(gettext("Post was reported"), "success")
    return redirect(request.referrer)

@app.route('/enable-post/<id>')
@min_role_required(ROLES["mod"])
def enable_post(id):
    post = Post.query.filter_by(id=id).first()
    reports = Report.query.filter_by(post_id=id).all()

    for report in reports:
        db.session.delete(report)

    post.enabled = True
    db.session.commit()

    return redirect(request.referrer)



# USERS ACTIONS
@app.route('/user/<id>')
def user_view(id):
    user = User.query.filter_by(id=id).first()

    if not user.enabled:
        flash(gettext("This account is suspended"), "danger")
        return redirect(url_for('index'))

    return render_template('user.html', user=user)

@app.route('/enable-user/<id>')
@min_role_required(ROLES["mod"])
def enable_user(id):
    user = User.query.filter_by(id=id).first()
    user.enabled = True
    db.session.commit()

    return redirect(request.referrer)

@app.route('/disable-user/<id>')
@min_role_required(ROLES["mod"])
def disable_user(id):
    user = User.query.filter_by(id=id).first()

    if user.is_admin():
        flash(gettext("Can't disable an administrator"), "danger")
    else:
        user.enabled = False
        db.session.commit()

    return redirect(request.referrer)

@app.route('/delete-user/<id>')
@admin_required()
def delete_user(id):
    user = User.query.filter_by(id=id).first()
    db.session.delete(user)
    db.session.commit()

    return redirect(request.referrer)

@app.route('/promote-user/<id>', methods=['POST'])
@admin_required()
def promote_user(id):
    new_role = request.form.get("new_role")
    user = User.query.filter_by(id=id).first()
    user.role = new_role
    db.session.commit()

    return redirect(request.referrer)



# COMMENTS ACTIONS

@app.route('/comment-post/<id>', methods=['POST'])
@login_required
def comment_post(id):
    userid = current_user.id
    post = Post.query.filter_by(id=id).first()
    content = request.form.get("content")

    if not content:
        flash(gettext("Your comment cannot be empty!"), "danger")
        return redirect(url_for('post', id=id))

    comment = Comment(
        user_id = userid,
        post_id = post.id,
        content = content
    )
    post.comment_count = post.comment_count + 1
    db.session.add(comment)
    db.session.commit()

    return redirect(url_for('post', id=id))

@app.route('/enable-comment/<id>')
@min_role_required(ROLES["mod"])
def enable_comment(id):
    comment = Comment.query.filter_by(id=id).first()
    comment.enabled = True
    post = Post.query.filter_by(id=comment.post_id).first()
    post.comment_count = post.comment_count + 1
    db.session.commit()

    return redirect(url_for('post', id=comment.post_id))

@app.route('/disable-comment/<id>')
@min_role_required(ROLES["mod"])
def disable_comment(id):
    comment = Comment.query.filter_by(id=id).first()
    comment.enabled = False
    post = Post.query.filter_by(id=comment.post_id).first()
    post.comment_count = post.comment_count - 1
    db.session.commit()

    return redirect(url_for('post', id=comment.post_id))

@app.route('/delete-comment/<id>')
@admin_required()
def delete_comment(id):
    comment = Comment.query.filter_by(id=id).first()
    post = Post.query.filter_by(id=comment.post_id).first()
    post.comment_count = post.comment_count - 1

    db.session.delete(comment)
    db.session.commit()

    return redirect(url_for('post', id=comment.post_id))

@app.route('/contact', methods=['GET','POST'])
def contact_us():

    if request.method == 'POST':

        email = request.form.get("email")
        object = request.form.get("object")
        body = request.form.get("body")
        trap = request.form.get("trp")

        # Email validation
        try:
            valid = validate_email(email)
            email = valid.email
        except EmailNotValidError:
            flash(gettext("Email is invalid"), "danger")
            return redirect(url_for('contact_us'))

        if trap:
            flash(gettext("Humans only!"), "danger")
            return redirect(url_for('contact_us'))

        if not object:
            flash(gettext("Your message should have an object"), "danger")
            return redirect(url_for('contact_us'))

        if not body:
            flash(gettext("Your message should'nt be empty"), "danger")
            return redirect(url_for('contact_us'))

        # Send email to owner
        send_email(app.config['APP_NAME'] + " - " + gettext("Contact"),
           sender = app.config['MAIL_USERNAME'],
           recipients = [app.config['OWNER_EMAIL']],
           reply_to = email,
           html_body = render_template('emails/contact_email.html', body=body, email=email))

        # Flash the deletion success
        flash(gettext("Thanks for reaching out! We'll reply as soon as possible"), "success")
        return redirect(url_for('index'))

    else:  # GET
        return render_template('contact_us.html')

# UPLOADED PICTURES
@app.route('/uploads/<filename>')
def upload(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'].replace('crommunity/',''), filename)