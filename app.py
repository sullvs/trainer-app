from flask import Flask, render_template
import sqlite3

def init_db():
    conn = sqlite3.connect('trainer_app.db') 
    with open('schema.sql') as f:
        s = f.read()
    conn.executescript(s)
    conn.close()

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/register')
def register():
    return render_template("register.html")

@app.route('/trainer/dashboard')
def trainer_dashboard():
    return render_template("trainer_dash.html")

@app.route('/client/dashboard')
def client_dashboard():
    return render_template("client_dash.html")

if __name__ == '__main__':
    init_db()
    app.run(threaded=True,debug=True)
