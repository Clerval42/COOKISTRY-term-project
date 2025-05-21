from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import Recipe, MealPlan, Review, db

meals_bp = Blueprint('meals', __name__)

@meals_bp.route('/meals')
def meals_page():
    # Get all unique meal categories from the MealPlan model's Enum
    meal_categories = [c for c in MealPlan.__table__.columns['PlanType'].type.enums]
    # Optionally, filter meals by category if requested
    meal_type = request.args.get('meal_type')
    if meal_type:
        # Redirect to the canonical category page for the selected meal type
        return redirect(url_for('meals.meal_category_page', category_name=meal_type))
    return render_template('meals.html', meal_categories=meal_categories, meals=[])

@meals_bp.route('/meals/category/<category_name>')
def meal_category_page(category_name):
    # Convert category_name from URL to display format (e.g., 'breakfast' -> 'Breakfast')
    display_category = category_name.replace('_', ' ').title()
    # Get all valid meal categories from the Enum
    meal_categories = [c for c in MealPlan.__table__.columns['PlanType'].type.enums]
    matched_category = next((c for c in meal_categories if c.lower().replace(' ', '_') == category_name.lower()), None)
    if not matched_category:
        return f"Category '{category_name}' not found.", 404
    # Find all MealPlans of this category
    mealplans = MealPlan.query.filter_by(PlanType=matched_category).all()
    return render_template('meal-category.html', category=matched_category, mealplans=mealplans)

@meals_bp.route('/meal-plan/<int:id>')
def meal_plan_detail(id):
    meal_plan = MealPlan.query.get(id)
    if not meal_plan:
        return 'Meal plan not found', 404
    # Optionally, fetch related recipes and reviews
    recipes = meal_plan.recipes if hasattr(meal_plan, 'recipes') else []
    reviews = meal_plan.reviews if hasattr(meal_plan, 'reviews') else []
    return render_template('meal-plan-detail.html', meal_plan=meal_plan, recipes=recipes, reviews=reviews)

@meals_bp.route('/meal-plan/<int:plan_id>/add-review', methods=['POST'])
def add_mealplan_review(plan_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login', next=request.url))
    meal_plan = MealPlan.query.get_or_404(plan_id)
    score = int(request.form.get('score', 0))
    comment = request.form.get('comment', '').strip()
    if not (1 <= score <= 5) or not comment:
        flash('Please provide a valid rating and comment.', 'danger')
        return redirect(request.referrer or url_for('meals.meal_plan_detail', id=plan_id))
    # Prevent duplicate review by same user for same meal plan
    existing = Review.query.filter_by(UserID=session['user_id'], PlanID=plan_id).first()
    if existing:
        flash('You have already reviewed this meal plan.', 'warning')
        return redirect(request.referrer or url_for('meals.meal_plan_detail', id=plan_id))
    review = Review(UserID=session['user_id'], PlanID=plan_id, Comment=comment, Score=score)
    db.session.add(review)
    db.session.commit()
    flash('Review submitted!', 'success')
    return redirect(request.referrer or url_for('meals.meal_plan_detail', id=plan_id))

@meals_bp.route('/meal-plan/<int:plan_id>/edit-review', methods=['POST'])
def edit_mealplan_review(plan_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login', next=request.url))
    meal_plan = MealPlan.query.get_or_404(plan_id)
    review = Review.query.filter_by(UserID=session['user_id'], PlanID=plan_id).first()
    if not review:
        flash('No review to edit.', 'danger')
        return redirect(request.referrer or url_for('meals.meal_plan_detail', id=plan_id))
    score = int(request.form.get('score', 0))
    comment = request.form.get('comment', '').strip()
    if not (1 <= score <= 5) or not comment:
        flash('Please provide a valid rating and comment.', 'danger')
        return redirect(request.referrer or url_for('meals.meal_plan_detail', id=plan_id))
    review.Score = score
    review.Comment = comment
    db.session.commit()
    flash('Review updated!', 'success')
    return redirect(request.referrer or url_for('meals.meal_plan_detail', id=plan_id))

@meals_bp.route('/delete-mealplan-review/<int:review_id>', methods=['POST'])
def delete_mealplan_review(review_id):
    review = Review.query.get_or_404(review_id)
    user_id = session.get('user_id')
    user_type = session.get('user_type')
    # Only allow if admin or owner
    if not user_id or (review.UserID != user_id and user_type != 'Admin'):
        flash('You are not authorized to delete this review.', 'danger')
        return redirect(url_for('profile.profile'))
    db.session.delete(review)
    db.session.commit()
    flash('Review deleted!', 'success')
    return redirect(url_for('profile.profile'))