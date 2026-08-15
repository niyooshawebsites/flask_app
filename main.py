from flask import Flask, render_template

# initialize the flask app
app = Flask(__name__)

# routes
# home route
@app.route("/")
def home():
    return render_template("index.html")
    
# register route
@app.route("/register")
def register():
    return render_template("register.html")
    
# login route
@app.route("/login")
def login():
    return render_template("login.html")
    
# dashboard route
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

if __name__ == "__main__":
    app.run(debug=True)