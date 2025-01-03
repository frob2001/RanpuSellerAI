import logging
from flask import Blueprint, request, jsonify
from paypalserversdk.api_helper import ApiHelper
from paypalserversdk.models.amount_with_breakdown import AmountWithBreakdown
from paypalserversdk.models.checkout_payment_intent import CheckoutPaymentIntent
from paypalserversdk.models.order_request import OrderRequest
from paypalserversdk.models.purchase_unit_request import PurchaseUnitRequest
from api.paypal_client import paypal_client
from api.models.productos import Productos
from api.models.impuestos import Impuestos
from firebase_admin import db as firebase_db  # Firebase Admin SDK initialized
from api.database import db

logger = logging.getLogger(__name__)

paypal_bp = Blueprint("paypal", __name__)
orders_controller = paypal_client.orders

@paypal_bp.route("/orders", methods=["POST"])
def create_order():
    logger.info("Creating PayPal order with dynamic cart calculation from Firebase...")
    request_body = request.get_json() or {}
    user_id = request_body.get('userId')

    if not user_id:
        return jsonify({"message": "User ID is required"}), 400

    # Fetch user's cart from Firebase Realtime Database
    cart_ref = firebase_db.reference(f'/carts/{user_id}')
    cart = cart_ref.get()

    if not cart:
        return jsonify({"message": "No cart found for this user"}), 404
    
    items = cart.get('items', [])

    if not items or not isinstance(items, list):
        return jsonify({"message": "Debe proporcionar una lista válida de productos con cantidades en 'items'"}), 400

    # Retrieve the active tax
    active_tax = Impuestos.query.filter_by(activo=True).first()
    if not active_tax:
        return jsonify({"message": "No hay ningún impuesto activo configurado"}), 400

    tax_percentage = float(active_tax.porcentaje) / 100  # Convert to percentage

    subtotal = 0
    delivery_fee = 2.00

    for item in items:
        producto_id = item.get('databaseProductId')  # Use the correct key
        quantity = item.get('quantity', 0)

        if not producto_id or not isinstance(quantity, int) or quantity <= 0:
            return jsonify({"message": f"ID de producto o cantidad inválida en el item: {item}"}), 400

        producto = Productos.query.get(producto_id)
        if not producto:
            return jsonify({"message": f"Producto con ID {producto_id} no encontrado"}), 404

        # Multiply price by quantity and accumulate in the subtotal
        subtotal += float(producto.precio) * quantity

    # Calculate tax
    calculated_tax = subtotal * tax_percentage

    # Calculate total
    total = subtotal + calculated_tax + delivery_fee

    # Create PayPal order with calculated total
    try:
        order = orders_controller.orders_create({
            "body": OrderRequest(
                intent=CheckoutPaymentIntent.CAPTURE,
                purchase_units=[
                    PurchaseUnitRequest(
                        amount=AmountWithBreakdown(
                            currency_code='USD',
                            value=f"{total:.2f}",  # Dynamic total
                            breakdown={
                                "item_total": {"currency_code": "USD", "value": f"{subtotal:.2f}"},
                                "tax_total": {"currency_code": "USD", "value": f"{calculated_tax:.2f}"},
                                "shipping": {"currency_code": "USD", "value": f"{delivery_fee:.2f}"}
                            }
                        )
                    )
                ]
            ),
            "prefer": 'return=representation'
        })
        
        approve_url = None
        for link in order.body.links:
            if link.rel == 'approve':
                approve_url = link.href
                break

        if not approve_url:
            logger.error("No approval URL found in PayPal response.")
            return jsonify({"error": "Unable to get approval URL from PayPal"}), 500
        
        logger.info(f"Order created. Approval URL: {approve_url}")
        return jsonify({"approveUrl": approve_url}), 200

    except Exception as e:
        logger.error(f"Error creating PayPal order: {e}")
        return {"error": str(e)}, 500


@paypal_bp.route("/orders/<order_id>/capture", methods=["POST"])
def capture_order(order_id):
    logger.info(f"Capturing PayPal order {order_id}...")
    try:
        captured_order = orders_controller.orders_capture({
            "id": order_id,
            "prefer": 'return=representation'
        })
        logger.info(f"Order {order_id} captured successfully.")

        # Update order status in Firebase
        request_body = request.get_json() or {}
        user_id = request_body.get('userId')

        if user_id:
            cart_ref = firebase_db.reference(f'/carts/{user_id}')
            cart_ref.update({"status": "paid"})  # Example status update

        return ApiHelper.json_serialize(captured_order.body), 200

    except Exception as e:
        logger.error(f"Error capturing order {order_id}: {e}")
        return {"error": str(e)}, 500
