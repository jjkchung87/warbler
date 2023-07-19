"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User, Follows, Likes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()
        self.testuser1id = 900
        self.testuser1 = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        
        self.testuser1.id=self.testuser1id

        self.testuser2id = 901
        self.testuser2 = User.signup(username="testuser2",
                                    email="test2@test.com",
                                    password="testuser2",
                                    image_url=None)
        self.testuser2.id=self.testuser2id

        self.testuser3id = 902
        self.testuser3 = User.signup(username="testuser3",
                                    email="test3@test.com",
                                    password="testuser3",
                                    image_url=None)
        self.testuser3.id=self.testuser3id

        db.session.commit()

    def tearDown(self):
        
        resp = super().tearDown()
        db.session.rollback()
        return resp

    def setup_follows(self):
        """set-up follows"""

        f1 = Follows(user_being_followed_id=self.testuser1id, user_following_id=self.testuser2id)
        f2 = Follows(user_being_followed_id=self.testuser2id, user_following_id=self.testuser3id)
        f3 = Follows(user_being_followed_id=self.testuser3id, user_following_id=self.testuser1id)

        db.sesion.add_all([f1,f2,f3])
        db.session.commit()

    def setup_likes(self):
        """set up likes"""

        m1 = Message(user_id=self.testuser1id, text="message1")
        m1id=99
        m1.id=m1id
        m2 = Message(user_id=self.testuser1id, text="message2")
        m3 = Message(user_id=self.testuser2id, text="message3")

        db.session.add_all([m1,m2,m3])
        db.session.commit()

        l1 = Likes(message_id=m1.id, user_id=self.testuser2id)
        db.session.add(l1)
        db.session.commit()
    
    # def test_user_show_with_likes(self):
    def test_add_like(self):
        """test addding a like"""

        m = Message(id=2000,user_id=self.testuser2id, text="message4")
        db.session.add(m)
        db.session.commit()

        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1id

            resp = client.post("/users/add_like/2000",follow_redirects=True)
            
            likes = Likes.query.filter_by(message_id=2000).all()
            self.assertTrue(len(likes) == 1)
            self.assertTrue(likes[0].user_id==self.testuser1id)

            
            


    def test_remove_like(self):
        """test removing a like"""

        self.setup_likes()
        m1=Message.query.get(99)

        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser2id
            
            resp = client.post("/users/add_like/99", follow_redirects=True)

            likes = Likes.query.all()
            # self.assertTrue(len(self.testuser2.likes)==0)
            self.assertTrue(len(likes)==0)
            

    def test_unauthenticated_like(self):
        """test unauthenticated like"""

        self.setup_likes()

        likes = Likes.query.all()
        self.assertIsNotNone(likes)

        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1id
            
            resp = client.post("/users/add_like/99",follow_redirects=True)
            

            self.assertEqual(len(likes),1)
            self.assertIn('Cannot like own message',str(resp.data))


    def test_user_show_with_follows(self):
        """test showing user with """

    # def test_show_following(self):
    # def test_show_followers(self):
    # def test_unauthorized_following_page_access(self):
    # def test_unauthorized_followers_page_access(self):








    # def test_see_others_follows_when_logged_in(self):
    #     """Can you see others followers and followings when logged in?"""

    #     # Since we need to change the session to mimic logging in,
    #     # we need to use the changing-session trick:

    #     with self.client as client:
    #         with client.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = self.testuser1.id

    #         # Now, that session setting is saved, so we can have
    #         # the rest of ours test

    #         resp = client.get(f"/users/{self.testuser2.id}/following")
    #         html = resp.get_data(as_text=True)
        
    #         self.assertEqual(resp.status_code, 200)
    #         self.assertIn('@testuser', html)