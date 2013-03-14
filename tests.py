#!/usr/bin/env python

import os
import unittest
import tempfile

from app import app, init_db

class DBTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        self.app = app.test_client()
        init_db()
        
    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])
        
if __name__ == '__main__':
    unittest.main()
