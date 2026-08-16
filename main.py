from flask import Flask, render_template, request, session, redirect, url_for
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv

load_dotenv()

# initialize the flask app
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

def get_db_connection():
    timeout = 10
    return pymysql.connect(
    charset="utf8mb4",
    connect_timeout=timeout,
    cursorclass=pymysql.cursors.DictCursor,
    database=os.getenv("MYSQL_DATABASE"),
    host=os.getenv("MYSQL_HOST"),
    password=os.getenv("MYSQL_PASSWORD"),
    read_timeout=timeout,
    port=22390,
    user=os.getenv("MYSQL_USER"),
    write_timeout=timeout,
    )

# create table
def create_table():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""CREATE TABLE IF NOT EXISTS  login_details(
                                id INT AUTO_INCREMENT PRIMARY KEY,
                                username VARCHAR(100) NOT NULL UNIQUE,
                                email VARCHAR(255) NOT NULL UNIQUE,
                                password VARCHAR(255) NOT NULL,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
            connection.commit()
    finally:
        connection.close()
    
# routes
# home route
@app.route("/")
def home():
    return render_template("index.html")
    
# register route
@app.route("/register", methods=["GET", "POST"])
def register():
    msg = ''
    if request.method == "POST" and 'username' in request.form and 'email' in request.form and 'password' in request.form:
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if not username or not email or not password:
            msg = 'Please fill out all the details'
            return render_template('register.html', msg=msg)
        
        connection = get_db_connection()
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM login_details WHERE username=%s and email=%s", (username, email))
                account = cursor.fetchone()
                if account:
                    msg = 'Account already exists! Please login.'  
                    return render_template("register.html", msg=msg)
                else:
                    hashed_password = generate_password_hash(password)
                    cursor.execute(
                        "INSERT INTO login_details (username, email, password) VALUES (%s, %s, %s)",
                        (username, email, hashed_password)
                    )
                    connection.commit()
                    msg = "Registration successful!"

                    # Store username in session
                    session["username"] = username
                    return render_template("dashboard.html", username=username, msg=msg)  
        finally:
            connection.close()  
    return render_template("register.html")
    
# login route
@app.route("/login", methods=["GET", "POST"])
def login():
    msg = ''
    if request.method == "POST" and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        
        if not email or not password:
            msg = 'Please enter email and password'
            return render_template('login.html', msg=msg)
        
        connection = get_db_connection()
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM login_details WHERE email=%s", (email,))
                account = cursor.fetchone()
                
        finally:
            connection.close()
        
        if account and check_password_hash(account["password"], password):
            username = account["username"]
            msg = 'Logged in successfully'
            session['username'] = username
            print('Logged in successfully')
            return redirect(url_for("dashboard"))
        else:
            msg = 'Incorrect Credentials'
            return render_template('login.html', msg=msg)
    else:
        return render_template("login.html")
    
# dashboard route
@app.route("/dashboard")
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    return render_template("dashboard.html", username=session['username'])

# logout route
@app.route("/logout")
def logout():
    msg = 'Logged out successfully'

    # Remove username from session
    session.pop("username", None)
    return redirect(url_for('home'))

if __name__ == "__main__":
    create_table()
    app.run(debug=True)