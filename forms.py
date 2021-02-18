from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, FloatField
from wtforms.fields.html5 import DecimalRangeField
from wtforms.validators import DataRequired, Email, Length, URL, NumberRange, Optional
from wtforms.widgets.html5 import RangeInput

class SignUp(FlaskForm):
    """Form to sign up as a new user"""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password',validators=[Length(min=6)] ) 
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    profile_img = StringField('Profile Image URL (optional)')

class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])


class ReviewForm(FlaskForm):
    
    rating = FloatField("Rating (0 to 5)", validators=[DataRequired(), NumberRange(min=0, max=5, message="Your rating must be a value between 0 and 5")])
    review = StringField("Review", validators=[Length(max=50, message="Your review cannot exceed 50 characters")]) 
    image=StringField("Image URL", validators=[URL(), Optional()])

    #  validators=[URL()] --> not working bc won't allow a null input
    

class UserEditForm(FlaskForm):
    """Form for editing user-info"""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    profile_img = StringField('Profile Image')
    banner_img = StringField('Banner Image')
    bio=StringField('Bio', validators=[Length(max=120, message="Your review cannot exceed 100 characters")])
    password=PasswordField('Password',  validators=[DataRequired()])

class CommentForm(FlaskForm):
    """Form to comment on users' reviews"""

    text=StringField('Comment', validators=[DataRequired()]) #how to add a text limit validator?