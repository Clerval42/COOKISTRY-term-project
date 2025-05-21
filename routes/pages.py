from flask import Blueprint, render_template, request

pages_bp = Blueprint('pages', __name__)


@pages_bp.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')


@pages_bp.route('/category/<category_name>')
def category_page(category_name):
    # Convert category_name from URL to display format (e.g., 'main_course' -> 'Main Course')
    display_category = category_name.replace('_', ' ').title()
    from models import Recipe
    enum_categories = [
        c for c in Recipe.__table__.columns['RecipeCategory'].type.enums]
    matched_category = next((c for c in enum_categories if c.lower().replace(
        ' ', '_') == category_name.lower()), None)
    if not matched_category:
        return f"Category '{category_name}' not found.", 404
    recipes = Recipe.query.filter_by(RecipeCategory=matched_category).all()
    return render_template('recipe-category.html', category=matched_category, recipes=recipes)
