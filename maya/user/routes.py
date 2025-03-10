
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, current_user, logout_user

from maya import app, config, db, bcrypt
from maya.user.forms import RegisterForm, LoginForm
from maya.user.models import Register


@app.route('/register', methods=['GET','POST'])
def register():

    if current_user.is_authenticated:
        # Code for authenticated users
        next = request.args.get('next')
        return redirect(next or url_for('home'))

    form = RegisterForm()
    if form.validate_on_submit():
        hash_password = bcrypt.generate_password_hash(form.password.data)
        register = Register(name=form.name.data, email=form.email.data, password=hash_password  )
        db.session.add(register)
        flash(f'Welcome {form.name.data}, Thank you for register ', 'success')
        db.session.commit()
        return redirect(url_for('login'))

        print(form.name.data)
    return render_template('user/register.html',
                           title=config.get("APP_NAME" , "Register"),form=form )


@app.route('/login', methods=['GET','POST'])
def login():

    if current_user.is_authenticated:
        # Code for authenticated users
        next = request.args.get('next')
        return redirect(next or url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = Register.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('You are login ', 'success')
            next = request.args.get('next')
            return redirect(next or url_for('home'))
        flash('incorrect email and password ','danger')
        return redirect(url_for('login'))

    return render_template('user/login.html',
                           title=config.get("APP_NAME" , "login"),form=form )


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))
