from flask_sqlalchemy import SQLAlchemy
import datetime

# from app import db,app
# with app.app_context():
#     db.create_all()
#     print("Database tables created successfully.")

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    UserID = db.Column(db.Integer, primary_key=True)
    UserName = db.Column(db.String(50), unique=False, nullable=False)
    PasswordHash = db.Column(db.String(255), nullable=False)
    Email = db.Column(db.String(100), unique=True, nullable=False)
    UserType = db.Column(db.Enum('User', 'Admin'), nullable=False, default='User')
    RegistrationDate = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    ProfilePicturePath = db.Column(db.String(255), default='/static/default-user.png')
    # Relationships
    recipes = db.relationship('Recipe', backref='user', lazy=True)
    mealplans = db.relationship('MealPlan', backref='user', lazy=True)
    reviews = db.relationship('Review', backref='user', lazy=True)

class Recipe(db.Model):
    __tablename__ = 'recipe'
    RecipeID = db.Column(db.Integer, primary_key=True)
    RecipeName = db.Column(db.String(100), nullable=False)
    Description = db.Column(db.Text)
    CookingTime = db.Column(db.Integer)
    Servings = db.Column(db.Integer)
    RecipeImagePath = db.Column(db.String(255))
    RecipeDate = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    RecipeCategory = db.Column(db.Enum('Appetizer','Main Course','Dessert','Salad','Soup','Snack','Beverage','Side Dish','Breakfast','Other'), nullable=False)
    AddedByUserID = db.Column(db.Integer, db.ForeignKey('user.UserID'), nullable=False)
    # Relationships
    ingredients = db.relationship('RecipeIngredient', backref='recipe', lazy=True)
    instructions = db.relationship('RecipeInstruction', backref='recipe', lazy=True)
    reviews = db.relationship('Review', backref='recipe', lazy=True)
    mealplans = db.relationship('MealPlan', secondary='meal_recipes', back_populates='recipes', lazy=True)

class Ingredient(db.Model):
    __tablename__ = 'ingredient'
    IngredientID = db.Column(db.Integer, primary_key=True)
    IngredientName = db.Column(db.String(100), nullable=False)
    IngredientCategory = db.Column(db.Enum('Dairy','Protein','Vegetable','Fruit','Grain','Herb','Spice','Nut & Seed','Oil & Vinegar','Sweetener','Condiment','Legume','Beverage','Seafood','Meat','Pasta & Noodles','Cheese','Bakery','Canned Goods','Frozen','Other'))
    # Relationships
    recipe_ingredients = db.relationship('RecipeIngredient', backref='ingredient', lazy=True)

class RecipeIngredient(db.Model):
    __tablename__ = 'recipe_ingredients'
    RecipeID = db.Column(db.Integer, db.ForeignKey('recipe.RecipeID'), primary_key=True)
    IngredientID = db.Column(db.Integer, db.ForeignKey('ingredient.IngredientID'), primary_key=True)
    Quantity = db.Column(db.Integer, nullable=False)
    Unit = db.Column(db.Enum('piece','cup','tablespoon','teaspoon','gram','kg','ml','liter','pinch','clove'), nullable=False)

class RecipeInstruction(db.Model):
    __tablename__ = 'recipe_instructions'
    RecipeID = db.Column(db.Integer, db.ForeignKey('recipe.RecipeID'), primary_key=True)
    StepNumber = db.Column(db.Integer, primary_key=True)
    InstructionText = db.Column(db.Text, nullable=False)
    ImagePath = db.Column(db.String(255))

class MealPlan(db.Model):
    __tablename__ = 'mealplan'
    PlanID = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer, db.ForeignKey('user.UserID'), nullable=False)
    PlanName = db.Column(db.Text)
    PlanDescription = db.Column(db.Text)
    PlanDate = db.Column(db.Date, nullable=False)
    PlanType = db.Column(db.Enum('Breakfast','Brunch','Lunch','Dinner','Snack','Other'), nullable=False)
    PlanImagePath = db.Column(db.String(255))
    # Relationships
    recipes = db.relationship('Recipe', secondary='meal_recipes', back_populates='mealplans', lazy=True)
    reviews = db.relationship('Review', backref='mealplan', lazy=True)

class MealRecipes(db.Model):
    __tablename__ = 'meal_recipes'
    PlanID = db.Column(db.Integer, db.ForeignKey('mealplan.PlanID'), primary_key=True)
    RecipeID = db.Column(db.Integer, db.ForeignKey('recipe.RecipeID'), primary_key=True)

class Review(db.Model):
    __tablename__ = 'review'
    ReviewID = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer, db.ForeignKey('user.UserID'), nullable=False)
    RecipeID = db.Column(db.Integer, db.ForeignKey('recipe.RecipeID'))
    PlanID = db.Column(db.Integer, db.ForeignKey('mealplan.PlanID'))
    Comment = db.Column(db.Text)
    Score = db.Column(db.Integer, nullable=False)
    ReviewDate = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
