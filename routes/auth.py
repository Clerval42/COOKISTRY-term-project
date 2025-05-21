from flask import Blueprint, request, redirect, url_for, render_template, session, flash
from models import db, User
import hashlib
import datetime
from sqlalchemy.exc import IntegrityError
import os
from werkzeug.utils import secure_filename

auth_bp = Blueprint('auth', __name__)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('loginEmail')
        password = request.form.get('loginPassword')
        # Use form or args for next_url, fallback to main page
        next_url = request.form.get('next') or request.args.get('next') or url_for('main_page.main_page')
        user = User.query.filter_by(Email=email, PasswordHash=hash_password(password)).first()
        if user:
            session['user_id'] = user.UserID
            session['username'] = user.UserName
            session['user_type'] = user.UserType
            return redirect(next_url)
        else:
            return render_template('login.html', error='Invalid email or password.', next=next_url)
    # GET: show login/register page
    next_url = request.args.get('next')
    return render_template('login.html', next=next_url)

@auth_bp.route('/register', methods=['POST'])
def register():
    username = request.form.get('signupName')
    email = request.form.get('signupEmail')
    password = request.form.get('signupPassword')
    confirm_password = request.form.get('signupConfirmPassword')
    profile_picture = request.files.get('signupProfilePicture')
    if not username or not email or not password or not confirm_password:
        return render_template('login.html', error='All fields are required.')
    if password != confirm_password:
        return render_template('login.html', error='Passwords do not match.')
    try:
        # Check if email already exists
        existing_user = User.query.filter_by(Email=email).first()
        if existing_user:
            return render_template('login.html', error='Username or email already exists. Please log in.')
        # Handle profile picture upload
        profile_picture_path = 'uploads/users/default-user.jpg'
        if profile_picture and profile_picture.filename:
            uploads_dir = os.path.join('uploads', 'users')
            os.makedirs(uploads_dir, exist_ok=True)
            filename = secure_filename(profile_picture.filename)
            file_path = os.path.join(uploads_dir, filename)
            profile_picture.save(file_path)
            profile_picture_path = f'uploads/users/{filename}'
        # Actually create and add the user
        new_user = User(
            UserName=username,
            PasswordHash=hash_password(password),
            Email=email,
            UserType='User',
            RegistrationDate=datetime.datetime.now(),
            ProfilePicturePath=profile_picture_path
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.')
        return redirect(url_for('auth.login'))
    except Exception as e:
        db.session.rollback()
        return render_template('login.html', error='Registration failed: ' + str(e))

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main_page.main_page'))