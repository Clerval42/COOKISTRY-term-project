from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from config import Config
import json

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)

# Model
class Recipe(db.Model):
    __tablename__ = 'recipe'
    RecipeID = db.Column(db.Integer, primary_key=True)
    RecipeName = db.Column(db.String(100), nullable=False)
    Description = db.Column(db.Text)
    CookingTime = db.Column(db.Integer)
    RecipeCategory = db.Column(db.Enum('Appetizer','Main Course','Dessert','Salad','Soup','Snack','Beverage','Side Dish','Breakfast','Brunch'))
    RecipeDate = db.Column(db.DateTime)
    AddedByUserID = db.Column(db.Integer)

# Route
@app.route('/')
def recipe_list():
    recipes = Recipe.query.all()
    return render_template('recipe_list.html', recipes=recipes)

@app.route('/search')
def search():
    keyword = request.args.get('q', '')
    cur = mysql.connection.cursor()
    cur.execute("SELECT RecipeID, RecipeName FROM recipe WHERE RecipeName LIKE %s", ('%' + keyword + '%',))
    results = cur.fetchall()
    cur.close()
    return jsonify(results)


if __name__ == '__main__':
    app.run(debug=True)
