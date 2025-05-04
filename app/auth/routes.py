from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import urlsplit
from app import db
from app.auth import bp
from app.models import User, ROLES
from app.auth.forms import LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        user = User.query.filter_by(username=data.get('username')).first()
        if user is None or not user.check_password(data.get('password')):
            if request.is_json:
                return jsonify({'message': 'Invalid username or password'}), 401
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
            
        login_user(user, remember=data.get('remember_me', False))
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('main.index')
            
        if request.is_json:
            return jsonify({'message': 'Login successful', 'redirect': next_page}), 200
        return redirect(next_page)
        
    return render_template('auth/login.html', title='Sign In')

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        # Check for existing user
        user = User.query.filter_by(username=data.get('username')).first()
        if user:
            if request.is_json:
                return jsonify({'message': 'Username already taken'}), 400
            flash('Username already taken')
            return redirect(url_for('auth.register'))
            
        user = User.query.filter_by(email=data.get('email')).first()
        if user:
            if request.is_json:
                return jsonify({'message': 'Email already registered'}), 400
            flash('Email already registered')
            return redirect(url_for('auth.register'))
        
        # Create new user
        user = User(
            username=data.get('username'),
            email=data.get('email'),
            role=data.get('role', ROLES['USER'])
        )
        user.set_password(data.get('password'))
        
        db.session.add(user)
        db.session.commit()
        
        if request.is_json:
            return jsonify({'message': 'Registration successful'}), 201
        flash('Registration successful! You can now log in.')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html', title='Register')

@bp.route('/profile', methods=['GET'])
@login_required
def profile():
    return render_template('auth/profile.html', title='Profile', user=current_user)

@bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    data = request.get_json() if request.is_json else request.form
    
    current_user.username = data.get('username', current_user.username)
    current_user.email = data.get('email', current_user.email)
    
    if data.get('password') and data.get('password') != '':
        current_user.set_password(data.get('password'))
    
    db.session.commit()
    
    if request.is_json:
        return jsonify({'message': 'Profile updated successfully'}), 200
    flash('Profile updated successfully')
    return redirect(url_for('auth.profile')) 