# app.py
from flask import Flask, session
from config import Config
from routes.auth import auth_bp
from routes.recipe import recipe_bp, slugify
from routes.main_page import main_page_bp
from routes.meals import meals_bp
from routes.pages import pages_bp
from routes.add import add_bp  # Import the add blueprint
from routes.profile import profile_bp  # Import the profile blueprint
from routes.lists import lists_bp  # Import the lists blueprint
from models import db

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(recipe_bp)
app.register_blueprint(main_page_bp)
app.register_blueprint(meals_bp)
app.register_blueprint(pages_bp)
app.register_blueprint(add_bp)  # Register the add blueprint
app.register_blueprint(profile_bp)  # Register the profile blueprint
app.register_blueprint(lists_bp)  # Register the lists blueprint

app.jinja_env.globals.update(slugify=slugify)

@app.context_processor
def inject_user():
    return {
        'is_logged_in': 'user_id' in session,
        'logged_in_username': session.get('username'),
        'logged_in_user_type': session.get('user_type')
    }

if __name__ == '__main__':
    app.run(debug=True)
