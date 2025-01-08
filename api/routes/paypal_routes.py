import logging
import os
import json
import base64
import requests
import pytz
from dateutil.parser import isoparse
from datetime import datetime
from flask import Blueprint, request, jsonify, redirect
from paypalserversdk.models.amount_with_breakdown import AmountWithBreakdown
from paypalserversdk.models.checkout_payment_intent import CheckoutPaymentIntent
from paypalserversdk.models.order_request import OrderRequest
from paypalserversdk.models.purchase_unit_request import PurchaseUnitRequest
from api.models.productos import Productos
from api.models.impuestos import Impuestos
from api.models.pedidos_usuario import PedidosUsuario
from api.models.pedidos import Pedidos
from api.models.usuarios import Usuarios
from firebase_admin import db as firebase_db  # Firebase Admin SDK initialized
from api.database import db

logger = logging.getLogger(__name__)

paypal_bp = Blueprint("paypal", __name__)

# =============================================================================
# PAYPAL DIRECT CAPTURE UTILS (OFFICIAL DOC STYLE)
# =============================================================================

PAYPAL_CLIENT_ID = os.getenv('PAYPAL_CLIENT_ID')
PAYPAL_CLIENT_SECRET = os.getenv('PAYPAL_CLIENT_SECRET')

# Toggle sandbox vs production as needed. 
# In production, set this based on an env var if you prefer.
USE_SANDBOX = True

if USE_SANDBOX:
    PAYPAL_BASE = "https://api-m.sandbox.paypal.com"
else:
    PAYPAL_BASE = "https://api-m.paypal.com"


def get_paypal_access_token() -> str:
    """
    Fetch an OAuth2 access token directly from PayPal (client credentials).
    https://developer.paypal.com/docs/api/get-an-access-token-curl/
    """
    url = f"{PAYPAL_BASE}/v1/oauth2/token"
    auth_header = base64.b64encode(
        f"{PAYPAL_CLIENT_ID}:{PAYPAL_CLIENT_SECRET}".encode("utf-8")
    ).decode("utf-8")

    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {"grant_type": "client_credentials"}

    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()  # raise HTTPError if 4xx/5xx
    token_info = response.json()
    return token_info["access_token"]


def capture_order_official(order_id: str) -> dict:
    """
    Captures a PayPal order via direct REST call to /v2/checkout/orders/<order_id>/capture
    per the official PayPal docs.
    https://developer.paypal.com/docs/api/orders/v2/#orders_capture
    """
    access_token = get_paypal_access_token()

    url = f"{PAYPAL_BASE}/v2/checkout/orders/{order_id}/capture"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }

    # Note: the capture API can accept an empty JSON body as per docs
    response = requests.post(url, headers=headers, json={})
    response.raise_for_status()  # raise if HTTP 4xx/5xx
    return response.json()  # The API returns JSON with capture details


# =============================================================================
# CREATE ORDER
# =============================================================================

@paypal_bp.route("/orders", methods=["POST"])
def create_order():
    logger.info("Creating PayPal order with dynamic cart calculation from Firebase...")
    request_body = request.get_json() or {}
    user_id = request_body.get('userId')
    order_id = request_body.get('orderId')

    if not user_id:
        return jsonify({"message": "User ID is required"}), 400
    
    if not order_id:
        return jsonify({"message": "Order ID is required"}), 400
    
    usuario = Usuarios.query.filter_by(firebase_uid=user_id).first()

    if not usuario:
        return jsonify({"message": "User not found"}), 404
    
    pedido = Pedidos.query.get(order_id)
    if not pedido:
        return jsonify({"message": "Pedido no encontrado"}), 404
    
    # Validar si el pedido pertenece al usuario
    pertenece_usuario = PedidosUsuario.query.filter_by(
        pedido_id=order_id, usuario_id=usuario.usuario_id
    ).first()

    if not pertenece_usuario:
        return jsonify({"message": "No tienes permiso para ver este pedido"}), 403
    
    address_payload = {
        "name": {
            "full_name": pedido.direcciones.nombre_completo
        },
        "address": {
            "address_line_1": pedido.direcciones.calle_principal,
            "address_line_2": pedido.direcciones.calle_secundaria,
            "admin_area_2": pedido.direcciones.ciudad,
            "admin_area_1": pedido.direcciones.provincia,
            "postal_code": pedido.direcciones.codigo_postal,
            "country_code": 'EC'  # Ecuador by default, change as needed
        }
    }

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

    tax_percentage = float(active_tax.porcentaje) / 100  # Convert to fraction

    subtotal = 0
    delivery_fee = 2.00

    for item in items:
        producto_id = item.get('databaseProductId')
        quantity = item.get('quantity', 0)

        if not producto_id or not isinstance(quantity, int) or quantity <= 0:
            return jsonify({"message": f"ID de producto o cantidad inválida en el item: {item}"}), 400

        producto = Productos.query.get(producto_id)
        if not producto:
            return jsonify({"message": f"Producto con ID {producto_id} no encontrado"}), 404

        subtotal += float(producto.precio) * quantity

    calculated_tax = subtotal * tax_percentage
    total = subtotal + calculated_tax + delivery_fee

    # Create PayPal order with calculated total
    try:
        # If you want to keep using paypalserversdk for creation, that's okay:
        from paypalserversdk.api_helper import ApiHelper
        from paypalserversdk.models.checkout_payment_intent import CheckoutPaymentIntent
        from paypalserversdk.models.order_request import OrderRequest
        from paypalserversdk.models.purchase_unit_request import PurchaseUnitRequest

        # NOTE: The snippet below assumes you still have a client that can create orders.
        # If you'd rather do everything via 'requests', you'd do a direct REST call to
        # /v2/checkout/orders. But let's keep your existing create logic for now:
        from api.paypal_client import paypal_client
        orders_controller = paypal_client.orders

        order = orders_controller.orders_create({
            "body": OrderRequest(
                intent=CheckoutPaymentIntent.CAPTURE,
                purchase_units=[
                    PurchaseUnitRequest(
                        amount=AmountWithBreakdown(
                            currency_code='USD',
                            value=f"{total:.2f}",
                            breakdown={
                                "item_total": {"currency_code": "USD", "value": f"{subtotal:.2f}"},
                                "tax_total": {"currency_code": "USD", "value": f"{calculated_tax:.2f}"},
                                "shipping": {"currency_code": "USD", "value": f"{delivery_fee:.2f}"}
                            }
                        ),
                        shipping=address_payload
                    )
                ],
                application_context={
                    "return_url": f"{os.getenv('FRONTEND_URL')}/es/payment/success?userId={user_id}",
                    "cancel_url": f"{os.getenv('FRONTEND_URL')}/es/payment/cancel",
                    "shipping_preference": "SET_PROVIDED_ADDRESS"
                }
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


# =============================================================================
# CAPTURE ORDER (REDIRECT FLOW)
# =============================================================================

@paypal_bp.route("/capture", methods=["GET"])
def capture_redirect():
    """
    This endpoint is triggered by PayPal's return_url after user approves.
    We do a direct REST capture using the official doc approach, then
    update Firebase, etc.
    """
    order_id = request.args.get('token')  # PayPal returns the order ID as 'token'
    user_id = request.args.get('userId')

    if not order_id or not user_id:
        return jsonify({"error": "Missing order ID or user ID"}), 400

    try:
        # Direct capture call to /v2/checkout/orders/<order_id>/capture
        captured_data = capture_order_official(order_id)
        logger.info(f"Order {order_id} captured successfully. Data: {captured_data}")

        # Update Firebase order status
        cart_ref = firebase_db.reference(f'/carts/{user_id}')
        cart_ref.update({"status": "paid"})

        # Redirect to success page with order details
        return redirect(f"{os.getenv('FRONTEND_URL')}/es/payment/success?orderId={order_id}")

    except requests.HTTPError as http_err:
        logger.error(f"PayPal HTTP error capturing order {order_id}: {http_err.response.text}")
        return redirect(f"{os.getenv('FRONTEND_URL')}/es/payment/error?reason=error_http")

    except Exception as e:
        logger.error(f"Error capturing order {order_id}: {e}")
        return redirect(f"{os.getenv('FRONTEND_URL')}/es/payment/error?reason=error")


# =============================================================================
# CAPTURE ORDER (MANUAL CAPTURE / API TRIGGER)
# =============================================================================

@paypal_bp.route("/orders/<order_id>/capture", methods=["POST"])
@paypal_bp.route("/orders/<order_id>/capture", methods=["POST"])
def capture_order(order_id):
    """
    Manual capture endpoint with 'all or nothing' behavior:
      - Capture PayPal order
      - Delete cart in Firebase
      - Update pedido in SQL DB
    If anything fails, the database changes are rolled back and no partial commit occurs.
    """
    logger.info(f"Capturing PayPal order {order_id} via direct REST call...")
    logger.info(f"RAW request.data: {request.data}")
    logger.info(f"RAW request.get_json(silent=True): {request.get_json(silent=True)}")

    try:
        # We start a DB transaction here.
        # Any Exception raised within this 'with' block will cause a rollback.
        with db.session.begin():
            # 1) Capture the order directly
            captured_data = capture_order_official(order_id)
            logger.info(f"Order {order_id} captured successfully. Data: {captured_data}")

            # If PayPal says it's not completed, raise an error to roll back
            if captured_data.get('status') != 'COMPLETED':
                raise ValueError("Order not completed by PayPal")

            # 2) Remove the cart from Firebase
            request_body = request.get_json() or {}
            user_id = request_body.get('userId')
            if not user_id:
                raise ValueError("Missing userId in request body")

            cart_ref = firebase_db.reference(f'/carts/{user_id}')

            # If cart_ref.delete() fails (network, auth, etc.), it will raise an exception
            # which triggers the DB rollback
            cart_ref.delete()

            # 3) Find the user's 'pending' pedido
            user = Usuarios.query.filter_by(firebase_uid=user_id).first()
            if not user:
                raise ValueError("User not found for firebase_uid={}".format(user_id))

            usuario_id = user.usuario_id
            pedidos_usuario = PedidosUsuario.query.filter_by(usuario_id=usuario_id).all()
            pedido_ids = [p.pedido_id for p in pedidos_usuario]

            pedido = Pedidos.query.filter(
                Pedidos.pedido_id.in_(pedido_ids),
                Pedidos.estado_pedido_id == 8  # 'Esperando pago'
            ).first()

            if not pedido:
                raise ValueError(f"No pending pedido (estado=8) found for user_id={user_id}")

            # Extract capture details from the PayPal response
            captures = (captured_data
                        .get("purchase_units", [{}])[0]
                        .get("payments", {})
                        .get("captures", []))

            if not captures:
                raise ValueError("No capture info found in purchase_units->payments->captures")

            first_capture = captures[0]
            payment_id = first_capture.get("id")
            create_time_str = first_capture.get("create_time")
            seller_receivable_breakdown = first_capture.get("seller_receivable_breakdown", {})
            net_amount = seller_receivable_breakdown.get("net_amount", {}).get("value")

            # Convert create_time from UTC -> UTC-5
            if create_time_str:
                parsed_utc = isoparse(create_time_str)
                tz_utc5 = pytz.timezone("Etc/GMT+5")
                local_time = parsed_utc.astimezone(tz_utc5)
                pedido.fecha_pago = local_time
            else:
                # fallback to "now"
                pedido.fecha_pago = datetime.now(pytz.timezone("Etc/GMT+5"))

            pedido.pago_id = payment_id
            pedido.detalles_pago = captured_data
            pedido.estado_pedido_id = 4  # Pagado
            pedido.ingreso_neto = net_amount

            # When we leave the 'with db.session.begin()' block successfully, DB changes commit

        # If we reach here, both the DB commit succeeded AND the Firebase delete succeeded
        return jsonify({"message": "Order captured successfully", "status": captured_data.get('status')}), 200

    except requests.HTTPError as http_err:
        # PayPal returned 4xx/5xx
        logger.error(f"PayPal HTTP error capturing order {order_id}: {http_err.response.text}")
        return jsonify({"error": http_err.response.text}), http_err.response.status_code

    except Exception as e:
        # Any other error -> logs + 500
        logger.error(f"Error capturing order {order_id}: {e}")
        return jsonify({"error": str(e)}), 500

