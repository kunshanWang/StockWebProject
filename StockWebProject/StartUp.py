from flask import Flask
from flask import request

# Create an instance of the Flask class that is the WSGI application.
# The first argument is the name of the application module or package,
# typically __name__ when using a single module.
app = Flask(__name__)

# Flask route decorators map / and /hello to the hello function.
# To add other resources, create functions that generate the page contents
# and add decorators to define the appropriate resource locators for them.

@app.route('/')
def index():
    user_agent = request.headers.get('User-Agent')
    return "<h1> your brwoser is %s </h1>" % user_agent

@app.route('/hello')
def hello():
    # Render the page
    return "Hello Python!"


@app.route('/user/<name>')
def user(name):
    return '<h1>hello, %s!</h1>' %name

if __name__ == '__main__':
    # Run the app server on localhost:4449
    app.run('localhost', 5000)