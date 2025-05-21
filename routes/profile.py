from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from models import db, User, Recipe, MealPlan, Review

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile')
def profile():
    # Check if user is logged in (assuming user_id is stored in session)
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))

    user = User.query.get(user_id)
    if not user:
        return redirect(url_for('auth.login'))

    # Get user's recipes, meal plans, and reviews
    recipes = Recipe.query.filter_by(AddedByUserID=user_id).order_by(Recipe.RecipeDate.desc()).all()
    meal_plans = MealPlan.query.filter_by(UserID=user_id).order_by(MealPlan.PlanDate.desc()).all()
    reviews = Review.query.filter_by(UserID=user_id).order_by(Review.ReviewDate.desc()).all()

    # For base.html header
    is_logged_in = True
    logged_in_username = user.UserName  # Ensure this is correct

    return render_template(
        'profile.html',  # Use the correct template for the logged-in user
        user=user,
        recipes=recipes,
        meal_plans=meal_plans,
        reviews=reviews,
        is_logged_in=is_logged_in,
        logged_in_username=logged_in_username
    )

@profile_bp.route('/user-profile/<int:id>')
def user_profile(id):
    user = User.query.get(id)
    if not user:
        return redirect(url_for('auth.login'))
    recipes = Recipe.query.filter_by(AddedByUserID=id).order_by(Recipe.RecipeDate.desc()).all()
    meal_plans = MealPlan.query.filter_by(UserID=id).order_by(MealPlan.PlanDate.desc()).all()
    reviews = Review.query.filter_by(UserID=id).order_by(Review.ReviewDate.desc()).all()
    # If the logged-in user is visiting their own profile, redirect to /profile
    if 'user_id' in session and session['user_id'] == id:
        return redirect(url_for('profile.profile'))
    return render_template(
        'user-profile.html',
        user=user,
        user_recipes=recipes,
        user_mealplans=meal_plans,
        user_reviews=reviews
    )

@profile_bp.route('/admin/users', methods=['GET', 'POST'])
def admin_manage_users():
    if session.get('user_type') != 'Admin':
        return redirect(url_for('profile.profile'))
    from models import User
    users = User.query.all()
    if request.method == 'POST':
        user_id = int(request.form.get('user_id'))
        new_role = request.form.get('new_role')
        user = User.query.get(user_id)
        if user and new_role in ['User', 'Admin']:
            user.UserType = new_role
            db.session.commit()
            flash(f"Role for {user.UserName} updated to {new_role}.", 'success')
        return redirect(url_for('profile.admin_manage_users'))
    return render_template('admin-users.html', users=users)
