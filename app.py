# Importt necessary modules
from flask import Flask, render_template, request, redirect, url_for, session, g
import pymysql
import hashlib
import os

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Database configuration
app.config['MYSQL_HOST'] = '192.168.40.13'
app.config['MYSQL_USER'] = 'quiz_user'
app.config['MYSQL_PASSWORD'] = 'quiz@123'
app.config['MYSQL_DB'] = 'quiz_app'

# Function to establish database connection
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = pymysql.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            db=app.config['MYSQL_DB'],
            cursorclass=pymysql.cursors.DictCursor
        )
    return db

# Function to close database connection
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Function to hash password
def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# Route for user registration
from flask import Flask, render_template, request, redirect, url_for, session, g, flash

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hash_password(password)

        try:
            connection = get_db()
            with connection.cursor() as cursor:
                sql = "INSERT INTO users (username, password) VALUES (%s, %s)"
                cursor.execute(sql, (username, hashed_password))
            connection.commit()
            flash('Registration successful! Please log in.', 'success') # Add flash message
            return redirect(url_for('login'))
        except Exception as e:
            return f"Registration failed: {str(e)}"
    return render_template('register.html')


# Route for user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hash_password(password)

        try:
            connection = get_db()
            with connection.cursor() as cursor:
                sql = "SELECT * FROM users WHERE username = %s AND password = %s"
                cursor.execute(sql, (username, hashed_password))
                user = cursor.fetchone()

            if user:
                session['username'] = username
                return redirect(url_for('show_categories'))
            else:
                return "Invalid username or password"

        except Exception as e:
            return f"Login failed: {str(e)}"

    return render_template('login.html')

# Route for user logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# Route to display quiz categories
@app.route('/')
def show_categories():
    try:
        if 'username' in session:
            connection = get_db()
            with connection.cursor() as cursor:
                sql = "SELECT id, name, description, image_url FROM categories"
                cursor.execute(sql)
                categories = cursor.fetchall()
            return render_template('categories.html', categories=categories)  # Pass categories to template
        else:
            return redirect(url_for('login'))
    except Exception as e:
        return f"Error: {str(e)}"

# Route for specific quiz category
@app.route('/quiz/<int:category_id>')
def category_quiz(category_id):
    if 'username' in session:
        try:
            connection = get_db()
            with connection.cursor() as cursor:
                sql = "SELECT * FROM questions WHERE category_id = %s"
                cursor.execute(sql, (category_id,))
                questions = cursor.fetchall()
            return render_template('quiz.html', title='Quiz', questions=questions)  # Pass questions to quiz.html
        except Exception as e:
            return f"Error: {str(e)}"
    else:
        return redirect(url_for('login'))

# Route for quiz submission
@app.route('/quiz', methods=['POST'])
def quiz():
    if 'username' in session:
        user_answers = {key: value for key, value in request.form.items()}
        score = calculate_score(user_answers)

        username = session['username']

        try:
            connection = get_db()
            with connection.cursor() as cursor:
                sql = "SELECT id FROM users WHERE username = %s"
                cursor.execute(sql, (username,))
                user = cursor.fetchone()
                user_id = user['id']

                sql = "INSERT INTO quiz_results (user_id, score) VALUES (%s, %s)"
                cursor.execute(sql, (user_id, score))
            connection.commit()

            return render_template('result.html', title='Quiz Result', score=score)
        except Exception as e:
            return f"Error: {e}"
    else:
        return redirect(url_for('login'))

# Function to calculate quiz score
def calculate_score(user_answers):
    score = 0
    try:
        connection = get_db()
        with connection.cursor() as cursor:
            sql = "SELECT * FROM questions"
            cursor.execute(sql)
            questions = cursor.fetchall()

        for question in questions:
            question_id = str(question['id'])
            if question_id in user_answers and user_answers[question_id] == question['correct_answer']:
                score += 1
    except Exception as e:
        return f"Error: {str(e)}"
    return score

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
