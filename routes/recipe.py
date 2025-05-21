from flask import Blueprint, render_template, request, session, flash, url_for
from models import Recipe, Review, db
from werkzeug.utils import redirect
import re

def slugify(text):
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    return re.sub(r'[-\s]+', '-', text)

recipe_bp = Blueprint('recipe', __name__)

@recipe_bp.route('/recipes')
def recipe_list():
    # Get all unique categories from the Recipe model's Enum
    categories = [c for c in Recipe.__table__.columns['RecipeCategory'].type.enums]
    recipes = Recipe.query.all()
    return render_template('recipes.html', recipes=recipes, categories=categories)

@recipe_bp.route('/recipe/<name>-<int:recipe_id>')
def recipe_detail_name_id(name, recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    correct_name = slugify(recipe.RecipeName)
    if name != correct_name:
        return redirect(f'/recipe/{correct_name}-{recipe.RecipeID}')
    return render_template('recipe-detail.html', recipe=recipe)

@recipe_bp.route('/category/<category_name>')
def recipe_category(category_name):
    # Convert category_name from URL to display format (e.g., 'main_course' -> 'Main Course')
    display_category = category_name.replace('_', ' ').title()
    # Find the exact enum value (case-insensitive match)
    enum_categories = [c for c in Recipe.__table__.columns['RecipeCategory'].type.enums]
    matched_category = next((c for c in enum_categories if c.lower().replace(' ', '_') == category_name.lower()), None)
    if not matched_category:
        return f"Category '{category_name}' not found.", 404
    recipes = Recipe.query.filter_by(RecipeCategory=matched_category).all()
    return render_template('recipe-category.html', category=matched_category, recipes=recipes)

@recipe_bp.route('/recipe/<int:recipe_id>/add-review', methods=['POST'])
def add_recipe_review(recipe_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login', next=request.url))
    recipe = Recipe.query.get_or_404(recipe_id)
    score = int(request.form.get('score', 0))
    comment = request.form.get('comment', '').strip()
    if not (1 <= score <= 5) or not comment:
        flash('Please provide a valid rating and comment.', 'danger')
        return redirect(request.referrer or url_for('recipe.recipe_detail_name_id', name=slugify(recipe.RecipeName), recipe_id=recipe.RecipeID))
    # Prevent duplicate review by same user for same recipe
    existing = Review.query.filter_by(UserID=session['user_id'], RecipeID=recipe_id).first()
    if existing:
        flash('You have already reviewed this recipe.', 'warning')
        return redirect(request.referrer or url_for('recipe.recipe_detail_name_id', name=slugify(recipe.RecipeName), recipe_id=recipe.RecipeID))
    review = Review(UserID=session['user_id'], RecipeID=recipe_id, Comment=comment, Score=score)
    db.session.add(review)
    db.session.commit()
    flash('Review submitted!', 'success')
    return redirect(request.referrer or url_for('recipe.recipe_detail_name_id', name=slugify(recipe.RecipeName), recipe_id=recipe.RecipeID))

@recipe_bp.route('/recipe/<int:recipe_id>/edit-review', methods=['POST'])
def edit_recipe_review(recipe_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login', next=request.url))
    recipe = Recipe.query.get_or_404(recipe_id)
    review = Review.query.filter_by(UserID=session['user_id'], RecipeID=recipe_id).first()
    if not review:
        flash('No review to edit.', 'danger')
        return redirect(request.referrer or url_for('recipe.recipe_detail_name_id', name=slugify(recipe.RecipeName), recipe_id=recipe.RecipeID))
    score = int(request.form.get('score', 0))
    comment = request.form.get('comment', '').strip()
    if not (1 <= score <= 5) or not comment:
        flash('Please provide a valid rating and comment.', 'danger')
        return redirect(request.referrer or url_for('recipe.recipe_detail_name_id', name=slugify(recipe.RecipeName), recipe_id=recipe.RecipeID))
    review.Score = score
    review.Comment = comment
    db.session.commit()
    flash('Review updated!', 'success')
    return redirect(request.referrer or url_for('recipe.recipe_detail_name_id', name=slugify(recipe.RecipeName), recipe_id=recipe.RecipeID))

@recipe_bp.route('/review/<int:review_id>/delete', methods=['POST'])
def delete_recipe_review(review_id):
    if 'user_id' not in session:
        flash('You must be logged in to delete a review.', 'danger')
        return redirect(url_for('main_page.index'))
    review = Review.query.get_or_404(review_id)
    # Only allow if owner or admin
    user_id = session.get('user_id')
    user_type = session.get('user_type')
    if review.UserID != user_id and user_type != 'Admin':
        flash('You are not authorized to delete this review.', 'danger')
        return redirect(url_for('profile.profile'))
    db.session.delete(review)
    db.session.commit()
    flash('Review deleted!', 'success')
    return redirect(url_for('profile.profile'))
