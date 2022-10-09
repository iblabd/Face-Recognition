from flask import Flask, render_template, redirect, url_for, request, flash
from werkzeug.security import check_password_hash
from Users import User
from flask_login import login_user, logout_user, login_required
from __init__ import db


auth = Flask(__name__, template_folder='../resources/views')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method=='GET':
        return render_template('login.html')
    else:
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('Nama akun Anda tidak ada di database!')
        elif not check_password_hash(user.password, password):
            flash('Please check your login details and try again.')
            return redirect(url_for('auth.login'))
        login_user(user, remember=remember)
        return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

if __name__=='__main__':
    auth.run(debug=True)