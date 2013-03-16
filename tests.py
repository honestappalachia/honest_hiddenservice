#!/usr/bin/env python

import os
import unittest
import tempfile

from app import app, init_db

class DBTestCase(unittest.TestCase):

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
        
    def signup(self, username, password, confirm):
        return self.app.post('/signup', data=dict(
            username=username,
            password=password,
            confirm=confirm
        ), follow_redirects=True)
    
    def test_signup(self):
        username, password = 'guest', 'guest'
        rv = self.signup(username, password, password)
        assert 'Successfully signed up' in rv.data
        rv = self.signup(username, password, password)
        assert 'Username is already in use' in rv.data
        rv = self.signup('', password, password)
        assert 'This field is required' in rv.data
        rv = self.signup(username, '', '')
        assert 'This field is required' in rv.data
        rv = self.signup(username, password, password + 'x')
        assert 'Passwords must match' in rv.data
    
    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)
    
    def logout(self):
        return self.app.get('/logout', follow_redirects=True)
    
    def test_login_logout(self):
        username, password = 'guest', 'guest'
        rv = self.signup(username, password, password)
        rv = self.login(username, password)
        assert 'You were logged in' in rv.data
        rv = self.logout()
        assert 'You were logged out' in rv.data
        rv = self.login('guestx', password)
        assert 'Invalid username' in rv.data
        rv = self.login(username, 'guestx')
        assert 'Invalid password' in rv.data

if __name__ == '__main__':
    unittest.main()
