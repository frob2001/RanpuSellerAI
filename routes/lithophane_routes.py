from flask import Blueprint, request, send_file
from services import apply_lithophane_no_light, apply_lithophane_with_light
from PIL import Image
import io

lithophane_bp = Blueprint('lithophane', __name__)

@lithophane_bp.route('/convert/no-light', methods=['POST'])
def convert_image_no_light():
    if 'image' not in request.files:
        return {"error": "No image file provided"}, 400

    # Leer la imagen del archivo enviado
    image_file = request.files['image']
    image = Image.open(image_file)

    # Aplicar filtro sin luz
    no_light_image = apply_lithophane_no_light(image)

    # Guardar la imagen en memoria
    img_io = io.BytesIO()
    no_light_image.save(img_io, 'PNG')
    img_io.seek(0)

    return send_file(img_io, mimetype='image/png')

@lithophane_bp.route('/convert/with-light', methods=['POST'])
def convert_image_with_light():
    if 'image' not in request.files:
        return {"error": "No image file provided"}, 400

    # Leer la imagen del archivo enviado
    image_file = request.files['image']
    image = Image.open(image_file)

    # Aplicar filtro con luz
    with_light_image = apply_lithophane_with_light(image)

    # Guardar la imagen en memoria
    img_io = io.BytesIO()
    with_light_image.save(img_io, 'PNG')
    img_io.seek(0)

    return send_file(img_io, mimetype='image/png')