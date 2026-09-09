import pytest
from app.models import MenuItem, Order, OrderItem

def test_pb01_restaurant_info_and_home_page(client):
    """PB-01: Home page includes business description, photos, hours, location, and contact information."""
    res = client.get('/')
    assert res.status_code == 200
    html = res.data.decode('utf-8')

    # Restaurant name and branding
    assert 'Bella Napoli' in html
    # Description / heritage
    assert 'Wood-Fired' in html or 'Neapolitan' in html
    # Operating Hours
    assert 'Monday - Thursday' in html
    assert '11:00 AM - 10:00 PM' in html
    # Location & Contact
    assert 'Evergreen Terrace' in html
    assert '(555) 392-4920' in html
    assert 'orders@bellanapolipizza.com' in html
    # Navigation elements
    assert 'Browse Menu' in html
    assert 'Staff Portal' in html
    assert 'Cart' in html

def test_pb02_menu_browsing_and_item_details(client):
    """PB-02: Menu is grouped by category. Shows item name, description, price, available options, and marks unavailable items."""
    res = client.get('/menu/')
    assert res.status_code == 200
    html = res.data.decode('utf-8')

    # Categories
    assert 'Specialty Pizzas' in html
    assert 'Appetizers' in html
    assert 'Beverages' in html
    assert 'Desserts' in html

    # Items and prices
    assert 'Margherita Classico' in html
    assert '14.99' in html
    assert 'Pepperoni Rustica' in html

    # Acceptance criteria: Unavailable items are clearly marked
    assert 'Sold Out' in html or 'Currently Unavailable' in html
    assert 'Diavola Piccante' in html

    # JSON endpoint for item details / customization
    item = MenuItem.query.filter_by(name='Margherita Classico').first()
    assert item is not None
    res_item = client.get(f'/menu/item/{item.id}')
    assert res_item.status_code == 200
    data = res_item.get_json()
    assert data['name'] == 'Margherita Classico'
    assert 'sizes' in data['options']
    assert 'crusts' in data['options']

def test_pb03_order_builder_and_shopping_cart(client):
    """PB-03: Add items to cart, change quantities, remove items, review cart, handle empty-cart behavior."""
    # 1. Empty cart behavior
    res = client.get('/cart/')
    assert res.status_code == 200
    assert 'Your Cart is Currently Empty' in res.data.decode('utf-8')
    assert 'Browse Our Menu' in res.data.decode('utf-8')

    # 2. Add item to cart
    item = MenuItem.query.filter_by(is_available=True).first()
    add_res = client.post('/cart/add', data={
        'menu_item_id': item.id,
        'size_option': 'Medium (12")',
        'crust_option': 'Classic Hand-Tossed',
        'special_notes': 'Extra crispy',
        'quantity': 2
    }, follow_redirects=True)
    assert add_res.status_code == 200
    cart_html = add_res.data.decode('utf-8')
    assert item.name in cart_html
    assert 'Medium' in cart_html
    assert 'Extra crispy' in cart_html

    # 3. Increase quantity
    upd_res = client.post('/cart/update', data={'index': 0, 'action': 'increase'}, follow_redirects=True)
    assert upd_res.status_code == 200

    # 4. Decrease quantity
    down_res = client.post('/cart/update', data={'index': 0, 'action': 'decrease'}, follow_redirects=True)
    assert down_res.status_code == 200

    # 5. Remove item
    rem_res = client.post('/cart/remove/0', follow_redirects=True)
    assert rem_res.status_code == 200
    assert 'Your Cart is Currently Empty' in rem_res.data.decode('utf-8')

def test_pb04_final_bill_calculation_and_order_review(client):
    """PB-04: System displays selected items, quantities, subtotal, taxes or fees, and final total. Customer cannot submit empty order."""
    # Cannot checkout with empty cart
    checkout_res = client.get('/cart/checkout', follow_redirects=True)
    assert 'Your cart is empty' in checkout_res.data.decode('utf-8')

    # Cannot submit empty order
    empty_submit = client.post('/order/submit', data={'customer_name': 'Test User'}, follow_redirects=True)
    assert 'Cannot submit an empty order' in empty_submit.data.decode('utf-8')

    # Add item to cart
    item = MenuItem.query.filter_by(is_available=True).first()
    client.post('/cart/add', data={
        'menu_item_id': item.id,
        'quantity': 1
    })

    # Test checkout view
    res = client.get('/cart/checkout')
    assert res.status_code == 200
    html = res.data.decode('utf-8')
    assert 'Subtotal' in html
    assert 'Estimated Tax (8.25%)' in html
    assert 'Final Total' in html

    # Test dynamic bill calculation API
    api_res = client.post('/cart/calculate-api', json={'order_type': 'delivery'})
    assert api_res.status_code == 200
    calc_data = api_res.get_json()
    assert calc_data['success'] is True
    assert calc_data['totals']['delivery_fee'] == 4.99
    expected_tax = round(calc_data['totals']['subtotal'] * 0.0825, 2)
    assert calc_data['totals']['tax_amount'] == expected_tax
    assert calc_data['totals']['total_amount'] == round(calc_data['totals']['subtotal'] + expected_tax + 4.99, 2)

def test_pb05_customer_order_submission_and_confirmation(client):
    """PB-05: Required info validated, order record created, confirmation screen shown with order number, and visible on staff dashboard."""
    # Add item to cart first
    item = MenuItem.query.filter_by(is_available=True).first()
    client.post('/cart/add', data={
        'menu_item_id': item.id,
        'size_option': 'Large (16")',
        'crust_option': 'Classic Hand-Tossed',
        'quantity': 1
    })

    # Test validation error (missing required fields)
    fail_submit = client.post('/order/submit', data={
        'customer_name': '',
        'customer_email': 'invalid-email',
        'customer_phone': '',
        'order_type': 'delivery',
        'delivery_address': ''
    }, follow_redirects=True)
    assert 'Customer Name is required.' in fail_submit.data.decode('utf-8')
    assert 'A valid Email address is required.' in fail_submit.data.decode('utf-8')
    assert 'Phone Number is required.' in fail_submit.data.decode('utf-8')
    assert 'Delivery Address is required for delivery orders.' in fail_submit.data.decode('utf-8')

    # Successful submission (Pickup)
    valid_submit = client.post('/order/submit', data={
        'customer_name': 'Kellen Jones',
        'customer_email': 'kjones@example.com',
        'customer_phone': '(555) 987-6543',
        'order_type': 'pickup',
        'special_instructions': 'Extra parmesan packets please'
    }, follow_redirects=True)

    assert valid_submit.status_code == 200
    confirm_html = valid_submit.data.decode('utf-8')
    assert 'Order Received!' in confirm_html
    assert 'ORD-' in confirm_html
    assert 'Kellen Jones' in confirm_html
    assert 'Extra parmesan packets please' in confirm_html

    # Verify order in database
    saved_order = Order.query.filter_by(customer_name='Kellen Jones').first()
    assert saved_order is not None
    assert saved_order.order_number.startswith('ORD-')
    assert len(saved_order.items) == 1
    assert saved_order.items[0].size_option == 'Large (16")'

    # Verify visible on Restaurant Staff Dashboard (PB-05 acceptance criteria)
    staff_res = client.get('/staff/orders')
    assert staff_res.status_code == 200
    staff_html = staff_res.data.decode('utf-8')
    assert saved_order.order_number in staff_html
    assert 'Kellen Jones' in staff_html
    assert '(555) 987-6543' in staff_html

    # Test staff updating order status
    status_update = client.post(f'/staff/orders/{saved_order.id}/status', data={
        'status': 'Preparing',
        'current_filter': 'all'
    }, follow_redirects=True)
    assert status_update.status_code == 200
    assert saved_order.status == 'Preparing'

def test_t1_06_responsive_layout_review(client):
    """T1-06 (PB-10): Review Sprint 1 pages for responsive layout (mobile, tablet, desktop)."""
    endpoints = ['/', '/menu/', '/cart/', '/staff/orders']
    for ep in endpoints:
        res = client.get(ep)
        assert res.status_code == 200
        html = res.data.decode('utf-8')
        # Viewport meta tag for mobile scaling
        assert 'name="viewport"' in html
        assert 'width=device-width' in html
        # Responsive navbar toggle for mobile screens
        assert 'navbar-toggler' in html
        # Responsive Bootstrap grid system
        assert 'container' in html
        assert 'col-' in html or 'col-md-' in html or 'col-lg-' in html

