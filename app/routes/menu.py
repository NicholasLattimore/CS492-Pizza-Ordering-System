from flask import Blueprint, render_template, jsonify, abort
from app.models import db, Category, MenuItem

menu_bp = Blueprint('menu', __name__)

@menu_bp.route('/')
def index():
    categories = Category.query.order_by(Category.display_order).all()
    # Eagerly group items by category
    menu_by_category = []
    for cat in categories:
        items = MenuItem.query.filter_by(category_id=cat.id).all()
        menu_by_category.append({
            'category': cat,
            'menu_items': items
        })
    return render_template('menu.html', menu_by_category=menu_by_category, categories=categories)

@menu_bp.route('/item/<int:item_id>')
def item_details(item_id):
    item = db.get_or_404(MenuItem, item_id)
    return jsonify(item.to_dict())
