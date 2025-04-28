import os
import sqlite3
import pickle
import random
import hashlib
import subprocess
import requests
import xml.etree.ElementTree as ET
from flask import Flask, request, render_template_string, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'supersecretkey'

def connect_to_database():
    conn = sqlite3.connect('app.db')
    return conn

def execute_db_query(conn, query, params=()):
    cursor = conn.cursor()
    cursor.execute(query, params)
    return cursor.fetchall()

def initialize_database():
    conn = connect_to_database()
    conn.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, bio TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS files (id INTEGER PRIMARY KEY, filename TEXT, content BLOB)')
    conn.commit()
    conn.close()

@app.route('/')
def home_page():
    return "<h1>Welcome to the SecureApp</h1><p><a href='/login'>Login</a> | <a href='/register'>Register</a></p>"

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        bio = request.form['bio']
        conn = connect_to_database()
        conn.execute('INSERT INTO users (username, password, bio) VALUES (?, ?, ?)', (username, hash_user_password(password), bio))
        conn.commit()
        conn.close()
        return redirect(url_for('login_user'))
    return render_template_string('''
        <form method="post">
            Username: <input type="text" name="username"><br>
            Password: <input type="password" name="password"><br>
            Bio: <textarea name="bio"></textarea><br>
            <input type="submit" value="Register">
        </form>
    ''')

@app.route('/login', methods=['GET', 'POST'])
def login_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if check_credentials(username, password):
            session['username'] = username
            return redirect(url_for('view_profile', username=username))
        else:
            return "Login Failed"
    return render_template_string('''
        <form method="post">
            Username: <input type="text" name="username"><br>
            Password: <input type="password" name="password"><br>
            <input type="submit" value="Login">
        </form>
    ''')

@app.route('/profile/<username>', methods=['GET'])
def view_profile(username):
    conn = connect_to_database()
    user_data = execute_db_query(conn, "SELECT * FROM users WHERE username = ?", (username,))
    conn.close()
    if user_data:
        return render_template_string('''
            <h1>{{ user[1] }}'s Profile</h1>
            <p>{{ user[3] }}</p>
            <a href="/">Home</a> | <a href="/upload">Upload File</a>
        ''', user=user_data[0])
    else:
        return "User not found"

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        filename = file.filename
        content = file.read()
        conn = connect_to_database()
        conn.execute('INSERT INTO files (filename, content) VALUES (?, ?)', (filename, content))
        conn.commit()
        conn.close()
        return "File uploaded successfully"
    return render_template_string('''
        <form method="post" enctype="multipart/form-data">
            <input type="file" name="file"><br>
            <input type="submit" value="Upload">
        </form>
    ''')

@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    if request.method == 'POST':
        admin_input = request.form['input']
        result = execute_admin_command(admin_input)
        return result
    return render_template_string('''
        <form method="post">
            Admin Input: <input type="text" name="input"><br>
            <input type="submit" value="Execute">
        </form>
    ''')

@app.route('/external', methods=['GET'])
def external_fetch():
    url = request.args.get('url')
    content = fetch_external_content(url)
    return content

@app.route('/greet', methods=['GET'])
def greet_user():
    name = request.args.get('name')
    template = f"<h1>Hello, {name}!</h1>"
    return render_template_string(template)

@app.route('/xml', methods=['POST'])
def xml_endpoint():
    xml_data = request.data
    try:
        tree = ET.ElementTree(ET.fromstring(xml_data))
        root = tree.getroot()
        response = f"Root element: {root.tag}"
    except ET.ParseError:
        response = "Invalid XML"
    return response

@app.route('/process', methods=['POST'])
def process_data():
    serialized_data = request.form['data']
    data = unserialize_data(serialized_data)
    return f"Processed data: {data}"

def execute_admin_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout

def unserialize_data(serialized_data):
    return pickle.loads(serialized_data)

def get_random_value():
    return random.randint(0, 100)

def read_system_file(filepath):
    with open(filepath, 'r') as file:
        return file.read()

def hash_user_password(password):
    return hashlib.md5(password.encode()).hexdigest()

def check_credentials(username, password):
    conn = connect_to_database()
    user = execute_db_query(conn, "SELECT * FROM users WHERE username = ?", (username,))
    conn.close()
    if user and hash_user_password(password) == user[0][2]:
        return True
    return False

def fetch_external_content(url):
    response = requests.get(url)
    return response.text

if __name__ == "__main__":
    initialize_database()
    app.run(debug=True)


