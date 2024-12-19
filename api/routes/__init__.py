from .usuarios_routes import usuarios_bp
from .estados_pedidos_routes import estados_pedidos_bp

# Exportamos cada Blueprint explícitamente
__all__ = ["usuarios_bp", "estados_pedidos_bp"]
