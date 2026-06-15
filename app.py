from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "home page"

@app.route('/login')
def login():
    return "login page"

@app.route('/register')
def register():
    return "register page"

@app.route('/trainer/dashboard')
def trainer_dashboard():
    return "trainer page" 

@app.route('/client/dashboard')
def client_dashboard():
    return "client page"

if __name__ == '__main__':
    app.run(debug=True)