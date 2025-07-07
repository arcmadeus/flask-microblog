from flask import render_template
from app import app
from app.forms import LoginForm

# Importing routes (It handles different URLs)
@app.route('/') # Decorators are used as callbacks for certain events
@app.route('/index')
def index():
	user = {'username': 'Marco'}
	posts = [
		{
			'author': {'username': 'Yushin'},
			'body': 'Natimado na ako sa FOEC'
		},
		{
			'author': {'username': 'Carlos'},
			'body': 'Tamang set, pero hindi pupunta'
		},
	]

	return render_template('index.html', title='Home', user=user, posts=posts)

@app.route('/login')
def login():
	form = LoginForm()
	return render_template('login.html', title='Sign In', form=form)