"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_Review_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import  db, User, Review, Follows, Likes, Comment, Drink
# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///project-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class ReviewModelTestCase(TestCase):
    """Test views for reviews"""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        self.uid = 94566
        u = User.signup("testing", "testing@test.com", "password", None)
        u.id = self.uid
        db.session.commit()

        self.u = User.query.get(self.uid)

        self.client = app.test_client()

        self.d1id = 5555555
        d1=Drink(name="TestDrink", ingredients="[gin, tonic water]", instructions="Mix ingredients", image=None)

        db.session.commit()

        d1.id=self.d1id

        db.session.commit()

        self.d1=Drink.query.get(self.d1id)

      

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_review_model(self):
        """Does basic model work?"""
        
        r = Review(
            drink_id=self.d1id,
            rating= 3.5,
            review="Test Review",
            user_id=self.uid,
            image= "https://images.unsplash.com/photo-1561150169-371f366b828a?ixid=MXwxMjA3fDB8MHxzZWFyY2h8MXx8YWxjb2hvbHxlbnwwfHwwfA%3D%3D&ixlib=rb-1.2.1&w=1000&q=80"
        )

        db.session.add(r)
        db.session.commit()

        # User should have 1 review
        self.assertEqual(len(self.u.reviews), 1)
        self.assertEqual(self.u.reviews[0].review, "Test Review")

    # def test_message_likes(self):
    #     m1 = Message(
    #         text="a warble",
    #         user_id=self.uid
    #     )

    #     m2 = Message(
    #         text="a very interesting warble",
    #         user_id=self.uid 
    #     )

    #     u = User.signup("yetanothertest", "t@email.com", "password", None)
    #     uid = 888
    #     u.id = uid
    #     db.session.add_all([m1, m2, u])
    #     db.session.commit()

    #     u.likes.append(m1)

    #     db.session.commit()

    #     l = Likes.query.filter(Likes.user_id == uid).all()
    #     self.assertEqual(len(l), 1)
    #     self.assertEqual(l[0].message_id, m1.id)