from flask import Flask, render_template, request, redirect, session, abort
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import date
from dotenv import load_dotenv
#import sqlite3
import psycopg2
import os

load_dotenv()

def get_db():
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    return conn

def init_db():
    conn = get_db()
    with open('schema.sql') as f:
        s = f.read()
    cur = conn.cursor()
    cur.execute(s)
    conn.commit()
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

    conn=get_db()
    cur = conn.cursor()
    cur.execute("SELECT password, user_id, role from users WHERE email = %s", (eemail,))
    check = cur.fetchone()
    print("DEBUG check =", check)   # <-- temporary
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
        conn=get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (first_name, last_name, password, email, height, birthdate, target_weight, role, registration_date) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)" ,(firstname, lastname, password_typed, email, height, birthdate, target_weight, 'Client', date.today()))
        conn.commit()
        conn.close()
        return redirect('/login')
    elif request.method=='GET':
        return render_template("register.html")


@app.route('/trainer/dashboard')
@login_required
@role_required('Trainer')
def trainer_dashboard():
    conn=get_db()
    cur = conn.cursor()
    cur.execute("SELECT first_name, last_name, user_id FROM users WHERE role='Client'")
    tri_rows = cur.fetchall()
    conn.close()
    return render_template("trainer_dash.html", all_cli=tri_rows)

@app.route('/trainer/client/<client_id>')
@login_required
@role_required('Trainer')
def trainer_view_client(client_id):
    conn=get_db()
    cur = conn.cursor()
    cur.execute("SELECT height, target_weight FROM users WHERE user_id= %s", (client_id,))
    per_rows_users = cur.fetchone()
    cur.execute("SELECT meal_type, meal_content, log_time FROM food_log WHERE user_id = %s", (client_id,))
    per_rows_food= cur.fetchall()
    cur.execute("SELECT current_weight, log_time FROM weight_log WHERE user_id= %s", (client_id,))
    per_rows_weight=cur.fetchall()
    conn.close()
    return render_template("one_client.html",one_cli_users=per_rows_users, one_cli_food=per_rows_food, one_cli_weight=per_rows_weight, client_id=client_id)

@app.route('/trainer/client/<client_id>/assign', methods=['POST','GET'])
@login_required
@role_required('Trainer')
def trainer_assign_splits(client_id):
    if request.method=='POST':
        num_of_dayss=request.form['num_of_days']
        suitable_workout_splitt=request.form['split']
        conn=get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO workout (num_of_days, suitable_workout_split, log_time, user_id) VALUES (%s, %s, %s, %s)", (num_of_dayss, suitable_workout_splitt, date.today(),client_id))
        conn.commit()
        conn.close()
        return redirect(f'/trainer/client/{client_id}/assign')
    elif request.method=='GET':
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT num_of_days, suitable_workout_split, log_time FROM workout WHERE user_id = %s", (client_id,))
        workout_val=cur.fetchall()
        conn.close()
        return render_template("assign.html", val=workout_val, client_id=client_id)


@app.route('/client/dashboard', methods=['POST','GET'])
@login_required
@role_required('Client')
def client_dashboard():
        if (request.method=='POST' and request.form['form_type']=="meals"):
            mmeal_type = request.form['meal_type']
            mmeal_content = request.form['meal_content']
            conn = get_db()
            cur = conn.cursor()
            cur.execute("INSERT INTO food_log (user_id, meal_type, meal_content, log_time) VALUES (%s,%s,%s,%s)" , (session['user_id'], mmeal_type, mmeal_content, date.today()))
            conn.commit()
            conn.close()
            return redirect('/client/dashboard')
        elif (request.method=="POST" and request.form['form_type']=="weight"):
            cur_weight=request.form['current_weight']
            conn = get_db()
            cur = conn.cursor()
            cur.execute("INSERT INTO weight_log (user_id, current_weight, log_time) VALUES (%s,%s,%s)" , (session['user_id'], cur_weight, date.today()))
            conn.commit()
            conn.close()
            return redirect('/client/dashboard')
        elif request.method=='GET':
            conn = get_db()
            cur = conn.cursor()
            cur.execute('SELECT meal_type, meal_content, log_time FROM food_log  WHERE user_id = %s', (session['user_id'],))
            m_rows=cur.fetchall()
            cur.execute('SELECT current_weight, log_time FROM weight_log WHERE user_id = %s', (session['user_id'],))
            w_rows=cur.fetchall()
            cur.execute('SELECT num_of_days, log_time FROM workout WHERE user_id = %s', (session['user_id'],))
            wr_rows=cur.fetchall()

            conn.close()
            return render_template("client_dash.html", meals=m_rows, weights=w_rows, workout=wr_rows) 

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    init_db()
    app.run(threaded=True, debug=True)
