# import os
# import re
# from flask import Flask, render_template, request, redirect, url_for, session, flash
# from werkzeug.utils import secure_filename
# import mysql.connector
# from flask_hashing import Hashing
# from mysql.connector import connect, Error
# from datetime import datetime
# from app import app
# import connect as connect

# app.secret_key = os.getenv('e2e62cdb171271f0b12e5043f9f84208eba1f05c8658704e', 'default-key-for-dev')
# hashing = Hashing(app)

# connection = None

# def getCursor():
#     global connection
#     try:
#         if connection is None or not connection.is_connected():
#             connection = mysql.connector.connect(
#                 user=connect.dbuser,
#                 password=connect.dbpass,
#                 host=connect.dbhost,
#                 database=connect.dbname,
#                 autocommit=True
#             )
#             print("Connection successful")
#         return connection.cursor(buffered=True), connection
#     except mysql.connector.Error as e:
#         print("Error while connecting to MySQL", e)
#         return None, None

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

# @app.route("/")
# def home():
#     return render_template("index.html")


# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         username = request.form['username']
#         first_name = request.form['first_name']
#         last_name = request.form['last_name']
#         password = request.form['password']
#         email = request.form['email']
#         birth_date = request.form['date_of_birth']
#         location = request.form['location']
#         file = request.files['profile_image']
#         profile_image = None

#         cursor, conn = getCursor()
        
#         #  DD-MM-YYYY format
#         try:
#             birth_date_obj = datetime.strptime(birth_date, '%Y-%m-%d')
#             birth_date = birth_date_obj.strftime('%Y-%m-%d')
#         except ValueError:
#             flash('Invalid date format. Use YYYY-MM-DD', 'error')
#             return redirect(url_for('register'))


#         if not re.match(r'^[A-Za-z\s,]+$', location):
#             flash('Location must contain only letters, spaces, and commas.', 'error')
#             return redirect(url_for('register'))

#         if 'profile_image' not in request.files or file.filename == '':
#             profile_image = 'default.png'
#         elif file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#             profile_image = filename
#         else:
#             flash('File not allowed', 'error')
#             return redirect(url_for('register'))
        
#         cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
#         account = cursor.fetchone()
        
#         if account:
#             flash('Username already exists!', 'error')
#             return redirect(url_for('register'))
        
#         password_hash = hashing.hash_value(password, 'ExampleSaltValue')

#         cursor.execute("""
#             INSERT INTO users (username, first_name, last_name, email, password_hash, birth_date, location, profile_image)
#             VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
#         """, (username, first_name, last_name, email, password_hash, birth_date, location, profile_image))
#         conn.commit()

#         flash('Registration successful. Please login now.', 'success')
#         return redirect(url_for('login'))
    
#     return render_template("register.html")


# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
        
#         cursor, conn = getCursor()
#         cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
#         user = cursor.fetchone()

#         if user and hashing.check_value(user[5], password, 'ExampleSaltValue'):
#             session['user_id'] = user[0]
#             session['username'] = username
#             session['role'] = user[9]
#             flash('Login successful!', 'success')
#             return redirect(url_for('profile'))
#         else:
#             flash('Invalid username or password', 'error')

#     return render_template('login.html')

# @app.route('/logout')
# def logout():
#     session.clear()
#     flash('You have been logged out.', 'success')
#     return redirect(url_for('home'))

# @app.route('/profile', methods=['GET'])
# def profile():
#     if 'user_id' in session:
#         cursor, conn = getCursor()
#         cursor.execute("SELECT * FROM users WHERE user_id = %s", (session['user_id'],))
#         user = cursor.fetchone()
#         return render_template("profile.html", user=user)
#     return redirect(url_for('login'))

# @app.route('/edit_profile', methods=['GET', 'POST'])
# def edit_profile():
#     if 'user_id' in session:
#         cursor, conn = getCursor()
#         if request.method == 'POST':
#             email = request.form['email']
#             birth_date = request.form['date_of_birth']
#             location = request.form['location']
#             file = request.files['profile_image']
#             profile_image = None

#             if file and allowed_file(file.filename):
#                 filename = secure_filename(file.filename)
#                 file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#                 profile_image = filename

#             cursor.execute("""
#                 UPDATE users SET email = %s, birth_date = %s, location = %s, profile_image = %s WHERE user_id = %s
#             """, (email, birth_date, location, profile_image, session['user_id']))
#             conn.commit()
#             flash('Profile updated successfully!', 'success')
        
#         cursor.execute("SELECT * FROM users WHERE user_id = %s", (session['user_id'],))
#         user = cursor.fetchone()
#         return render_template('edit_profile.html', user=user)
#     return redirect(url_for('login'))

# @app.route('/community')
# def community():
#     if 'username' not in session:
#         return redirect(url_for('login'))

#     cursor, conn = getCursor()
#     cursor.execute("SELECT * FROM messages ORDER BY created_at DESC")
#     messages = cursor.fetchall()

#     return render_template('community.html', messages=messages)

# @app.route('/post_message', methods=['POST'])
# def post_message():
#     user_id = session['user_id']
#     text = request.form['message']

#     cursor, conn = getCursor()
#     cursor.execute("INSERT INTO messages (user_id, text) VALUES (%s, %s)", (user_id, text))
#     conn.commit()

#     return redirect(url_for('community'))

# @app.route('/admin_home')
# def admin_home():
#     if 'role' not in session or session['role'] != 'admin':
#         return redirect(url_for('login'))
#     return render_template('admin_home.html')

# @app.route('/moderator_home')
# def moderator_home():
#     if 'role' not in session or session['role'] != 'moderator':
#         return redirect(url_for('login'))
#     return render_template('moderator_home.html')

# if __name__ == '__main__':
#     app.run(debug=True, port=5001)