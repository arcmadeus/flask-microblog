import os

class Config:
    # Uses to protect against Cross-site Request Forgery
    SECRET_KEY = os.environ.get('SECRET_KEY') or "timados_unidos_united"