from flask import Flask, render_template, request, session, redirect, url_for
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv

load_dotenv()

# initialize the flask app
app = Flask(__name__)

# helper function for DB connection
def get_db_connection():
    return mysql.connector.connect(
    host=os.getenv("MYSQL_HOST"),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database=os.getenv("MYSQL_DATABASE")
    )

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
        
        myDB = get_db_connection()
        mycursor = myDB.cursor()
        
        mycursor.execute("SELECT * FROM LoginDetails WHERE username=%s and email=%s", (username, email))
        account = mycursor.fetchone()
        
        if account:
            msg = 'Account already exists! Please login.'
            mycursor.close()
            myDB.close()
            
            return render_template("register.html", msg=msg)
        else:
            hashed_password = generate_password_hash(password)
            mycursor.execute(
                "INSERT INTO LoginDetails (username, email, password) VALUES (%s, %s, %s)",
                (username, email, hashed_password)
            )
            myDB.commit()
            mycursor.close()
            myDB.close()

            msg = "Registration successful!"

            # Store username in session
            session["username"] = username
            return render_template("dashboard.html", username=username, msg=msg)
        
    return render_template("register.html")
    
# login route
@app.route("/login", methods=["GET", "POST"])
def login():
    msg = ''
    if request.method == "POST" and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        
        myDB = get_db_connection()
        mycursor = myDB.cursor()
        mycursor.execute("SELECT * FROM LoginDetails WHERE email=%s", (email))
        account = mycursor.fetchone()
        
        mycursor.close()
        myDB.close()
        
        if account and check_password_hash(account[3], password):
            username = account[1]
            msg = 'Logged in successfully'
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
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)