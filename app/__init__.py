from flask import Flask
from config import Config

app = Flask(__name__) # Setting a name for this module
app.config.from_object(Config)

from app import routes # the app variable is an instance of Flask

