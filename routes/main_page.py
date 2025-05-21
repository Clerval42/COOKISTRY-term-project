from flask import Blueprint, render_template, jsonify
from models import Recipe, Review, User, MealPlan
from sqlalchemy import desc, func

main_page_bp = Blueprint('main_page', __name__)


@main_page_bp.route('/')
def main_page():
    # Most popular recipes (by review count)
    popular_recipes = (
        Recipe.query
        .outerjoin(Review, Review.RecipeID == Recipe.RecipeID)
        .group_by(Recipe.RecipeID)
        .order_by(func.count(Review.ReviewID).desc())
        .limit(10)
        .all()
    )
    # Most popular meals (MealPlan, by review count)
    popular_meals = (
        MealPlan.query
        .outerjoin(Review, Review.PlanID == MealPlan.PlanID)
        .group_by(MealPlan.PlanID)
        .order_by(func.count(Review.ReviewID).desc())
        .limit(10)
        .all()
    )
    # Most commented recipes
    most_commented = (
        Recipe.query
        .outerjoin(Review, Review.RecipeID == Recipe.RecipeID)
        .group_by(Recipe.RecipeID)
        .order_by(func.count(Review.Comment).desc())
        .limit(10)
        .all()
    )
    # Most active users (by review count)
    most_active_users = (
        User.query
        .outerjoin(Review, Review.UserID == User.UserID)
        .group_by(User.UserID)
        .order_by(func.count(Review.ReviewID).desc())
        .limit(10)
        .all()
    )
    # Most used ingredients (by recipe_ingredients count)
    from models import Ingredient, RecipeIngredient
    most_used_ingredients = (
        Ingredient.query
        .outerjoin(RecipeIngredient, RecipeIngredient.IngredientID == Ingredient.IngredientID)
        .group_by(Ingredient.IngredientID)
        .order_by(func.count(RecipeIngredient.RecipeID).desc())
        .limit(10)
        .all()
    )
    return render_template(
        'index.html',
        popular_recipes=popular_recipes,
        popular_meals=popular_meals,
        most_commented=most_commented,
        most_active_users=most_active_users,
        most_used_ingredients=most_used_ingredients
    )


@main_page_bp.route('/search_suggestions')
def search_suggestions():
    recipes = Recipe.query.with_entities(Recipe.RecipeID, Recipe.RecipeName).all()
    mealplans = MealPlan.query.with_entities(MealPlan.PlanID, MealPlan.PlanName).all()
    users = User.query.with_entities(User.UserID, User.UserName).all()
    return jsonify({
        'recipes': [{'id': r.RecipeID, 'name': r.RecipeName} for r in recipes],
        'mealplans': [{'id': m.PlanID, 'name': m.PlanName} for m in mealplans],
        'users': [{'id': u.UserID, 'name': u.UserName} for u in users]
    })
