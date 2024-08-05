from flask import render_template, redirect, url_for, session
from app import views

@views.route('/staff/home')
def staff_home():
    if 'loggedin' in session and session['role'] == 'staff':
        return render_template('staff_home.html', username=session['username'], user_role=session['role'])
    return redirect(url_for('login'))



# from flask import render_template
# from flask import redirect
# from flask import url_for
# from flask import session
# from loginapp import app

# @app.route('/staff/home')
# def staff_home():
#     # Check if user is loggedin
#     if 'loggedin' in session:
#         # User is loggedin show them the home page
#         return render_template('staff_home.html', username=session['username'], user_role=session['role'])
    
#     # User is not loggedin redirect to login page
#     return redirect(url_for('login'))