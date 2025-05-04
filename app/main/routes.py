from flask import render_template, redirect, url_for, request, jsonify, current_app
from flask_login import current_user, login_required
from app.main import bp

@bp.route('/')
@bp.route('/index')
def index():
    """Main landing page"""
    return render_template('index.html', title='EthicAI - Enterprise AI Responsibility Suite')

@bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard based on user role"""
    if current_user.role == 'admin':
        return render_template('admin/dashboard.html', title='Admin Dashboard')
    elif current_user.role == 'developer':
        return render_template('developer/dashboard.html', title='Developer Dashboard')
    elif current_user.role == 'manager':
        return render_template('manager/dashboard.html', title='Manager Dashboard')
    elif current_user.role == 'hr':
        return render_template('hr/dashboard.html', title='HR Dashboard')
    else:
        return render_template('user/dashboard.html', title='User Dashboard') 