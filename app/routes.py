from flask import render_template, flash, redirect, url_for, request
from app import app
from app.forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from app import db
from app.models import User
from urllib.parse import urlsplit

# Importing routes (It handles different URLs)
@app.route('/') # Decorators are used as callbacks for certain events
@app.route('/index')
@login_required
def index():
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

	return render_template('index.html', title='Home Page', posts=posts)

#GET requests information to the client, POST requests used to submit forms
@app.route('/login', methods=['GET', 'POST']) # Accepts both GET and POST request
def login():

	# Returns the user in the index page IF the account is logged in.
	if current_user.is_authenticated:
		return redirect(url_for('index'))

	form = LoginForm()
	if form.validate_on_submit(): # Does all the form processing work
		user = db.session.scalar( # Load the user from the database
			sa.select(User).where(User.username == form.username.data)
		) # Finding the user's username and since it will return 1 or 0, use SCALAR if it exists or not

		if user is None or not user.check_password(form.password.data): # Checks the password
			flash('Invalid username or password.')
			return redirect(url_for('login'))
		
		# Redirects the newly-logged in user to the index page.
		login_user(user, remember=form.remember_me.data)
		next_page = request.args.get('next')
		if not next_page or urlsplit(next_page).netloc != '':
			next_page = url_for('index')
		return redirect(next_page) #Redirect the user to the index page of the application.
	return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(username=form.username.data, email=form.email.data)
		user.set_password(form.password.data)
		db.session.add(user)
		db.session.commit()
		flash('Congratulations, you are now a registered user!')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)