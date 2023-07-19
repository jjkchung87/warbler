"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows, Likes

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


class MessageModelTestCase(TestCase):
    """Test Message model."""

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

        messageId = 999
        message1 = Message(id=messageId, text="i like raw!", user_id=self.user1.id)
        db.session.add(message1)
        db.session.commit()

        self.message1 = message1

        follow = Follows(user_being_followed_id=1,
            user_following_id=2)
        
        db.session.add(follow)
        db.session.commit()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res    


    def test_message_model(self):
        """test basics of message model"""

        self.assertTrue(len(self.user1.messages)==1)
        self.assertFalse(len(self.user2.messages)==1)
        
    def test_message_likes(self):
        """test message liking"""

        self.user2.likes.append(self.message1)
        db.session.commit()
        like = Likes.query.filter_by(message_id=999).first()

        self.assertTrue(len(self.user2.likes)==1)
        self.assertEqual(like.user_id, self.user2.id)
        
