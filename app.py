from flask import Flask, render_template, request, redirect
from datetime import date
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

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method=='POST':
        firstname= request.form['first_name']
        lastname= request.form['last_name']
        password=request.form['password']
        email=request.form['email']
        height=request.form['height']
        birthdate=request.form['birthdate']

        conn=sqlite3.connect('trainer_app.db')
        conn.execute("INSERT INTO users (first_name, last_name, password, email, height, birthdate, role, registration_date) VALUES (?,?,?,?,?,?,?,?)" ,(firstname, lastname, password, email, height, birthdate, 'Client', date.today()))
        conn.commit()
        conn.close()
        return redirect('/login')
    elif request.method=='GET':
        return render_template("register.html")


@app.route('/trainer/dashboard')
def trainer_dashboard():
    return render_template("trainer_dash.html")

@app.route('/client/dashboard')
def client_dashboard():
    return render_template("client_dash.html")

if __name__ == '__main__':
    init_db()
    app.run(threaded=True, debug=True)
