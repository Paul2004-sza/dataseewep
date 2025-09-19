from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

main_bp = Blueprint('main', __name__)

# Public landing page / showcase
@main_bp.route('/')
def landing():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))  # Logged-in users go straight to home
    return render_template('main/landing.html')

# User home/dashboard page (requires login)
@main_bp.route('/home')
@login_required
def home():
    return render_template('main/home.html')
