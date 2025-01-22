import os
from flask import request, jsonify

def validate_origin():
    """
    Middleware to validate the Origin of requests based on environment configuration.
    """
    allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")

    def decorator(f):
        from functools import wraps

        @wraps(f)
        def decorated_function(*args, **kwargs):
            origin = request.headers.get('Origin') or request.headers.get('Referer')
            if not origin or not any(origin.startswith(allowed_origin) for allowed_origin in allowed_origins):
                return jsonify({'error': 'Unauthorized: Invalid origin'}), 403
            return f(*args, **kwargs)

        return decorated_function
    return decorator
