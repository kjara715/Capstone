import os

from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_
from forms import SignUp, LoginForm, ReviewForm, UserEditForm

from models import User, Review, Drink, Saved_recipe, Likes, Follows, db, connect_db

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgres:///cocktail_db'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "secrettt")
toolbar = DebugToolbarExtension(app)

connect_db(app)

db.create_all()

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

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


@app.route('/')
def home_page():

    return render_template("home.html")

@app.route('/register', methods=["GET", "POST"])
def register_user():
    """Returns form to register a new user.

    If form validates, adds the new User to the db, and redirects to homepage.
    
    If username is taken, re-render the form and flash msg to user """
    form=SignUp()
    if form.validate_on_submit():
        try:
            user = User.signup(
                form.username.data,
                form.email.data,
                form.password.data,
                form.profile_img.data or User.profile_img.default.arg
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken, please choose another", 'danger')
            return render_template('sign_up.html', form=form)

        do_login(user)
        flash(f"Welcome {user.username}", "success")

        return redirect("/")

    else:
        return render_template('sign_up.html', form=form)
    

@app.route('/login', methods=["GET", "POST"])
def login_user():
    """Returns a form to login user, handles login"""
    form = LoginForm()


    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        
        flash("Invalid credentials.", 'danger')

    return render_template("login.html", form=form)

@app.route('/logout')
def logout():
    """Handle logout of user."""
    if g.user == User.query.get(session[CURR_USER_KEY]):
        flash(f"{g.user.username} has been logged out", "primary")
        do_logout()
    
    # IMPLEMENT THIS
    return redirect('/login')

@app.route('/users/<int:user_id>')
def users_show(user_id):
    """Show user profile."""

    user = User.query.get_or_404(user_id)

    # snagging messages in order from the database;
    # user.messages won't be in order by default
    reviews = (Review
                .query
                .filter(Review.user_id == user_id)
                .order_by(Review.timestamp.desc())
                .limit(100)
                .all())

    return render_template('user_profile.html', user=user, reviews=reviews)

@app.route('/users/edit', methods=["GET", "POST"])
def edit_profile():
    """Update details of the user in form and handle form submit"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form=UserEditForm(obj=g.user)
    

    
    if form.validate_on_submit():
        try:
            #first see if the correct password was entered:
        
            # import pdb
            # pdb.set_trace()
            if User.authenticate(g.user.username, form.password.data) == False:
                flash(f"The password you entered is incorrect for {g.user.username}", 'danger')
                return redirect('/users/edit')

            g.user.username=form.username.data 
            g.user.email=form.email.data 
            g.user.profile_img=form.profile_img.data or User.profile_img.default.arg
            g.user.banner_img=form.banner_img.data or User.banner_img.default.arg
            g.user.bio=form.bio.data
        

            db.session.commit()

            flash("Your changes have been saved", 'success')

            return redirect(f"/users/{g.user.id}")

        except IntegrityError:
            flash("Username already taken", 'danger')
            return redirect('users/edit.html', form=form)

    return render_template("edit_user.html", form=form)