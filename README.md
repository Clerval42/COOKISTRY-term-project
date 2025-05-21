# COOKISTRY

A modern web application for sharing, discovering, and planning recipes and meal plans. Built with Flask, SQLAlchemy, and MySQL.

## Features
- User registration, login, and profile management
- Add, edit, and view recipes with rich details and images
- Create and manage meal plans (collections of recipes)
- Leave reviews and ratings for both recipes and meal plans
- Search and filter recipes and meal plans by category, popularity, and comments
- Responsive, modern UI with category images and carousels

## Project Structure
```
COOKISTRY/
├── app.py                # Main Flask app
├── config.py             # Configuration (DB, secret keys, etc.)
├── models.py             # SQLAlchemy models
├── requirements.txt      # Python dependencies
├── routes/               # Flask Blueprints (modular routes)
├── static/
│   ├── css/style.css     # Main stylesheet
│   ├── js/script.js      # Main JS
│   ├── images/           # Category, logo, and default images
│   └── uploads/
│       ├── recipes/      # Uploaded recipe images
│       ├── mealplans/    # Uploaded meal plan images
│       └── users/        # User profile images
├── templates/            # Jinja2 HTML templates
│   ├── base.html         # Main layout
│   ├── index.html        # Homepage
│   ├── ...               # Other pages (recipes, meals, add, detail, etc.)
└── ...
```

## Setup Instructions
1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd COOKISTRY
   ```
2. **Create a virtual environment and activate it**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure the database**
   - Edit `config.py` with your MySQL connection details.
   - Create the database and tables:
     ```bash
     python
     >>> from app import db, app
     >>> with app.app_context():
     ...     db.create_all()
     ...
     ```
5. **Run the application**
   ```bash
   flask run
   ```
   The app will be available at http://127.0.0.1:5000/

## Usage
- Register or log in to add recipes and meal plans.
- Browse recipes and meal plans by category or popularity.
- Add images for recipes and meal plans (stored in `static/uploads/recipes/` and `static/uploads/mealplans/`).
- Leave reviews and ratings for both recipes and meal plans.

## Folder Conventions
- **Recipe images:** `static/uploads/recipes/`
- **Meal plan images:** `static/uploads/mealplans/`
- **User profile images:** `static/uploads/users/`
- **Default images:** `static/images/`

## Customization
- To add new categories, update the Enum fields in `models.py`.
- To change the look and feel, edit `static/css/style.css` and the templates in `templates/`.

## License
© 2025 COOKISTRY. All rights reserved.

---
For any issues or contributions, please open an issue or pull request.
