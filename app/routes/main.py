from flask import Blueprint, render_template
from app.models import MenuItem, Category

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Fetch featured items for landing page highlight
    featured_items = MenuItem.query.filter_by(is_available=True).limit(3).all()
    categories = Category.query.order_by(Category.display_order).all()
    return render_template('index.html', featured_items=featured_items, categories=categories)

@main_bp.route('/about')
def about():
    return render_template('index.html', scroll_to='about')

@main_bp.route('/contact')
def contact():
    return render_template('index.html', scroll_to='contact')
