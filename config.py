import os

class Config:
    SECRET_KEY = 'supersecretkey'
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysqlPass@localhost/recipesandmeals'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
