from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, FloatField
from wtforms.fields.html5 import DecimalRangeField
from wtforms.validators import DataRequired, Email, Length

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

    drink_name = StringField("Drink")
    rating = FloatField("Rating")
    review = StringField("Review") 
    image=StringField("Image URL")

class EditReviewForm(FlaskForm):
    
    rating = FloatField("Rating")
    review = StringField("Review") 
    image=StringField("Image URL")
    

class UserEditForm(FlaskForm):
    """Form for editing user-info"""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    profile_img = StringField('Profile Image')
    banner_img = StringField('Banner Image')
    bio=StringField('Bio')
    password=PasswordField('Password',  validators=[DataRequired()])

class CommentForm(FlaskForm):
    """Form to comment on users' reviews"""

    text=StringField('Comment', validators=[DataRequired()]) #how to add a text limit validator?