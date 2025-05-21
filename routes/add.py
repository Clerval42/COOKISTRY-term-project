from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Recipe, Ingredient, MealPlan
from datetime import datetime

add_bp = Blueprint('add', __name__)

@add_bp.route('/add-recipe', methods=['GET', 'POST'])
def add_recipe():
    if 'user_id' not in session:
        return redirect(url_for('auth.login', next=request.url))
    # Fetch all ingredients and categories from DB
    ingredients = Ingredient.query.order_by(Ingredient.IngredientName).all()
    # Serialize ingredients to dicts for JSON
    ingredients_serialized = [
        {"IngredientID": ing.IngredientID, "IngredientName": ing.IngredientName}
        for ing in ingredients
    ]
    categories = [c for c in Recipe.__table__.columns['RecipeCategory'].type.enums]
    units = [
        'piece', 'cup', 'tablespoon', 'teaspoon', 'gram', 'kg', 'ml', 'liter', 'pinch', 'clove'
    ]
    # Fetch all recipes for search (id, name, image)
    all_recipes = Recipe.query.with_entities(Recipe.RecipeID, Recipe.RecipeName, Recipe.RecipeImagePath).all()
    recipe_list = [
        {"RecipeID": r.RecipeID, "RecipeName": r.RecipeName, "RecipeImagePath": r.RecipeImagePath} for r in all_recipes
    ]
    # Fetch meal plan categories from Enum (all possible values)
    mealplan_categories = [c for c in MealPlan.__table__.columns['PlanType'].type.enums]
    if request.method == 'POST':
        # Get form data
        recipe_name = request.form.get('recipeName')
        recipe_category = request.form.get('recipeCategory')
        recipe_description = request.form.get('recipeDescription')
        servings = request.form.get('servings')
        cooking_time_hours = int(request.form.get('cookingTimeHours', 0))
        cooking_time_minutes = int(request.form.get('cookingTimeMinutes', 0))
        total_cooking_time = cooking_time_hours * 60 + cooking_time_minutes
        # Handle file upload for recipe photo
        recipe_photo = request.files.get('recipePhoto')
        photo_filename = None
        if recipe_photo:
            import os
            from werkzeug.utils import secure_filename
            uploads_dir = os.path.join('static', 'uploads', 'recipes')
            os.makedirs(uploads_dir, exist_ok=True)
            photo_filename = secure_filename(recipe_photo.filename)
            photo_path = os.path.join(uploads_dir, photo_filename)
            recipe_photo.save(photo_path)
            # Store the path in the format 'uploads/recipes/filename.ext' (no static/)
            photo_filename = f'uploads/recipes/{photo_filename}'
        # Create Recipe
        new_recipe = Recipe(
            RecipeName=recipe_name,
            RecipeCategory=recipe_category,
            Description=recipe_description,
            RecipeImagePath=photo_filename,
            CookingTime=total_cooking_time,
            Servings=servings,
            RecipeDate=datetime.utcnow(),
            AddedByUserID=session['user_id']  # Use current user ID
        )
        db.session.add(new_recipe)
        db.session.flush()  # Ensure RecipeID is available before adding ingredients/instructions
        # Add ingredients
        ingredient_quantities = request.form.getlist('ingredient_quantity[]')
        ingredient_units = request.form.getlist('ingredient_unit[]')
        ingredient_ids = request.form.getlist('ingredient_id[]')
        from models import RecipeIngredient
        # Ensure all lists are the same length and not empty
        if not (ingredient_quantities and ingredient_units and ingredient_ids) or not len(ingredient_quantities):
            flash('Ingredient data missing or invalid.', 'danger')
            db.session.rollback()
            return redirect(url_for('add.add_recipe'))
        for qty, unit, ing_id in zip(ingredient_quantities, ingredient_units, ingredient_ids):
            if not qty or not unit or not ing_id:
                continue
            try:
                recipe_ingredient = RecipeIngredient(
                    RecipeID=new_recipe.RecipeID,
                    IngredientID=int(ing_id),
                    Quantity=float(qty),
                    Unit=unit
                )
                db.session.add(recipe_ingredient)
            except Exception as e:
                flash(f'Ingredient error: {e}', 'danger')
                db.session.rollback()
                return redirect(url_for('add.add_recipe'))
        # Add instructions
        instruction_texts = request.form.getlist('instruction_text[]')
        # Handle step images for instructions
        step_images = request.files.getlist('instruction_image[]') if 'instruction_image[]' in request.files else []
        from models import RecipeInstruction
        if not instruction_texts or not any(text.strip() for text in instruction_texts):
            flash('At least one instruction step is required.', 'danger')
            db.session.rollback()
            return redirect(url_for('add.add_recipe'))
        for idx, text in enumerate(instruction_texts):
            if not text.strip():
                continue
            step_image_path = None
            if step_images and len(step_images) > idx:
                file = step_images[idx]
                if file and hasattr(file, 'filename') and file.filename:
                    import os
                    from werkzeug.utils import secure_filename
                    uploads_dir = os.path.join('static', 'uploads', 'recipes', 'steps')
                    os.makedirs(uploads_dir, exist_ok=True)
                    step_filename = secure_filename(file.filename)
                    step_full_path = os.path.join(uploads_dir, step_filename)
                    file.save(step_full_path)
                    step_image_path = f'uploads/recipes/steps/{step_filename}'
            try:
                instruction = RecipeInstruction(
                    RecipeID=new_recipe.RecipeID,
                    StepNumber=idx+1,
                    InstructionText=text,
                    ImagePath=step_image_path
                )
                db.session.add(instruction)
            except Exception as e:
                flash(f'Instruction error: {e}', 'danger')
                db.session.rollback()
                return redirect(url_for('add.add_recipe'))
        db.session.commit()
        flash('Recipe submitted!', 'success')
        return redirect(url_for('add.add_recipe'))
    return render_template('add-recipe.html', ingredients=ingredients_serialized, categories=categories, units=units, recipe_list=recipe_list, mealplan_categories=mealplan_categories)

@add_bp.route('/add-meal-plan', methods=['POST'])
def add_meal_plan():
    if 'user_id' not in session:
        return redirect(url_for('auth.login', next=request.url))
    # Get form data
    plan_name = request.form.get('mealPlanName')
    plan_description = request.form.get('mealPlanDescription')
    plan_type = request.form.get('mealPlanCategory')
    plan_date = datetime.utcnow()
    plan_photo = request.files.get('mealPlanPhoto')
    photo_filename = None
    if plan_photo:
        import os
        from werkzeug.utils import secure_filename
        uploads_dir = os.path.join('static', 'uploads', 'mealplans')
        os.makedirs(uploads_dir, exist_ok=True)
        photo_filename = secure_filename(plan_photo.filename)
        photo_path = os.path.join(uploads_dir, photo_filename)
        plan_photo.save(photo_path)
        photo_filename = f'uploads/mealplans/{photo_filename}'
    # Add recipes to meal plan
    recipe_ids = request.form.getlist('meal_plan_recipe_ids[]')
    if len(recipe_ids) < 2:
        flash('You must select at least 2 recipes for a meal plan.', 'danger')
        return redirect(url_for('add.add_recipe'))
    # Create MealPlan
    new_plan = MealPlan(
        PlanName=plan_name,
        PlanDescription=plan_description,
        PlanType=plan_type,
        PlanDate=plan_date,
        PlanImagePath=photo_filename,
        UserID=session['user_id']
    )
    db.session.add(new_plan)
    db.session.flush()  # Get new_plan.PlanID
    from models import MealRecipes
    for rid in recipe_ids:
        db.session.add(MealRecipes(PlanID=new_plan.PlanID, RecipeID=rid))
    db.session.commit()
    flash('Meal plan submitted!', 'success')
    return redirect(url_for('main_page.main_page'))

@add_bp.route('/edit-recipe/<int:recipe_id>', methods=['GET', 'POST'])
def edit_recipe(recipe_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login', next=request.url))
    recipe = Recipe.query.get_or_404(recipe_id)
    if recipe.AddedByUserID != session['user_id'] and session.get('user_type') != 'Admin':
        flash('You are not authorized to edit this recipe.', 'danger')
        return redirect(url_for('profile.profile'))
    ingredients = Ingredient.query.order_by(Ingredient.IngredientName).all()
    ingredients_serialized = [
        {"IngredientID": ing.IngredientID, "IngredientName": ing.IngredientName}
        for ing in ingredients
    ]
    categories = [c for c in Recipe.__table__.columns['RecipeCategory'].type.enums]
    units = [
        'piece', 'cup', 'tablespoon', 'teaspoon', 'gram', 'kg', 'ml', 'liter', 'pinch', 'clove'
    ]
    all_recipes = Recipe.query.with_entities(Recipe.RecipeID, Recipe.RecipeName, Recipe.RecipeImagePath).all()
    recipe_list = [
        {"RecipeID": r.RecipeID, "RecipeName": r.RecipeName, "RecipeImagePath": r.RecipeImagePath} for r in all_recipes
    ]
    mealplan_categories = [c for c in MealPlan.__table__.columns['PlanType'].type.enums]
    # Fetch current ingredients and instructions for this recipe
    from models import RecipeIngredient, RecipeInstruction
    edit_ingredients = []
    for ri in RecipeIngredient.query.filter_by(RecipeID=recipe_id).all():
        ingredient = Ingredient.query.get(ri.IngredientID)
        edit_ingredients.append({
            'IngredientID': ri.IngredientID,
            'IngredientName': ingredient.IngredientName if ingredient else '',
            'Quantity': ri.Quantity,
            'Unit': ri.Unit
        })
    edit_instructions = []
    for instr in RecipeInstruction.query.filter_by(RecipeID=recipe_id).order_by(RecipeInstruction.StepNumber).all():
        edit_instructions.append({
            'StepNumber': instr.StepNumber,
            'InstructionText': instr.InstructionText,
            'ImagePath': instr.ImagePath
        })
    if request.method == 'POST':
        recipe.RecipeName = request.form.get('recipeName')
        recipe.RecipeCategory = request.form.get('recipeCategory')
        recipe.Description = request.form.get('recipeDescription')
        recipe.Servings = request.form.get('servings')
        cooking_time_hours = int(request.form.get('cookingTimeHours', 0))
        cooking_time_minutes = int(request.form.get('cookingTimeMinutes', 0))
        recipe.CookingTime = cooking_time_hours * 60 + cooking_time_minutes
        recipe_photo = request.files.get('recipePhoto')
        if recipe_photo and recipe_photo.filename:
            import os
            from werkzeug.utils import secure_filename
            uploads_dir = os.path.join('static', 'uploads', 'recipes')
            os.makedirs(uploads_dir, exist_ok=True)
            photo_filename = secure_filename(recipe_photo.filename)
            photo_path = os.path.join(uploads_dir, photo_filename)
            recipe_photo.save(photo_path)
            recipe.RecipeImagePath = f'uploads/recipes/{photo_filename}'
        # Update ingredients
        from models import RecipeIngredient
        RecipeIngredient.query.filter_by(RecipeID=recipe.RecipeID).delete()
        ingredient_quantities = request.form.getlist('ingredient_quantity[]')
        ingredient_units = request.form.getlist('ingredient_unit[]')
        ingredient_ids = request.form.getlist('ingredient_id[]')
        for qty, unit, ing_id in zip(ingredient_quantities, ingredient_units, ingredient_ids):
            recipe_ingredient = RecipeIngredient(
                RecipeID=recipe.RecipeID,
                IngredientID=ing_id,
                Quantity=qty,
                Unit=unit
            )
            db.session.add(recipe_ingredient)
        # Update instructions
        from models import RecipeInstruction
        RecipeInstruction.query.filter_by(RecipeID=recipe.RecipeID).delete()
        instruction_texts = request.form.getlist('instruction_text[]')
        step_images = request.files.getlist('instruction_image[]') if 'instruction_image[]' in request.files else []
        for idx, text in enumerate(instruction_texts):
            step_image_path = None
            if step_images and len(step_images) > idx:
                file = step_images[idx]
                if file and hasattr(file, 'filename') and file.filename:
                    import os
                    from werkzeug.utils import secure_filename
                    uploads_dir = os.path.join('static', 'uploads', 'recipes', 'steps')
                    os.makedirs(uploads_dir, exist_ok=True)
                    step_filename = secure_filename(file.filename)
                    step_full_path = os.path.join(uploads_dir, step_filename)
                    file.save(step_full_path)
                    step_image_path = f'uploads/recipes/steps/{step_filename}'
            instruction = RecipeInstruction(
                RecipeID=recipe.RecipeID,
                StepNumber=idx+1,
                InstructionText=text,
                ImagePath=step_image_path
            )
            db.session.add(instruction)
        db.session.commit()
        flash('Recipe updated!', 'success')
        return redirect(url_for('profile.profile'))
    return render_template('add-recipe.html', edit_mode=True, recipe=recipe, ingredients=ingredients_serialized, categories=categories, units=units, recipe_list=recipe_list, mealplan_categories=mealplan_categories, edit_ingredients=edit_ingredients, edit_instructions=edit_instructions)

@add_bp.route('/edit-mealplan/<int:plan_id>', methods=['GET', 'POST'])
def edit_mealplan(plan_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login', next=request.url))
    plan = MealPlan.query.get_or_404(plan_id)
    if plan.UserID != session['user_id'] and session.get('user_type') != 'Admin':
        flash('You are not authorized to edit this meal plan.', 'danger')
        return redirect(url_for('profile.profile'))
    mealplan_categories = [c for c in MealPlan.__table__.columns['PlanType'].type.enums]
    all_recipes = Recipe.query.with_entities(Recipe.RecipeID, Recipe.RecipeName, Recipe.RecipeImagePath).all()
    recipe_list = [
        {"RecipeID": r.RecipeID, "RecipeName": r.RecipeName, "RecipeImagePath": r.RecipeImagePath} for r in all_recipes
    ]
    from models import Ingredient, MealRecipes
    ingredients = Ingredient.query.order_by(Ingredient.IngredientName).all()
    ingredients_serialized = [
        {"IngredientID": ing.IngredientID, "IngredientName": ing.IngredientName}
        for ing in ingredients
    ]
    # Fetch selected recipes for this meal plan
    edit_selected_recipes = []
    for mr in MealRecipes.query.filter_by(PlanID=plan.PlanID).all():
        recipe = Recipe.query.get(mr.RecipeID)
        if recipe:
            edit_selected_recipes.append({
                'RecipeID': recipe.RecipeID,
                'RecipeName': recipe.RecipeName
            })
    if request.method == 'POST':
        plan.PlanName = request.form.get('mealPlanName')
        plan.PlanDescription = request.form.get('mealPlanDescription')
        plan.PlanType = request.form.get('mealPlanCategory')
        plan_photo = request.files.get('mealPlanPhoto')
        if plan_photo and plan_photo.filename:
            import os
            from werkzeug.utils import secure_filename
            uploads_dir = os.path.join('static', 'uploads', 'mealplans')
            os.makedirs(uploads_dir, exist_ok=True)
            photo_filename = secure_filename(plan_photo.filename)
            photo_path = os.path.join(uploads_dir, photo_filename)
            plan_photo.save(photo_path)
            plan.PlanImagePath = f'uploads/mealplans/{photo_filename}'
        # Update meal plan recipes
        from models import MealRecipes
        MealRecipes.query.filter_by(PlanID=plan.PlanID).delete()
        recipe_ids = request.form.getlist('meal_plan_recipe_ids[]')
        for rid in recipe_ids:
            db.session.add(MealRecipes(PlanID=plan.PlanID, RecipeID=rid))
        db.session.commit()
        flash('Meal plan updated!', 'success')
        return redirect(url_for('profile.profile'))
    return render_template('add-recipe.html', edit_mode=True, mealplan=plan, mealplan_categories=mealplan_categories, recipe_list=recipe_list, ingredients=ingredients_serialized, edit_selected_recipes=edit_selected_recipes)

@add_bp.route('/delete-recipe/<int:recipe_id>', methods=['POST'])
def delete_recipe(recipe_id):
    from models import Recipe, RecipeIngredient, RecipeInstruction, Review
    recipe = Recipe.query.get_or_404(recipe_id)
    user_id = session.get('user_id')
    user_type = session.get('user_type')
    # Only allow if admin or owner
    if not user_id or (recipe.AddedByUserID != user_id and user_type != 'Admin'):
        flash('You are not authorized to delete this recipe.', 'danger')
        return redirect(url_for('profile.profile'))
    # Delete related ingredients, instructions, reviews
    RecipeIngredient.query.filter_by(RecipeID=recipe_id).delete()
    RecipeInstruction.query.filter_by(RecipeID=recipe_id).delete()
    Review.query.filter_by(RecipeID=recipe_id).delete()
    db.session.delete(recipe)
    db.session.commit()
    flash('Recipe deleted!', 'success')
    return redirect(url_for('profile.profile'))

@add_bp.route('/delete-mealplan/<int:plan_id>', methods=['POST'])
def delete_mealplan(plan_id):
    from models import MealPlan, MealRecipes, Review
    plan = MealPlan.query.get_or_404(plan_id)
    user_id = session.get('user_id')
    user_type = session.get('user_type')
    # Only allow if admin or owner
    if not user_id or (plan.UserID != user_id and user_type != 'Admin'):
        flash('You are not authorized to delete this meal plan.', 'danger')
        return redirect(url_for('profile.profile'))
    # Delete related meal recipes and reviews
    MealRecipes.query.filter_by(PlanID=plan_id).delete()
    Review.query.filter_by(PlanID=plan_id).delete()
    db.session.delete(plan)
    db.session.commit()
    flash('Meal plan deleted!', 'success')
    return redirect(url_for('profile.profile'))
