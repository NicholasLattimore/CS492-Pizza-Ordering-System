from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify, current_app
from app.models import db, MenuItem

cart_bp = Blueprint('cart', __name__)

def get_cart():
    """Retrieve or initialize the shopping cart in session."""
    if 'cart' not in session:
        session['cart'] = []
    return session['cart']

def calculate_totals(cart, order_type='pickup'):
    """Compute subtotal, sales tax, delivery fee, and grand total."""
    subtotal = sum(item.get('unit_price', 0.0) * item.get('quantity', 1) for item in cart)
    subtotal = round(subtotal, 2)
    tax_rate = current_app.config.get('TAX_RATE', 0.0825)
    tax_amount = round(subtotal * tax_rate, 2)
    delivery_fee = current_app.config.get('DELIVERY_FEE', 4.99) if order_type == 'delivery' else 0.0
    total_amount = round(subtotal + tax_amount + delivery_fee, 2)
    return {
        'subtotal': subtotal,
        'tax_rate': tax_rate,
        'tax_amount': tax_amount,
        'delivery_fee': delivery_fee,
        'total_amount': total_amount,
        'item_count': sum(item.get('quantity', 1) for item in cart)
    }

@cart_bp.route('/')
def index():
    cart = get_cart()
    totals = calculate_totals(cart, order_type=session.get('order_type', 'pickup'))
    return render_template('cart.html', cart=cart, totals=totals)

@cart_bp.route('/add', methods=['POST'])
def add_to_cart():
    menu_item_id = request.form.get('menu_item_id', type=int)
    item = db.get_or_404(MenuItem, menu_item_id)

    if not item.is_available:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'This item is currently sold out.'}), 400
        flash(f'Sorry, {item.name} is currently out of stock.', 'danger')
        return redirect(url_for('menu.index'))

    size_name = request.form.get('size_option', '').strip()
    crust_name = request.form.get('crust_option', '').strip()
    special_notes = request.form.get('special_notes', '').strip()
    quantity = max(1, request.form.get('quantity', 1, type=int))

    # Calculate unit price based on options
    unit_price = item.base_price
    options = item.get_options()

    if size_name and 'sizes' in options:
        for s in options['sizes']:
            if s['name'] == size_name:
                unit_price += s.get('price_modifier', 0.0)
                break

    if crust_name and 'crusts' in options:
        for c in options['crusts']:
            if c['name'] == crust_name:
                unit_price += c.get('price_modifier', 0.0)
                break

    unit_price = round(unit_price, 2)

    cart = get_cart()

    # Check if identical item with exact same configuration already exists in cart
    existing_index = None
    for idx, cart_item in enumerate(cart):
        if (cart_item['menu_item_id'] == item.id and
            cart_item.get('size_option') == size_name and
            cart_item.get('crust_option') == crust_name and
            cart_item.get('special_notes') == special_notes):
            existing_index = idx
            break

    if existing_index is not None:
        cart[existing_index]['quantity'] += quantity
        cart[existing_index]['line_total'] = round(cart[existing_index]['quantity'] * unit_price, 2)
    else:
        cart.append({
            'menu_item_id': item.id,
            'name': item.name,
            'description': item.description,
            'image_url': item.image_url,
            'size_option': size_name or None,
            'crust_option': crust_name or None,
            'special_notes': special_notes or None,
            'unit_price': unit_price,
            'quantity': quantity,
            'line_total': round(quantity * unit_price, 2)
        })

    session['cart'] = cart
    session.modified = True

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        totals = calculate_totals(cart)
        return jsonify({
            'success': True,
            'message': f'Added {item.name} to cart.',
            'cart_count': totals['item_count'],
            'cart_subtotal': totals['subtotal']
        })

    flash(f'Added {item.name} to your cart!', 'success')
    return redirect(url_for('cart.index'))

@cart_bp.route('/update', methods=['POST'])
def update_item():
    index = request.form.get('index', type=int)
    action = request.form.get('action')  # 'increase', 'decrease', or 'set'
    cart = get_cart()

    if index is not None and 0 <= index < len(cart):
        if action == 'increase':
            cart[index]['quantity'] += 1
        elif action == 'decrease':
            cart[index]['quantity'] -= 1
        elif action == 'set':
            new_qty = request.form.get('quantity', 1, type=int)
            cart[index]['quantity'] = new_qty

        if cart[index]['quantity'] <= 0:
            removed_name = cart[index]['name']
            cart.pop(index)
            flash(f'Removed {removed_name} from your cart.', 'info')
        else:
            cart[index]['line_total'] = round(cart[index]['quantity'] * cart[index]['unit_price'], 2)

        session['cart'] = cart
        session.modified = True

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        order_type = request.form.get('order_type', 'pickup')
        totals = calculate_totals(cart, order_type=order_type)
        return jsonify({
            'success': True,
            'cart': cart,
            'totals': totals
        })

    return redirect(url_for('cart.index'))

@cart_bp.route('/remove/<int:index>', methods=['POST'])
def remove_item(index):
    cart = get_cart()
    if 0 <= index < len(cart):
        removed_item = cart.pop(index)
        session['cart'] = cart
        session.modified = True
        flash(f'Removed {removed_item["name"]} from your cart.', 'info')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        order_type = request.form.get('order_type', 'pickup')
        totals = calculate_totals(cart, order_type=order_type)
        return jsonify({
            'success': True,
            'cart': cart,
            'totals': totals
        })

    return redirect(url_for('cart.index'))

@cart_bp.route('/clear', methods=['POST'])
def clear_cart():
    session['cart'] = []
    session.modified = True
    flash('Your cart has been cleared.', 'info')
    return redirect(url_for('menu.index'))

@cart_bp.route('/checkout')
def checkout():
    """PB-04: Order review and final bill calculation screen before submitting."""
    cart = get_cart()
    if not cart:
        flash('Your cart is empty. Please add delicious items before reviewing your bill.', 'warning')
        return redirect(url_for('menu.index'))

    order_type = session.get('order_type', 'pickup')
    totals = calculate_totals(cart, order_type=order_type)
    return render_template('checkout.html', cart=cart, totals=totals, order_type=order_type)

@cart_bp.route('/calculate-api', methods=['POST'])
def calculate_api():
    """PB-04: Dynamic AJAX bill calculation when switching Pickup vs Delivery."""
    cart = get_cart()
    data = request.get_json() or {}
    order_type = data.get('order_type', 'pickup')
    session['order_type'] = order_type
    totals = calculate_totals(cart, order_type=order_type)
    return jsonify({
        'success': True,
        'totals': totals
    })
