import sqlite3
import os
import random
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'agro_guard_2026_super_secret'

# Database Path
DB_PATH = os.path.join(os.path.dirname(__file__), 'users.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        hashed_pw = generate_password_hash(password)
        try:
            conn = get_db_connection()
            conn.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", 
                         (name, email, hashed_pw))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return "Email already registered! <a href='/register'>Try again</a>"
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = email
            return redirect(url_for('dashboard'))
        else:
            return "Invalid Login. <a href='/login'>Go back and try again.</a>"

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    sensors = {"temp": 28, "humidity": 88}
    risk = "High" if sensors['humidity'] > 85 else "Stable"
    alerts = [{"msg": "High Humidity detected.", "level": "Warning"}]
    
    return render_template('dashboard.html', name=session['user_name'], sensors=sensors, risk=risk, alerts=alerts)

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if 'user_id' not in session: 
        return redirect(url_for('login'))
        
    result = None
    if request.method == 'POST':
        crop_data = [
            {"crop": "Tomato", "disease": "Early Blight", "confidence": "94%", "remedy": "Remove infected leaves; apply Copper Fungicide."},
            {"crop": "Wheat", "disease": "Leaf Rust", "confidence": "91%", "remedy": "Apply Neem-based botanical formulation."},
            {"crop": "Corn", "disease": "Common Rust", "confidence": "89%", "remedy": "Improve field drainage and use sulfur dust."},
            {"crop": "Rice", "disease": "Blast Disease", "confidence": "96%", "remedy": "Avoid excessive Nitrogen; use biocontrol agents."},
            {"crop": "Potato", "disease": "Late Blight", "confidence": "92%", "remedy": "Ensure 10ft spacing; use organic fungicides."},
            {"crop": "Apple", "disease": "Apple Scab", "confidence": "88%", "remedy": "Prune affected branches and apply lime sulfur."},
            {"crop": "Grapes", "disease": "Powdery Mildew", "confidence": "95%", "remedy": "Increase sunlight exposure; use potassium bicarbonate."},
            {"crop": "Cotton", "disease": "Bollworm Infestation", "confidence": "97%", "remedy": "Deploy pheromone traps and botanical sprays."},
            {"crop": "Soybean", "disease": "Sudden Death Syndrome", "confidence": "85%", "remedy": "Rotate crops with corn; use resistant varieties."},
            {"crop": "Banana", "disease": "Sigatoka Leaf Spot", "confidence": "90%", "remedy": "Remove dead leaves; apply mineral oil sprays."}
        ]
        
        result = random.choice(crop_data)
        
    return render_template('predict.html', result=result)

@app.route('/profile')
def profile():
    if 'user_id' not in session: 
        return redirect(url_for('login'))
    return render_template('profile.html', name=session['user_name'], email=session.get('user_email', 'User'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)