from .usuarios_routes import usuarios_bp
from .estados_pedidos_routes import estados_pedidos_bp
from .impuestos_routes import impuestos_bp
from .direcciones_routes import direcciones_bp
from .pedidos_routes import pedidos_bp

# Exportamos cada Blueprint explícitamente
__all__ = ["usuarios_bp", "estados_pedidos_bp", "impuestos_bp", "direcciones_bp", "pedidos_bp"]