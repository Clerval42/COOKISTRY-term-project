from flask import Blueprint, render_template
from models import Recipe, Ingredient, RecipeIngredient
from sqlalchemy import func

lists_bp = Blueprint('lists', __name__)

@lists_bp.route('/lists')
def lists_page():
    # Helper: get top 5 recipes containing an ingredient category
    def get_top_recipes_by_ingredient_category(category):
        ingredient_ids = [i.IngredientID for i in Ingredient.query.filter_by(IngredientCategory=category).all()]
        if not ingredient_ids:
            return []
        recipe_ids = (
            RecipeIngredient.query
            .filter(RecipeIngredient.IngredientID.in_(ingredient_ids))
            .with_entities(RecipeIngredient.RecipeID)
            .distinct()
        )
        # Correct join: use Review model, not string
        from models import Review
        recipes = (
            Recipe.query
            .filter(Recipe.RecipeID.in_(recipe_ids))
            .outerjoin(Review, Review.RecipeID == Recipe.RecipeID)
            .group_by(Recipe.RecipeID)
            .order_by(func.count(Review.ReviewID).desc())
            .limit(5)
            .all()
        )
        return recipes
    # Get top 5 for each category
    meat_recipes = get_top_recipes_by_ingredient_category('Meat')
    bakery_recipes = get_top_recipes_by_ingredient_category('Bakery')
    pasta_noodles_recipes = get_top_recipes_by_ingredient_category('Pasta & Noodles')
    vegetable_recipes = get_top_recipes_by_ingredient_category('Vegetable')
    seafood_recipes = get_top_recipes_by_ingredient_category('Seafood')
    chicken_recipes = get_top_recipes_by_ingredient_category('Meat')
    return render_template(
        'lists.html',
        meat_recipes=meat_recipes,
        bakery_recipes=bakery_recipes,
        pasta_noodles_recipes=pasta_noodles_recipes,
        vegetable_recipes=vegetable_recipes,
        seafood_recipes=seafood_recipes,
        chicken_recipes=chicken_recipes
    )
