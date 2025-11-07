from flask import Flask, request, redirect, url_for, session, flash, render_template_string
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, os
app = Flask(__name__)
app.secret_key = "super_secret_key"
if not os.path.exists("users.db"):
    with sqlite3.connect("users.db") as conn:
        conn.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)
        conn.commit()

base_html = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{{ title }}</title>
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    * { box-sizing: border-box; }
    body {
        font-family: 'Inter', sans-serif;
        background: radial-gradient(circle at 20% 20%, #d7e1ec, #f8f9fb 70%);
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0;
    }
    .card {
        background: rgba(255, 255, 255, 0.25);
        backdrop-filter: blur(12px);
        border-radius: 20px;
        padding: 50px 40px;
        width: 340px;
        text-align: center;
        color: #222;
        box-shadow: 0 8px 40px rgba(0, 0, 0, 0.1);
        animation: floatIn 0.6s ease-out;
    }
    @keyframes floatIn {
        from { opacity: 0; transform: translateY(25px); }
        to { opacity: 1; transform: translateY(0); }
    }
    h2 {
        margin-bottom: 25px;
        color: #111;
        font-weight: 600;
    }
    input {
        width: 90%;
        padding: 12px;
        margin: 8px 0;
        border: 1px solid rgba(255,255,255,0.6);
        border-radius: 10px;
        outline: none;
        background: rgba(255,255,255,0.55);
        font-size: 14px;
        color: #222;
    }
    input::placeholder { color: #666; }
    button {
        background: linear-gradient(90deg, #007aff, #5ac8fa);
        border: none;
        border-radius: 10px;
        color: white;
        font-weight: 600;
        padding: 12px 25px;
        margin-top: 15px;
        cursor: pointer;
        transition: 0.25s;
        box-shadow: 0 3px 15px rgba(0,122,255,0.3);
    }
    button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(0,122,255,0.4);
    }
    a {
        display: inline-block;
        margin-top: 15px;
        color: #007aff;
        text-decoration: none;
        font-size: 14px;
    }
    a:hover { text-decoration: underline; }

    .toast {
        position: fixed;
        top: 20px;
        right: 20px;
        min-width: 220px;
        border-radius: 12px;
        padding: 12px 20px;
        color: #fff;
        font-weight: 500;
        backdrop-filter: blur(10px);
        box-shadow: 0 5px 25px rgba(0,0,0,0.2);
        animation: slideIn 0.4s ease-out, fadeOut 5s ease-in forwards;
    }
    .toast.success { background: rgba(76, 175, 80, 0.85); }
    .toast.error { background: rgba(244, 67, 54, 0.85); }
    .toast.info { background: rgba(33, 150, 243, 0.85); }
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(100%); }
        to { opacity: 1; transform: translateX(0); }
    }
    @keyframes fadeOut {
        0%, 85% { opacity: 1; }
        100% { opacity: 0; }
    }
</style>
</head>
<body>
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        {% for category, message in messages %}
          <div class="toast {{ category }}">{{ message }}</div>
        {% endfor %}
      {% endif %}
    {% endwith %}
    <div class="card">
        {{ content|safe }}
    </div>
</body>
</html>
"""
@app.route('/')
def home():
    content = """
    <h2>VaultX Authentication</h2>
    <p style='color:#555;'>A simple, secure & elegant login system.</p>
    <a href='/register'>Create an account</a> |
    <a href='/login'>Login</a>
    """
    return render_template_string(base_html, title="Home", content=content)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        if not username or not password:
            flash("⚠️ All fields are required!", "error")
            return redirect(url_for('register'))
        hashed_pw = generate_password_hash(password)
        try:
            with sqlite3.connect("users.db") as conn:
                conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
                conn.commit()
            flash("✅ Registration successful! Please log in.", "success")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("❌ Username already exists.", "error")
    content = """
    <h2>Create Account</h2>
    <form method='POST'>
        <input type='text' name='username' placeholder='Username'><br>
        <input type='password' name='password' placeholder='Password'><br>
        <button type='submit'>Register</button>
    </form>
    <a href='/login'>Already have an account?</a>
    """
    return render_template_string(base_html, title="Register", content=content)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        with sqlite3.connect("users.db") as conn:
            cur = conn.cursor()
            cur.execute("SELECT password FROM users WHERE username=?", (username,))
            row = cur.fetchone()
            if row and check_password_hash(row[0], password):
                session['user'] = username
                flash(f"🎉 Welcome, {username}!", "success")
                return redirect(url_for('dashboard'))
            else:
                flash("🚫 Invalid credentials. Try again!", "error")
                return redirect(url_for('login'))
    content = """
    <h2>Login</h2>
    <form method='POST'>
        <input type='text' name='username' placeholder='Username'><br>
        <input type='password' name='password' placeholder='Password'><br>
        <button type='submit'>Login</button>
    </form>
    <a href='/register'>New user? Register</a>
    """
    return render_template_string(base_html, title="Login", content=content)

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        flash("🔒 Please login first!", "error")
        return redirect(url_for('login'))
    user = session['user']
    content = f"""
    <h2>Welcome, {user} 👋</h2>
    <p style='color:#555;'>You’ve accessed a secure area of VaultX.</p>
    <form action='/logout' method='get'>
        <button type='submit'>Logout</button>
    </form>
    """
    return render_template_string(base_html, title="Dashboard", content=content)

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("👋 Logged out successfully!", "info")
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)
