from firebase_admin import auth
from flask import request, jsonify

def firebase_auth_required(f):
    """
    Middleware to protect endpoints requiring Firebase authentication.
    """
    from functools import wraps

    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Unauthorized: Missing token'}), 401

        token = token.split("Bearer ")[-1]

        try:
            # Verify the Firebase token
            decoded_token = auth.verify_id_token(token)
            request.user = decoded_token
        except Exception as e:
            return jsonify({'error': f'Unauthorized: {str(e)}'}), 401

        return f(*args, **kwargs)

    return decorated_function
