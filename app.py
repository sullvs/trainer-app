from flask import Flask, render_template, request, redirect, session, abort
from functools import wraps
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

def login_required(f):
    @wraps(f)
    def wrapper():
        if 'user_id' not in session:
            return redirect('/login')
        else: return f()
    return wrapper

def role_required(role):
    def decorator(f):
        @wraps(f)
        def wrapper():
            if session.get('role') == role:
                return f()
            else:
                abort(403)
        return wrapper
    return decorator


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
@login_required
@role_required('Trainer')
def trainer_dashboard():
    return render_template("trainer_dash.html")

@app.route('/client/dashboard', methods=['POST','GET'])
@login_required
@role_required('Client')
def client_dashboard():
        if request.method=='POST':
            mmeal_type = request.form['meal_type']
            mmeal_content = request.form['meal_content']
            conn=sqlite3.connect('trainer_app.db')
            conn.execute("INSERT INTO food_log (user_id, meal_type, meal_content, log_time) VALUES (?,?,?,?)" , (session['user_id'], mmeal_type, mmeal_content, date.today()))
            conn.commit()
            conn.close()
            return redirect('/client/dashboard')
        elif request.method=='GET':
            conn=sqlite3.connect('trainer_app.db')
            rows=conn.execute('SELECT meal_type, meal_content, log_time FROM food_log  WHERE user_id = ?', (session['user_id'],)).fetchall()
            conn.commit()
            conn.close()
            return render_template("client_dash.html", meals=rows) 

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    init_db()
    app.run(threaded=True, debug=True)
