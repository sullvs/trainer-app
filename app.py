from flask import Flask, render_template, request, redirect, session, abort
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import date
import sqlite3
import os
def init_db():
    conn = sqlite3.connect('trainer_app.db') 
    with open('schema.sql') as f:
        s = f.read()
    conn.executescript(s)
    conn.close()

app = Flask(__name__)
init_db()
app.secret_key = os.environ['SECRET_KEY']

@app.route('/')
def home():
    return render_template("home.html")

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/login')
        else: return f(*args, **kwargs)
    return wrapper

def role_required(role):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if session.get('role') == role:
                return f(*args, **kwargs)
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
    if check is None or not check_password_hash(check[0],ppassword):
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
        target_weight=request.form['target_weight']

        password_typed = generate_password_hash(password, method='pbkdf2:sha256')
        conn=sqlite3.connect('trainer_app.db')
        conn.execute("INSERT INTO users (first_name, last_name, password, email, height, birthdate, target_weight, role, registration_date) VALUES (?,?,?,?,?,?,?,?,?)" ,(firstname, lastname, password_typed, email, height, birthdate, target_weight, 'Client', date.today()))
        conn.commit()
        conn.close()
        return redirect('/login')
    elif request.method=='GET':
        return render_template("register.html")


@app.route('/trainer/dashboard')
@login_required
@role_required('Trainer')
def trainer_dashboard():
    conn=sqlite3.connect('trainer_app.db')
    tri_rows=conn.execute("SELECT first_name, last_name, user_id FROM users WHERE role='Client'").fetchall()
    conn.close()
    return render_template("trainer_dash.html", all_cli=tri_rows)

@app.route('/trainer/client/<client_id>')
@login_required
@role_required('Trainer')
def trainer_view_client(client_id):
    conn=sqlite3.connect("trainer_app.db")
    per_rows_users=conn.execute("SELECT height, target_weight FROM users WHERE user_id= ?", (client_id,)).fetchone()
    per_rows_food=conn.execute("SELECT meal_type, meal_content, log_time FROM food_log WHERE user_id = ?", (client_id,)).fetchall()
    per_rows_weight=conn.execute("SELECT current_weight, log_time FROM weight_log WHERE user_id= ?", (client_id,)).fetchall()
    conn.close()
    return render_template("one_client.html",one_cli_users=per_rows_users, one_cli_food=per_rows_food, one_cli_weight=per_rows_weight, client_id=client_id)

@app.route('/trainer/client/<client_id>/assign', methods=['POST','GET'])
@login_required
@role_required('Trainer')
def trainer_assign_splits(client_id):
    if request.method=='POST':
        num_of_dayss=request.form['num_of_days']
        suitable_workout_splitt=request.form['split']
        conn=sqlite3.connect("trainer_app.db")
        conn.execute("INSERT INTO workout (num_of_days, suitable_workout_split, log_time, user_id) VALUES (?, ?, ?, ?)", (num_of_dayss, suitable_workout_splitt, date.today(),client_id))
        conn.commit()
        conn.close()
        return redirect(f'/trainer/client/{client_id}')
    elif request.method=='GET':
        conn=sqlite3.connect("trainer_app.db")
        workout_val=conn.execute("SELECT num_of_days, suitable_workout_split, log_time FROM workout WHERE user_id = ?", (client_id,)).fetchall()
        conn.close()
        return render_template("assign.html", val=workout_val)


@app.route('/client/dashboard', methods=['POST','GET'])
@login_required
@role_required('Client')
def client_dashboard():
        if (request.method=='POST' and request.form['form_type']=="meals"):
            mmeal_type = request.form['meal_type']
            mmeal_content = request.form['meal_content']
            conn=sqlite3.connect('trainer_app.db')
            conn.execute("INSERT INTO food_log (user_id, meal_type, meal_content, log_time) VALUES (?,?,?,?)" , (session['user_id'], mmeal_type, mmeal_content, date.today()))
            conn.commit()
            conn.close()
            return redirect('/client/dashboard')
        elif (request.method=="POST" and request.form['form_type']=="weight"):
            cur_weight=request.form['current_weight']
            conn=sqlite3.connect('trainer_app.db')
            conn.execute("INSERT INTO weight_log (user_id, current_weight, log_time) VALUES (?,?,?)" , (session['user_id'], cur_weight, date.today()))
            conn.commit()
            conn.close()
            return redirect('/client/dashboard')
        elif request.method=='GET':
            conn=sqlite3.connect('trainer_app.db')
            m_rows=conn.execute('SELECT meal_type, meal_content, log_time FROM food_log  WHERE user_id = ?', (session['user_id'],)).fetchall()
            w_rows=conn.execute('SELECT current_weight, log_time FROM weight_log WHERE user_id = ?', (session['user_id'],)).fetchall()
            wr_rows=conn.execute('SELECT num_of_days, log_time FROM workout WHERE user_id = ?', (session['user_id'],)).fetchall()

            conn.close()
            return render_template("client_dash.html", meals=m_rows, weights=w_rows, workout=wr_rows) 

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    init_db()
    app.run(threaded=True, debug=True)
