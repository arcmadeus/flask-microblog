import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Uses to protect against Cross-site Request Forgery
    SECRET_KEY = os.environ.get('SECRET_KEY') or "timados_unidos_united"
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')