from flask import Flask

app = Flask(__name__) # Setting a name for this module

from app import routes # the app variable is an instance of Flask

