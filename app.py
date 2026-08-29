from flask import Flask, render_template, request, redirect, session
from datetime import date
import sqlite3

def init_db():
    conn = sqlite3.connect('trainer_app.db') 
    with open('schema.sql') as f:
        s = f.read()
    conn.executescript(s)
    conn.close()

app = Flask(__name__)
app.secret_key = 'dev-key-change-later'

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='GET':
        return render_template("login.html")
    
    eemail=request.form['email']
    ppassword=request.form['password']

    conn=sqlite3.connect('trainer_app.db')
    check=conn.execute("SELECT password, user_id, role from users WHERE email = ?", (eemail,)).fetchone()
    conn.close()
    if check is None or ppassword!=check[0]:
        return render_template("login.html", error="Wrong Email or Password")
            
    session['user_id']=check[1]
    session['role']=check[2]

    if session['role']=='Client':
            return redirect('/client/dashboard')
    else:
            return redirect('/trainer/dashboard')

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
    if 'user_id' not in session:
        return redirect("/login")
    
    if session['role']=='Trainer': 
        return render_template("trainer_dash.html") 

    return redirect('/client/dashboard')

@app.route('/client/dashboard')
def client_dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    if session['role']=='Client':
        return render_template("client_dash.html") 

    return redirect("/trainer/dashboard")

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    init_db()
    app.run(threaded=True, debug=True)
