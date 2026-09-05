from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import db, Order

staff_bp = Blueprint('staff', __name__)

@staff_bp.route('/orders')
def orders():
    status_filter = request.args.get('status', 'all')
    query = Order.query.order_by(Order.created_at.desc())

    if status_filter and status_filter != 'all':
        query = query.filter_by(status=status_filter)

    orders_list = query.all()
    counts = {
        'all': Order.query.count(),
        'Received': Order.query.filter_by(status='Received').count(),
        'Preparing': Order.query.filter_by(status='Preparing').count(),
        'Ready': Order.query.filter_by(status='Ready').count(),
        'Completed': Order.query.filter_by(status='Completed').count(),
    }

    return render_template('staff/orders.html', orders=orders_list, counts=counts, current_filter=status_filter)

@staff_bp.route('/orders/<int:order_id>/status', methods=['POST'])
def update_status(order_id):
    order = db.get_or_404(Order, order_id)
    new_status = request.form.get('status')
    valid_statuses = ['Received', 'Preparing', 'Ready', 'Completed', 'Cancelled']

    if new_status in valid_statuses:
        order.status = new_status
        db.session.commit()
        flash(f'Order {order.order_number} status updated to {new_status}.', 'success')
    else:
        flash('Invalid order status.', 'danger')

    return redirect(url_for('staff.orders', status=request.form.get('current_filter', 'all')))
