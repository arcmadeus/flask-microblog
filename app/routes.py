from app import app

# Importing routes (It handles different URLs)
@app.route('/') # Decorators are used as callbacks for certain events
@app.route('/index')
def index():
  return "Hello, World!"