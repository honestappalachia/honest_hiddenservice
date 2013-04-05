#!/usr/bin/env python

import os
import unittest
import tempfile

from app import app, init_db

class DBTestCase(unittest.TestCase):

    user_types = ('source', 'contact')
    user_form_common = {
            'username': 'test',
            'password': 'test',
            'confirm': 'test',
        }

    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + self.db_path
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False
        self.app = app.test_client()
        init_db()
        
    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)
        
    def test_redirect_to_login(self):
        """
        If the user is not logged in, accessing the home page should redirect
        them to the login page
        """
        rv = self.app.get('/', follow_redirects=True)
        assert 'Login' in rv.data
        
    def test_signup_user_choice_selection(self):
        rv = self.app.get('/signup')
        assert 'Signup' in rv.data
        assert 'What type of user are you?' in rv.data

    def test_signup_user_choices(self):
        """
        Test that we get a signup page for each valid user type
        """
        for user_type in self.user_types:
            rv = self.app.get('/signup', data=dict(user_type=user_type),
                    follow_redirects=True)
            assert 'Signup' in rv.data

    def signup(self, username, password, confirm, user_type, **kwargs):
        """
        Signup a specific type of user. The required parameters suffice to
        submit a SignupForm. Additional parameters for the post may be
        specified as keyword arguments.
        """
        return self.app.post('/signup', data=dict(
            username=username,
            password=password,
            confirm=confirm,
            recaptcha_challenge_field='test',
            recaptcha_response_field='test',
            user_type=user_type,
            **kwargs
        ), follow_redirects=True)
    
    def shared_signup_tests(self, form):
        """
        Test common behaviors shared by all user types when signing up
        """
        rv = self.signup(**form)
        assert 'Successfully signed up' in rv.data
        rv = self.signup(**form)
        assert 'Username is already in use' in rv.data
        rv = self.signup(**dict(form, username=''))
        assert 'This field is required' in rv.data
        rv = self.signup(**dict(form, password='', confirm=''))
        assert 'This field is required' in rv.data
        rv = self.signup(**dict(form, confirm='testx'))
        assert 'Password must match in rv.data'

    def test_signup_source(self):
        source_form = dict(self.user_form_common, user_type='source')
        self.shared_signup_tests(source_form)

    def test_signup_contact(self):
        contact_form = dict(self.user_form_common, user_type='contact',
                email='test@test.com', public_key=open('devgpg.pub').read())
        self.shared_signup_tests(contact_form)
        rv = self.signup(**dict(contact_form, email=''))
        assert 'This field is required' in rv.data
        rv = self.signup(**dict(contact_form, email='notavalidemail'))
        assert 'Must be a valid email address' in rv.data
        rv = self.signup(**dict(contact_form, public_key=''))
        assert 'This field is required' in rv.data
        rv = self.signup(**dict(contact_form, public_key='notapublickey'))
        assert 'Not a valid ASCII-armored GPG public key' in rv.data

    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)
    
    def logout(self):
        return self.app.get('/logout', follow_redirects=True)
    
    def test_login_logout(self):
        username, password = 'test', 'test'
        rv = self.signup(username, password, password, user_type='source')
        rv = self.login(username, password)
        assert 'You were logged in' in rv.data
        rv = self.logout()
        assert 'You were logged out' in rv.data
        rv = self.login('testx', password)
        assert 'Invalid username' in rv.data
        rv = self.login(username, 'testx')
        assert 'Invalid password' in rv.data

    def test_delete_user(self):
        username, password = 'test', 'test'
        rv = self.signup(username, password, password, user_type='source')
        rv = self.login(username, password)
        assert 'You were logged in' in rv.data
        rv = self.app.post('/settings/user/delete/', follow_redirects=True)
        assert 'Your account was deleted.' in rv.data
        rv = self.login(username, password)
        assert 'Invalid username' in rv.data

if __name__ == '__main__':
    unittest.main()
