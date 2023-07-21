import os

from flask import Flask, render_template, request, flash, redirect, session, g, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_

from forms import UserAddForm, LoginForm, MessageForm, UserUpdateForm
from models import db, connect_db, User, Message, Follows, Likes, DEFAULT_IMG_URL

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///warbler'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['EXPLAIN_TEMPLATE_LOADING'] = True
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
app.debug=True
toolbar = DebugToolbarExtension(app)

connect_db(app)


##############################################################################
# User signup/login/logout


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global "g". Used to manage user auth and access control throughout application"""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                image_url=form.image_url.data or User.image_url.default.arg,
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""
    
    form = LoginForm()


    # if form.validate_on_submit():
    #     user = User.authenticate(form.username.data,
    #                              form.password.data)

    #     if user:
    #         do_login(user)
    #         flash(f"Hello, {user.username}!", "success")
    #         return redirect("/")

    #     flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""
    
    do_logout()
    flash('Successfully logged out.','success')
    return redirect('/')


##############################################################################
# General user routes:

@app.route('/users')
def list_users():
    """Page with listing of users.

    Can take a 'q' param in querystring to search by that username.
    """

    search = request.args.get('q')

    if not search:
        users = User.query.all()
    else:
        users = User.query.filter(User.username.like(f"%{search}%")).all()

    return render_template('users/index.html', users=users)


@app.route('/users/<int:user_id>')
def users_show(user_id):
    """Show user profile."""

    user = User.query.get_or_404(user_id)

    # snagging messages in order from the database;
    # user.messages won't be in order by default
    messages = (Message
                .query
                .filter(Message.user_id == user_id)
                .order_by(Message.timestamp.desc())
                .limit(100)
                .all())
    return render_template('users/show.html', user=user, messages=messages)


@app.route('/users/<int:user_id>/following')
def show_following(user_id):
    """Show list of people this user is following."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    return render_template('users/following.html', user=user)


@app.route('/users/<int:user_id>/followers')
def users_followers(user_id):
    """Show list of followers of this user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    return render_template('users/followers.html', user=user)

@app.route('/users/<int:user_id>/likes')
def show_likes(user_id):
    """show users liked messages"""

    if not g.user:
        flash("Access unauthorized","danger")
        return redirect("/")
    
    user = User.query.get_or_404(user_id)
    return render_template('users/likes.html', user=user)


@app.route('/users/follow/<int:follow_id>', methods=['POST'])
def add_follow(follow_id):
    """Add a follow for the currently-logged-in user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    followed_user = User.query.get_or_404(follow_id)
    g.user.following.append(followed_user)
    db.session.commit()

    return redirect(f"/users/{g.user.id}/following")


@app.route('/users/stop-following/<int:follow_id>', methods=['POST'])
def stop_following(follow_id):
    """Have currently-logged-in-user stop following this user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    followed_user = User.query.get(follow_id)
    g.user.following.remove(followed_user)
    db.session.commit()

    return redirect(f"/users/{g.user.id}/following")


@app.route('/users/profile', methods=["GET", "POST"])
def update_profile():
    """Update profile for current user."""

    form = UserUpdateForm(obj = g.user)
    
    if not g.user:
        flash("Access unauthorized.","danger")
        return redirect("/")    

    if form.validate_on_submit():
        if not User.authenticate(g.user.username,form.password.data):
            flash("Incorrect password. Profile update failed.", "danger")
            return redirect(f'/users/{g.user.id}')
        g.user.username = form.username.data
        g.user.email = form.email.data
        g.user.image_url = form.image_url.data
        g.user.header_image_url = form.header_image_url.data
        g.user.bio = form.bio.data

        db.session.commit()

        return redirect(f'/users/{g.user.id}')
    
    return render_template('/users/edit.html', form=form)


@app.route('/users/delete', methods=["POST"])
def delete_user():
    """Delete user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect("/signup")


##############################################################################
# Messages routes:

@app.route('/messages/new', methods=["GET", "POST"])
def messages_add():
    """Add a message:

    Show form if GET. If valid, update message and redirect to user page.
    """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = MessageForm()

    if form.validate_on_submit():
        msg = Message(text=form.text.data)
        g.user.messages.append(msg)
        db.session.commit()

        return redirect(f"/users/{g.user.id}")

    return render_template('messages/new.html', form=form)


@app.route('/messages/<int:message_id>', methods=["GET"])
def messages_show(message_id):
    """Show a message."""

    msg = Message.query.get(message_id)
    return render_template('messages/show.html', message=msg)


@app.route('/messages/<int:message_id>/delete', methods=["POST"])
def messages_destroy(message_id):
    """Delete a message."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    msg = Message.query.get(message_id)

    if msg.user_id != g.user.id:
        flash("Not authorized to delete this message","danger")
        return redirect(request.referrer)
    
    else:
        db.session.delete(msg)
        db.session.commit()
        return redirect(f"/users/{g.user.id}")

# @app.route('/messages/<int:message_id>/like', methods=['POST'])
# def toggle_like(message_id):
#     """Toggle a liked message for the currently-logged-in user."""

#     if not g.user:
#         flash("Access unauthorized.", "danger")
#         return redirect("/")

#     liked_message = Message.query.get_or_404(message_id)
#     if liked_message.user_id == g.user.id:
#         flash("Access unauthorized.", "danger")
#         return redirect("/")

#     user_likes = g.user.likes

#     if liked_message in user_likes:
#         g.user.likes = [like for like in user_likes if like != liked_message]
#     else:
#         g.user.likes.append(liked_message)

#     db.session.commit()

#     return redirect("/")





##############################################################################
# Homepage and error pages


@app.route('/')
def homepage():
    """Show homepage:

    - anon users: no messages
    - logged in: 100 most recent messages of followed_users
    """

    if g.user:
        messages = (Message
                    .query
                    .filter(or_(Message.user_id == g.user.id, Message.user_id.in_(
                        db.session.query(Follows.user_being_followed_id).filter_by(user_following_id=g.user.id)
                    )))
                    .order_by(Message.timestamp.desc())
                    .limit(100)
                    .all())

        return render_template('home.html', messages=messages, user=g.user)

    else:
        return render_template('home-anon.html')


##############################################################################
# Turn off all caching in Flask
#   (useful for dev; in production, this kind of stuff is typically
#   handled elsewhere)
#
# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask

@app.after_request 
def add_header(req):
    """Add non-caching headers on every request, to ensure client does not cache the response and always requests fresh content from server"""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req

##############################################################################
# API Routes


@app.route('/warbler/api/users/login', methods=['POST'])
def login_endpoint():
    """endpoint for user login"""
    username = request.json['username']
    password = request.json['password']

    auth_user = User.authenticate(username, password)
    likes = [like.serialize() for like in auth_user.likes]
    
    do_login(auth_user)
    user_id = auth_user.id
    messages = (Message.query.filter(or_(Message.user_id == user_id, Message.user_id.in_(db.session.query(Follows.user_being_followed_id).filter_by(user_following_id=user_id)))).order_by(Message.timestamp.desc()).limit(100).all())

    return jsonify(user=auth_user.serialize(), likes=likes, messages=[message.serialize() for message in messages])

@app.route('/warbler/api/users/<int:user_id>')
def retrieve_loggedin_user_details(user_id):
    """retrieve details of logged in user"""
    user = User.query.get(user_id)
    likes = [like.serialize() for like in user.likes]
    user_id=user.id
    messages = (Message.query.filter(or_(Message.user_id == user_id, Message.user_id.in_(db.session.query(Follows.user_being_followed_id).filter_by(user_following_id=user_id)))).order_by(Message.timestamp.desc()).limit(100).all())
    return jsonify(user=user.serialize(), likes=likes, messages=[message.serialize() for message in messages])


@app.route('/warbler/api/users/<int:user_id>/likes/<int:message_id>', methods=['PATCH'])
def add_like(user_id):
    """end-point for Liking a message"""
    messageId = request.json['message_id']
    user = User.query.get(user_id)
    message = Message.query.get(messageId)

    user.likes.append(message)
    db.session.add_all([user,message])
    db.session.commit()
    likes = [like.serialize() for like in user.likes]
    return jsonify(user=user.serialize(), likes=likes)

@app.route('/warbler/api/users/<int:user_id>/likes/<int:message_id>', methods=['DELETE'])
def remove_like(user_id, message_id):
    """end-point for unliking a message"""
    user = User.query.get(user_id)
    message = Message.query.get(message_id)

    user.likes.remove(message)
    db.session.add(user)
    db.session.commit()
    likes = [like.serialize() for like in user.likes]
    return jsonify(user=user.serialize(), likes=likes)

@app.route('/warbler/api/users/<int:user_id>/messages', methods=['POST'])
def new_message(user_id):
    """end-point when user adds new message"""

    user = User.query.get(user_id)
    text = request.json['text']
    newMessage = Message(text = text, 
            user_id = user.id)
    db.session.add_all([user, newMessage])
    db.session.commit()
    return jsonify(message = newMessage.serialize())
    
    

