from flask import render_template, flash, redirect, url_for
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

#GET requests information to the client, POST requests used to submit forms
@app.route('/login', methods=['GET', 'POST']) # Accepts both GET and POST request
def login():
	form = LoginForm()
	if form.validate_on_submit(): # Does all the form processing work
		flash('Login requested for user {}, remember_me={}'.format(form.username.data, form.remember_me.data)) # flash() function is a useful way to show a message to the user. 
		return redirect(url_for('index')) #Redirect the user to the index page of the application.
	return render_template('login.html', title='Sign In', form=form)