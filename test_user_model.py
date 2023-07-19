"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        user_table = User.__table__
        user_pk_sequence = f"{user_table.name}_{user_table.primary_key.columns.values()[0].name}_seq"
        db.session.execute(f"ALTER SEQUENCE {user_pk_sequence} RESTART WITH 1")


        self.client = app.test_client()

        user1 = User.signup(email="arlo@dog.com",
        username="arlo_chung",
        password="arlo123",
        image_url="")
        
        db.session.add(user1)
        db.session.commit()

        self.user1 = user1

        user2 = User.signup(email="willow@dog.com",
        username="willow_chung",
        password="willow123",
        image_url="")
        
        db.session.add(user2)
        db.session.commit()

        self.user2 = user2

        user3 = User.signup(email="rory@golf.com",
        username="rory_mcilroy",
        password="rory123",
        image_url="")
        
        db.session.add(user3)
        db.session.commit()

        self.user3 = user3

        follow = Follows(user_being_followed_id=1,
            user_following_id=2)
        
        db.session.add(follow)
        db.session.commit()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res    


    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_repr(self):
        """Test repr method"""

        self.assertEqual(self.user1.__repr__(),"<User #1: arlo_chung, arlo@dog.com>")

    def test_is_following(self):
        """test if is_following is working correctly"""

        self.assertEqual(self.user2.is_following(self.user1), True)
        self.assertEqual(self.user3.is_following(self.user1), False)

    def test_is_followed_by(self):
        """test if is_followed_by is working correctly"""

        self.assertEqual(self.user1.is_followed_by(self.user2), True)
        self.assertEqual(self.user1.is_following(self.user3), False)

    def test_valid_signup(self):
        """tests a proper signup"""

        user4 = User.signup(username='tiger_woods', email='tiger@golf.com', password='tiger123', image_url="")
        db.session.commit()
        
        user = User.query.filter_by(username='tiger_woods').first()
        self.assertEqual(user.email,'tiger@golf.com')
        self.assertEqual(user.username,'tiger_woods')
        self.assertNotEqual(user.password,'tiger123')
        self.assertTrue(user.password.startswith('$2b$'))

    def test_invalid_signup(self):
        """tests invalid signup"""
        user5 = User.signup(username="arlo_chung", email="arlothedog@dog.com", password="arlo456", image_url="")

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_valid_authentication(self):
        """tests authentication"""

        authenticated_user = User.authenticate(username="arlo_chung", password="arlo123")
          
        self.assertEqual(authenticated_user.username, 'arlo_chung')
        self.assertEqual(authenticated_user.email, 'arlo@dog.com')

    def test_invalid_authentication(self):
        """tests invalid authentication"""

        self.assertFalse(User.authenticate(username="arlo_chung", password="arlo789"))    