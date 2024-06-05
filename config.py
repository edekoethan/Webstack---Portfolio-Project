import os

class Config:
    SECRET_KEY = os.urandom(24)
    SQLALCHEMY_DATABASE_URI = 'mysql://root:00781227.mYSQL@localhost/pharmacology'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
