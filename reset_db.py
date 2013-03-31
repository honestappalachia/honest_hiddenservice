#!/usr/bin/env python
import os
from settings import SQLALCHEMY_DATABASE_URI
db_path = SQLALCHEMY_DATABASE_URI[len('sqlite:///'):]
os.remove(db_path)
import app
app.init_db()
