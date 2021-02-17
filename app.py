import os
import requests

from jinja2 import Template
from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_
from forms import SignUp, LoginForm, ReviewForm, UserEditForm, CommentForm

from models import User, Review, Drink, Saved_recipe, Likes, Follows, Comment, db, connect_db

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

    if g.user:
        reviews = (Review
                    .query
                    .filter(or_(Review.user_id.in_([ user.id for user in g.user.following]), Review.user_id==g.user.id))
                    .order_by(Review.timestamp.desc())
                    .limit(100)
                    .all())
        
        # get all the likes with g.user.id=user_id and get the reviews_id's from this
        likes=Likes.query.with_entities(Likes.reviews_id).filter(Likes.user_id == g.user.id).all()

        result = [] 

        # turn likes (list of tuples) into just a list
        for t in likes: 
            for x in t: 
                result.append(x)

        #comment=Comment(user_id=g.user.id, reviews_id=review_id, text=form.text.data)

        # comments=Comment.query.with_entities(Comment.reviews_id).all()
        comments=Comment.query.all()

        form=CommentForm() 
           
        return render_template('home.html', reviews=reviews, likes=result, form=form, comments=comments)

    return render_template("home.html")

@app.route('/search', methods=["POST"])
def search_drink():
    """Searches api for """

    search_term=request.form["search"]

    resp=requests.get(f"https://www.thecocktaildb.com/api/json/v1/1/search.php",
                        params={"s": search_term}
        )

    details=resp.json() #converts to python dictionary

    
    
    my_drinks=details["drinks"] #gives list of drinks
    my_drinks_reduced=[]
    if my_drinks:
        
        for item in my_drinks: #each dict of different drink, item=1 drink
            drink_dict={"strDrink": item["strDrink"],
                      "strDrinkThumb": item["strDrinkThumb"],
                    "strInstructions": item["strInstructions"]}
  
            for key in item:
                if item[key]:
      #this keeps getting mutated :( 
                    all_ingredients=[]
                    for number in range(1,16):
                        if item[f"strMeasure{number}"] and item[f"strIngredient{number}"]:
                            x=item[f"strMeasure{number}"]
                            y=item[f"strIngredient{number}"]
                            combined=x + ' '+ y
                            all_ingredients.append(combined)
                        elif item[f"strIngredient{number}"]:
                            y=item[f"strIngredient{number}"]
                            all_ingredients.append(y)
   
            drink_dict["ingredient_list"]=all_ingredients
            my_drinks_reduced.append(drink_dict)
    

    return render_template("drink_details.html", drink_list=my_drinks_reduced, search_term=search_term)

@app.route('/random', methods=["POST"])
def search_random_drink():
    """Generates a random cocktail recipe for the user"""
    resp=requests.get("https://www.thecocktaildb.com/api/json/v1/1/random.php")
    details=resp.json()

    
    my_drinks=details["drinks"] #gives list of drinks
    my_drinks_reduced=[]
    if my_drinks:
        
        for item in my_drinks: #each dict of different drink, item=1 drink
            drink_dict={"strDrink": item["strDrink"],
                      "strDrinkThumb": item["strDrinkThumb"],
                    "strInstructions": item["strInstructions"]}
  
            for key in item:
                if item[key]:
      #this keeps getting mutated :( 
                    all_ingredients=[]
                    for number in range(1,16):
                        if item[f"strMeasure{number}"] and item[f"strIngredient{number}"]:
                            x=item[f"strMeasure{number}"]
                            y=item[f"strIngredient{number}"]
                            combined=x + ' '+ y
                            all_ingredients.append(combined)
                        elif item[f"strIngredient{number}"]:
                            y=item[f"strIngredient{number}"]
                            all_ingredients.append(y)
   
            drink_dict["ingredient_list"]=all_ingredients
            my_drinks_reduced.append(drink_dict)
    

    return render_template("random_drink.html", drink_list=my_drinks_reduced)

@app.route("/instructions")
def user_instructions():
    if not g.user:
        flash("Please login or create an account to view these instructions.", "danger")
        return redirect("/")

    return render_template("instructions.html")

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

    form=CommentForm()

    comments=Comment.query.all()
    likes=Likes.query.with_entities(Likes.reviews_id).filter(Likes.user_id == g.user.id).all()
    result = [] 

        # turn likes (list of tuples) into just a list
    for t in likes: 
        for x in t: 
            result.append(x)


    return render_template('user_profile.html', user=user, reviews=reviews, form=form, comments=comments, likes=result)

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

@app.route('/users', methods=["GET", "POST"])
def show_users():
    """List page of users"""
    if not g.user:
        flash("Please login or create an account to view users.", "danger")
        return redirect("/")

    users = User.query.all()

    return render_template("list_users.html", users=users)

@app.route('/users/follow/<int:user_id>', methods=["POST"])
def follow_user(user_id):
    """Follow user"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    follow = User.query.get_or_404(user_id)
    g.user.following.append(follow)
    db.session.commit()

    flash(f"You are now following @{follow.username}", "success")
    return redirect("/users")

@app.route('/users/stop-following/<int:user_id>', methods=['POST'])
def stop_following(user_id):
    """Have currently-logged-in-user stop following this user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    followed_user = User.query.get(user_id)
    g.user.following.remove(followed_user)
    flash(f"You have unfollowed @{followed_user.username}", "primary")
    db.session.commit()

    return redirect(f"/users")

@app.route('/save', methods=["POST"])
def save_recipe():
    """Adds the drink to the db, if not there currently and then saves the recipe for the user"""
    if not g.user:
        flash('You must be logged into an account to save a recipe', 'danger')
        return redirect('/')

    name=request.form["name"]
    ingredients=request.form["ingredients"] 
    instructions=request.form["instructions"]
    image=request.form["image"]

    #if the drink is already in the db
    if Drink.query.filter_by(name=name).first():
        drink=Drink.query.filter_by(name=name).first()
    
    #if the drink is not saved as an instance of Drink in the db
    else:
        drink=Drink(name=name, ingredients=ingredients, instructions=instructions, image=image)
        db.session.add(drink)
        db.session.commit()

    if Saved_recipe.query.filter_by(user_id=g.user.id, drink_id=drink.id).all():
        flash(f"You have already saved the recipe for {drink.name}", "danger")
        return redirect('/')
        

    #now make the drink a saved recipe for the user
    saved=Saved_recipe(drink_id=drink.id, user_id=g.user.id)
    db.session.add(saved)
    db.session.commit()

    #on the saved page, we want ALL of the particular user's saved recipes to 
    return redirect(f"/users/{g.user.id}/saved") #might not want to jump right to the page

@app.route('/users/<int:user_id>/saved')
def show_saved_recipe(user_id):
    """shows page on user profile of all saved recipes"""
    user_drinks=g.user.saved_recipes

    # all_ingredients_list=[]
    # for one_drink in user_drinks:
    #     ingredients=one_drink.drink.ingredients
    #     ingredients_list=ingredients.split(",")
    #     all_ingredients_list
  
    return render_template("saved_recipes.html", user_drinks=user_drinks) 



@app.route('/users/<int:user_id>/following')
def show_following(user_id):
    """Show list of people this user is following."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    return render_template('following.html', user=user)


@app.route('/users/<int:user_id>/followers')
def users_followers(user_id):
    """Show list of followers of this user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    return render_template('followers.html', user=user)

@app.route('/delete/<int:drink_id>', methods=["POST"])
def delete_saved(drink_id):
    """Remove a drink from a user's saved drinks"""
    #need to obtain the drin_id from the template!
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
     #logic to unlike if the liked message is already an instance of the Likes class
    if Saved_recipe.query.filter_by(user_id=g.user.id, drink_id=drink_id).all():
        saved_recipe=Saved_recipe.query.filter_by(user_id=g.user.id, drink_id=drink_id).one()
        db.session.delete(saved_recipe)
        db.session.commit()
        return redirect(f'/users/{g.user.id}/saved')

    return redirect('/')

@app.route('/users/add_like/<int:review_id>', methods=["POST"])
def like_message(review_id):
    """Like/"cheers" a message."""


    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    #prevent user from liking their own message
    # m = Message.query.get(message_id)
    # if m in g.user.messages:
    #     flash("You cannot like your own message.", "danger")
    #     return redirect ("/")
    
    #logic to unlike if the liked message is already an instance of the Likes class
    if Likes.query.filter_by(user_id=g.user.id, reviews_id=review_id).all():
        liked_msg=Likes.query.filter_by(user_id=g.user.id, reviews_id=review_id).one()
        db.session.delete(liked_msg)
        db.session.commit()
        return redirect('/')

    #like the message otherwise
    liked_msg=Likes(user_id=g.user.id, reviews_id=review_id)
    db.session.add(liked_msg)
    db.session.commit()

    return redirect("/")

@app.route('/users/<int:user_id>/likes') #not using yet...
def show_likes(user_id):
    """Show list of likes"""
    likes=g.user.likes

@app.route('/users/comment/<int:review_id>', methods=["POST"])
def comment(review_id):
    """Comment on a user's post"""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form=CommentForm()
    
    
    comment=Comment(user_id=g.user.id, reviews_id=review_id, text=form.text.data)
    db.session.add(comment)
    db.session.commit()

    return redirect("/")

@app.route('/users/delete/<int:review_id>', methods=["POST"])
def delete_review(review_id):
    
    if not g.user:
        flash("Access denied", "danger")
        return redirect('/')

    delete_me=Review.query.get_or_404(review_id)

    if delete_me.user_id != g.user.id:
        flash("You are not allowed to delete another user's post", 'danger')
        redirect('/')

    flash(f"Your review of {delete_me.drink.name} has been deleted", 'success')
    db.session.delete(delete_me)
    db.session.commit()
    return redirect('/')

@app.route('/users/edit/<int:review_id>', methods=["GET","POST"])
def edit_review(review_id):
    """Returns and processess form to edit a review"""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    review=Review.query.get(review_id)
    form=ReviewForm(obj=review)
    drink_name=review.drink.name

    if form.image.data:
            display_img=form.image.data
    else:
            display_img="https://banner2.cleanpng.com/20190714/uvh/kisspng-martini-cocktail-glass-clip-art-vector-graphics-home-forty-two-peterborough-5d2b093a9f6130.8579484215631014986528.jpg"
    
    if form.validate_on_submit():
           

            review.rating=form.rating.data 
            review.review=form.review.data 
            review.image=display_img
            
            db.session.commit()

            flash("Your changes have been saved", 'success')

            return redirect("/")


    return render_template("edit_review.html", form=form, drink=drink_name)

@app.route('/reviews/<int:saved_drink_id>', methods=["GET", "POST"])
def review_for(saved_drink_id):
    """Returns and processes form to make a review for a drink"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = ReviewForm()

    saved_drink=Saved_recipe.query.get(saved_drink_id)
    
    if form.validate_on_submit():

        if form.image.data:
            display_img=form.image.data
        else:
            display_img="https://banner2.cleanpng.com/20190714/uvh/kisspng-martini-cocktail-glass-clip-art-vector-graphics-home-forty-two-peterborough-5d2b093a9f6130.8579484215631014986528.jpg"

        review = Review(
            drink_id= saved_drink.drink.id,
            rating=round(float(form.rating.data),2),
            review=form.review.data,
            image=display_img,
            user_id=g.user.id
        )
        
        db.session.add(review)    
        db.session.commit()

        return redirect("/")

    return render_template("single_review.html", saved_drink=saved_drink, form=form)

@app.route("/users/<int:comment_id>/delete", methods=["POST"])
def delete_comment(comment_id):
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    comment=Comment.query.get(comment_id)

    if comment.user_id is not g.user.id:
        flash("You cannot delete another user's comment that is not on your post")
        return redirect("/")

    db.session.delete(comment)
    db.session.commit()

    return redirect("/")
    






