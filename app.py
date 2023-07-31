from flask import Flask, render_template, request, url_for, redirect, session
import pymongo
import bcrypt
import json
import mysql.connector

app = Flask(__name__)
app.secret_key = "testing"
client = pymongo.MongoClient('mongodb+srv://teslasacademicgroup:oDELC6JXdmB8w84Q@cluster0.gvzgh2h.mongodb.net/?retryWrites=true&w=majority')
db = client.get_database('total_records')
records = db.register

config = {
  'host': 'gateway01.eu-central-1.prod.aws.tidbcloud.com',
  'port': 4000,
  'user': '4LqKgTg4CQHvYTu.demo_client',
  'password': 'avt5elBOHaOi8sgD',
  'database': 'demo',

}

@app.route('/fruit', methods=['GET'])
def rfid():
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM fruit')
    
    row_headers=[x[0] for x in cursor.description]
    myresult = cursor.fetchall()
    json_data=[]
    for result in myresult:
        json_data.append(dict(zip(row_headers,result)))
        
    # return json.dumps(json_data)
    return json.dumps(json_data)


# Route for the landing page
@app.route('/')
def landing():
    return render_template('landing.html')


@app.route("/register", methods=['POST', 'GET'])
def index():
    message = ''
    if "email" in session:
        return redirect(url_for("logged_in"))
    if request.method == "POST":
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        email = request.form.get("email")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        
        user_found = records.find_one({"name": firstname})
        email_found = records.find_one({"email": email})
        if user_found:
            message = 'There already is a user by that name'
            return render_template('index.html', message=message)
        if email_found:
            message = 'This email already exists in the database'
            return render_template('index.html', message=message)
        if password1 != password2:
            message = 'Passwords should match!'
            return render_template('index.html', message=message)
        else:
            hashed = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())
            user_input = {'firstname': firstname, 'lastname': lastname, 'email': email, 'password': hashed}
            records.insert_one(user_input)
            
            user_data = records.find_one({"email": email})
            new_email = user_data['email']
   
            return render_template('logged_in.html', firstname=firstname, email=new_email)
    return render_template('index.html')


@app.route('/logged_in')
def logged_in():
    if "email" in session:
        email = session["email"]
        return render_template('logged_in.html', email=email)
    else:
        return redirect(url_for("login"))
#end of code to run it

@app.route("/login", methods=["POST", "GET"])
def login():
    message = 'Please login to your account'
    if "email" in session:
        return redirect(url_for("logged_in"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

       
        email_found = records.find_one({"email": email})
        if email_found:
            email_val = email_found['email']
            passwordcheck = email_found['password']
            
            if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                session["email"] = email_val
                return redirect(url_for('logged_in'))
            else:
                if "email" in session:
                    return redirect(url_for("logged_in"))
                message = 'Wrong password'
                return render_template('login.html', message=message)
        else:
            message = 'Email not found'
            return render_template('login.html', message=message)
    return render_template('login.html', message=message)

@app.route("/logout", methods=["POST", "GET"])
def logout():
    if "email" in session:
        session.pop("email", None)
        return render_template("signout.html")
    else:
        return render_template('index.html')
    
    

    
if __name__ == "__main__":
  app.run(debug=True)
