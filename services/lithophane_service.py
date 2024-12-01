from PIL import Image, ImageOps, ImageEnhance, ImageDraw, ImageFilter

# Función para aplicar la litofanía sin luz (como un dibujo a mano con trazos negros sutiles)
def apply_lithophane_no_light(image):
    """
    Simula una litofanía sin luz de fondo, con trazos negros sutiles, similar a un dibujo a mano.
    """
    # Convertir a escala de grises
    grayscale = ImageOps.grayscale(image)

    # Aplicar un filtro de detección de bordes para resaltar contornos
    edges = grayscale.filter(ImageFilter.FIND_EDGES)

    # Invertir los colores para que los bordes sean negros sobre un fondo blanco
    inverted = ImageOps.invert(edges)

    # Aclarar la imagen para hacer los trazos más sutiles
    brightness_enhancer = ImageEnhance.Brightness(inverted)
    very_bright = brightness_enhancer.enhance(1.5)

    # Reducir el contraste para que los trazos sean apenas visibles
    contrast_enhancer = ImageEnhance.Contrast(very_bright)
    low_contrast = contrast_enhancer.enhance(0.5)

    return low_contrast


def apply_lithophane_with_light(image):
    """
    Simula una litofanía con luz de fondo, creando un degradado circular amarillo desde el centro.
    """
    # Convertir a escala de grises
    grayscale = ImageOps.grayscale(image)

    # Aumentar brillo para un efecto de luz de fondo
    enhancer = ImageEnhance.Brightness(grayscale)
    brighter = enhancer.enhance(1.5)

    # Obtener tamaño de la imagen
    width, height = brighter.size

    # Crear un degradado radial que comienza amarillo en el centro y se aclara hacia los bordes
    gradient = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(gradient)

    center_x, center_y = width // 2, height // 2
    max_radius = (width**2 + height**2) ** 0.5

    for y in range(height):
        for x in range(width):
            # Calcular la distancia del pixel al centro
            distance_to_center = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
            # Calcular el factor de degradado (entre 1.0 y 0.0)
            gradient_factor = 1.0 - (distance_to_center / max_radius)
            gradient_factor = max(0, gradient_factor)  # Asegurarse de que esté entre 0 y 1

            # Mezclar entre amarillo y blanco
            r = int(255 * gradient_factor + 255 * (1 - gradient_factor))
            g = int(255 * gradient_factor + 255 * (1 - gradient_factor))
            b = int(0 * gradient_factor + 255 * (1 - gradient_factor))

            draw.point((x, y), (r, g, b))

    # Combinar la imagen aclarada con el degradado para simular la luz en el centro
    combined = Image.blend(brighter.convert('RGB'), gradient, alpha=0.5)

    return combined