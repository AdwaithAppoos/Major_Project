from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import pickle
import pandas as pd
import numpy as np
import joblib
scaler = joblib.load("C:/Users/adwai/OneDrive/Desktop/Water Quality Classification Main Project/Project Development/my_scaler.save")
model=pickle.load(open('C:/Users/adwai/OneDrive/Desktop/Water Quality Classification Main Project/Project Development/model.pkl','rb'))
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

conn = sqlite3.connect('user_data.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
             name TEXT NOT NULL,
             security_key TEXT NOT NULL,
             password TEXT NOT NULL);''')
conn.commit()
conn.close()

conn = sqlite3.connect('user_data.db')
c = conn.cursor()
# Create a table
c.execute('''CREATE TABLE IF NOT EXISTS water_quality_data (
    row_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ph REAL,
    Hardness REAL,
    Solids REAL,
    Chloramines REAL,
    Sulfate REAL,
    Conductivity REAL,
    Organic_carbon REAL,
    Trihalomethanes REAL,
    Turbidity REAL,
    Result REAL
)''')
conn.commit()
conn.close()

def insert_data(ph, Hardness, Solids, Chloramines, Sulfate, Conductivity, Organic_carbon, Trihalomethanes, Turbidity, Result):
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute("SELECT * FROM water_quality_data WHERE ph=? AND Hardness=? AND Solids=? AND Chloramines=? AND Sulfate=? AND Conductivity=? AND Organic_carbon=? AND Trihalomethanes=? AND Turbidity=? AND Result=?", (ph, Hardness, Solids, Chloramines, Sulfate, Conductivity, Organic_carbon, Trihalomethanes, Turbidity, Result))
    data = c.fetchone()
    if data is None:
        c.execute('''INSERT INTO water_quality_data (ph, Hardness, Solids, Chloramines, Sulfate, Conductivity, Organic_carbon, Trihalomethanes, Turbidity, Result) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (ph, Hardness, Solids, Chloramines, Sulfate, Conductivity, Organic_carbon, Trihalomethanes, Turbidity, Result))
        conn.commit()
    conn.close()

@app.route('/log', methods=['POST'])
def log_data():
    ph = request.form['ph']
    Hardness = request.form['Hardness']
    Solids = request.form['Solids']
    Chloramines = request.form['Chloramines']
    Sulfate = request.form['Sulfate']
    Conductivity = request.form['Conductivity']
    Organic_carbon = request.form['Organic_carbon']
    Trihalomethanes = request.form['Trihalomethanes']
    Turbidity = request.form['Turbidity']
    Result = request.form['Result']

    # Check if the data already exists in the database
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM water_quality_data WHERE ph=? AND Hardness=? AND Solids=? AND Chloramines=? AND Sulfate=? AND Conductivity=? AND Organic_carbon=? AND Trihalomethanes=? AND Turbidity=? AND Result=?", (ph, Hardness, Solids, Chloramines, Sulfate, Conductivity, Organic_carbon, Trihalomethanes, Turbidity, Result))
    rows = cursor.fetchall()

    if len(rows) > 0:
        # Data already exists, do not insert into the database
        conn.close()
        return redirect(url_for('log_page'))

    # Insert the data and Result into the database
    cursor.execute("INSERT INTO water_quality_data (ph, Hardness, Solids, Chloramines, Sulfate, Conductivity, Organic_carbon, Trihalomethanes, Turbidity, Result) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                   (ph, Hardness, Solids, Chloramines, Sulfate, Conductivity, Organic_carbon, Trihalomethanes, Turbidity, Result))
    conn.commit()
    conn.close()

    # Redirect to the log page
    return redirect(url_for('log_page'))

@app.route('/log')
def log_page():
    # Retrieve all the user data from the database
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM water_quality_data")
    rows = cursor.fetchall()
    conn.close()

    # Render the log page with the user data
    return render_template('log.html', rows=rows)

@app.route('/delete/<int:row_id>', methods=['DELETE'])
def delete_row(row_id):
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute("DELETE FROM water_quality_data WHERE row_id=?", (row_id,))
    conn.commit()
    conn.close()
    return "Record deleted successfully"

@app.route("/")
def home():
    return render_template('Main.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    user_count = c.fetchone()[0]
    conn.close()

    if user_count > 0:
        return "<script>alert('Error: Only one user can register'); window.location.replace('/login');</script>"

    if request.method == 'POST':
        # Get the form data from the request object
        name = request.form['name']
        security_key = request.form['security-key']
        password = request.form['password']

        # Insert the user data into the database
        conn = sqlite3.connect('user_data.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (name, security_key, password) VALUES (?, ?, ?)",
                  (name, security_key, password))
        conn.commit()
        conn.close()

        return "<script>alert('Registration Successful'); window.location.replace('/login');</script>"

    # Render the registration form template for GET requests
    return render_template('Registration.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        lpassword = request.form.get('password')
        conn = sqlite3.connect('user_data.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE name = ? AND password = ?', (username, lpassword))
        user = c.fetchone()

        if user is None:
            conn.close()
            return "<script>alert('Invalid Credentials. Please try again.'); window.location.replace('/login');</script>"
        else:
            conn.close()
            return "<script>alert('Login Successful'); window.location.replace('/predict');</script>"

    return render_template('Login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    if request.method == 'POST':
        security_key = request.form['security-key']
        # Connect to database
        conn = sqlite3.connect('user_data.db')
        c = conn.cursor()
        # Check if security key exists in database
        c.execute('SELECT * FROM users WHERE security_key=?', (security_key,))
        user = c.fetchone()
        if user is None:
            conn.close()
            return "<script>alert('Entered Security key is Incorrect'); window.location.replace('/forgot');</script>"
        else:
            session['security_key'] = security_key
            conn.close()
            return redirect('/reset')
        
    return render_template('Forgot.html')    
   
@app.route('/reset', methods=['GET', 'POST'])
def reset():
    if request.method == 'POST':
        security_key = session['security_key']
        new_password = request.form['new-password']
        confirm_password = request.form['confirm-password']
        if new_password != confirm_password:
            return "<script>alert('Passwords do not match'); window.location.replace('/reset');</script>"
        # Update user's password in the database
        conn = sqlite3.connect('user_data.db')
        c = conn.cursor()
        c.execute('UPDATE users SET password=? WHERE security_key=?', (new_password, session['security_key']))
        conn.commit()
        conn.close()
        session.pop('security_key', None)
        return "<script>alert('Password successfully reset'); window.location.replace('/login');</script>"
    else:
        return render_template('Reset.html')
    
@app.route('/info')
def info():
    return render_template('Info.html')

@app.route("/predict", methods = ["GET", "POST"])
def predict():
    if request.method == "POST":
        input_features = [float(x) for x in request.form.values()]
        features_value = [np.array(input_features)]

        feature_names = ["ph", "Hardness" , "Solids", "Chloramines", "Sulfate",
                         "Conductivity", "Organic_carbon","Trihalomethanes", "Turbidity"]

        df = pd.DataFrame(features_value, columns = feature_names)
        df = scaler.transform(df)
        output = model.predict(df)

        if output[0] == 1:           
            prediction = "safe"
        else:
            prediction = "not safe"

        Result = prediction

        insert_data(input_features[0], input_features[1], input_features[2], input_features[3], input_features[4], input_features[5], input_features[6], input_features[7], input_features[8], Result)

        return render_template('predict.html', prediction_text= "water is {} for human consumption ".format(prediction))
    
    return render_template('predict.html')    

if __name__ == "__main__":
    app.run(debug=True)