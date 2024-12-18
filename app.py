import os
from dotenv import load_dotenv
import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, session

load_dotenv()
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Secret key for session management

# Load database configuration from environment variables
db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

# Initialize the database connection
def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            connection.commit()
            cursor.close()
            connection.close()
            message = "Registration successful"
        except mysql.connector.Error as err:
            message = f"Error: {err}"

    return render_template('register.html', message=message)

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    print('enetered')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
            user = cursor.fetchone()
            cursor.close()
            connection.close()

            if user:
                session['username'] = username
                return redirect(url_for('math_operations'))
            else:
                message = "Invalid username or password."
        except mysql.connector.Error as err:
            message = f"Error: {err}"

    return render_template('login.html', message=message)

@app.route('/math', methods=['GET', 'POST'])
def math_operations():
    if 'username' not in session:
        return redirect(url_for('login'))

    result = None
    if request.method == 'POST':
        try:
            username = session['username']
            num1 = float(request.form.get('num1', 0))
            num2 = float(request.form.get('num2', 0))
            operation = request.form.get('operation')

            if operation == 'add':
                result = num1 + num2
            elif operation == 'sub':
                result = num1 - num2
            elif operation == 'multiply':
                result = num1 * num2
            elif operation == 'cube':
                result = f"cube of {num1}: {num1**3}, cube of {num2}: {num2**3}"

            # Insert data into the database
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO user_logs (user_name, number1, number2, result)
                VALUES (%s, %s, %s, %s)
            """, (username, num1, num2, result))
            connection.commit()
            cursor.close()
            connection.close()

        except ValueError:
            result = "Invalid input, please enter valid numbers."
        except mysql.connector.Error as err:
            result = f"Error inserting into database: {err}"

    return render_template('math.html', result=result, username=session['username'])


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)


