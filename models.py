"""SQLAlchemy models for app."""

from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)

class Follows(db.Model):
    """Following and followers"""

    __tablename__='follows'

    user_being_followed_id=db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        primary_key=True
    )

    user_following_id=db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        primary_key=True
    )

class Likes(db.Model):
    """Likes of reviews"""

    __tablename__ = 'likes'

    id=db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id=db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )

    reviews_id=db.Column(
        db.Integer,
        db.ForeignKey('reviews.id', ondelete='CASCADE'),
        nullable=False
    )

class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

   

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    email = db.Column(
        db.Text,
        nullable=False
        # unique=True,
    )

    bio = db.Column(
        db.String(200),
    )

    profile_img = db.Column(
        db.Text,
        default="/static/images/default-pic.png",
    )

    banner_img = db.Column(
        db.Text,
        default="/static/images/warbler-hero.jpg"
    )
    

    reviews = db.relationship('Review')

    followers = db.relationship(
        "User",
        secondary="follows",
        primaryjoin=(Follows.user_being_followed_id == id),
        secondaryjoin=(Follows.user_following_id == id)
    )

    following = db.relationship(
        "User",
        secondary="follows",
        primaryjoin=(Follows.user_following_id == id),
        secondaryjoin=(Follows.user_being_followed_id == id)
    )

    likes = db.relationship(
        'Review',
        secondary="likes",
        primaryjoin=(Likes.user_id == id))
    

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"

    def is_followed_by(self, other_user):
        """Is this user followed by `other_user`?"""

        found_user_list = [user for user in self.followers if user == other_user]
        return len(found_user_list) == 1

    def is_following(self, other_user):
        """Is this user following `other_use`?"""

        found_user_list = [user for user in self.following if user == other_user]
        return len(found_user_list) == 1

    @classmethod
    def signup(cls, username, email, password, profile_img):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            profile_img=profile_img
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

class Review(db.Model):
    """An individual review made by a user."""

    __tablename__ = 'reviews'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    drink_id= db.Column(
        db.Integer,
        db.ForeignKey('drinks.id', ondelete='CASCADE'),
        nullable=False
    )

    drink = db.relationship('Drink')

    rating = db.Column(
        db.Integer,
        nullable = False
    )

    review = db.Column(
       db.String(200)
    )

    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow(),
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )

    user = db.relationship('User')

class Drink(db.Model):
    """Drink recipe model"""

    __tablename__ = 'drinks'

    id= db.Column(
        db.Integer, 
        primary_key=True,
        autoincrement=True
    )

    name=db.Column(
        db.String,
        nullable=False)

    ingredients=db.Column(
        db.String,
        nullable=False)

    instructions=db.Column(
        db.String,
        nullable=False
    )

    image=db.Column(
        db.String
    )


class Saved_recipe(db.Model):
    """Saved recipe"""

    __tablename__ = 'saved_recipes'

    id=db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    drink_id=db.Column(
        db.Integer,
        db.ForeignKey('drinks.id', ondelete='CASCADE'),
        nullable=False)

    drink=db.relationship('Drink')

    user_id=db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False)
    
    user=db.relationship('User', backref="saved_recipes")




