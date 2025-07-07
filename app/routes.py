from flask import render_template
from app import app

# Importing routes (It handles different URLs)
@app.route('/') # Decorators are used as callbacks for certain events
@app.route('/index')
def index():
	user = {'username': 'Marco'}
	return render_template('index.html', title='Home', user=user)
