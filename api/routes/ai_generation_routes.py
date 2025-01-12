import os
import time
import requests
from datetime import datetime, timedelta, timezone
from flask import Blueprint, request, jsonify, make_response, Response
from flasgger import swag_from
from ..database import db
from ..models.usuarios import Usuarios
from ..models.productos import Productos
from ..models.detalles_productos_ia import DetallesProductosIA
import firebase_admin
from firebase_admin import storage


# Create Blueprint
ai_generation_bp = Blueprint('ai_generation', __name__)

# Retrieve your Meshy.ai API Key from environment variables or config
MESHY_API_KEY = os.getenv('MESHY_API_KEY')
MESHY_BASE_URL = 'https://api.meshy.ai/openapi'

# Headers for Meshy.ai requests
HEADERS = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {MESHY_API_KEY}'
}

@ai_generation_bp.route('/generate-3d-model', methods=['POST'])
@swag_from({
    'tags': ['AI Generation'],
    'summary': 'Generate a 3D model using Meshy.ai',
    'description': (
        'Creates a new 3D model generation job in Meshy.ai. The endpoint can generate '
        'a model from either text or an image prompt. The user must have AI generation '
        'tokens available, and the Meshy.ai API key must have sufficient credits.'
    ),
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'type': {
                        'type': 'string',
                        'enum': ['text', 'image'],
                        'example': 'text',
                        'description': 'Specifies whether to generate a 3D model from text or image.'
                    },
                    'prompt': {
                        'type': 'string',
                        'example': 'A cute puppy sculpture',
                        'description': 'The textual prompt for 3D model generation.'
                    },
                    'image_url': {
                        'type': 'string',
                        'example': 'https://example.com/puppy.jpg',
                        'description': 'A URL to the source image (required when type="image").'
                    },
                    'user_id': {
                        'type': 'string',
                        'example': 'Alkasdhjaskdj123jk',
                        'description': 'The Firebase UID or a unique identifier for the user.'
                    }
                },
                'required': ['type', 'prompt', 'user_id']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'AI generation task created successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {
                        'type': 'string',
                        'example': 'AI generation task created'
                    },
                    'job_id': {
                        'type': 'string',
                        'example': 'abc123',
                        'description': 'The ID of the Meshy.ai job that was created.'
                    }
                }
            }
        },
        400: {
            'description': 'Invalid input data or insufficient tokens/credits',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'No credits available'
                    }
                }
            }
        },
        404: {
            'description': 'User not found in the system',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {
                        'type': 'string',
                        'example': 'Usuario no encontrado'
                    }
                }
            }
        }
    }
})
def generate_3d_model():
    """
    Generate a 3D model either from text or image using Meshy.ai API.
    Returns a JSON with the Meshy.ai job ID, plus the .stl and .glb URLs.
    """
    data = request.get_json()

    # Extract fields from incoming JSON
    generation_type = data.get('type')  # 'text' or 'image'
    prompt = data.get('prompt')
    image_url = data.get('image_url', None)
    userId = data.get('user_id', None)

    # Basic validation
    if not generation_type or generation_type not in ['text', 'image']:
        return jsonify({'error': 'type must be either "text" or "image"'}), 400
    if not userId:
        return jsonify({'error': 'user_id is required'}), 400
    if generation_type == 'text' and not prompt:
        return jsonify({'error': 'prompt is required'}), 400
    if generation_type == 'image' and not image_url:
        return jsonify({'error': 'image_url is required when type="image"'}), 400

    # Decide which Meshy.ai endpoint to call
    if generation_type == 'text':
        url = f'{MESHY_BASE_URL}/v2/text-to-3d'
        payload = {
            'mode': 'preview',
            'prompt': f'{prompt}. Keep the model 3D printable (single piece)',
            'art-style': "realistic",
            'topology': 'quad'
        }
    else:  # generation_type == 'image'
        url = f'{MESHY_BASE_URL}/v1/image-to-3d'
        payload = {
            'image_url': image_url,
            'topology': 'quad',
            'should_texture': False
        }

    # Verify that a user has ai gen tokens
    user = Usuarios.query.filter_by(firebase_uid=userId).first()

    if not user:
        return jsonify({"message": "Usuario no encontrado"}), 404
    
    if user.ai_gen_tokens == 0:
        return jsonify({"message": "Usuario no tiene tokens para generar productos con IA"}), 507

    # Verify that the api key has credits
    try:
        response = requests.get(
            "https://api.meshy.ai/openapi/v1/balance",
            headers=HEADERS,
        )
        response.raise_for_status()
        balance_info = response.json()
        balance = balance_info.get('balance')

        if not balance:
            return jsonify({'error': 'No balance returned from Meshy.ai'}), 400

        if balance <= 10:
            return jsonify({'error': 'No credits available'}), 400
        
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 400


    # Create the meshy ai task
    try:
        # 1. Submit the job to Meshy.ai
        response = requests.post(url, json=payload, headers=HEADERS, timeout=120)
        response.raise_for_status()
        job_info = response.json()
        job_id = job_info.get('result')

        if not job_id:
            return jsonify({'error': 'No job ID returned from Meshy.ai'}), 400

        return jsonify({
            'message': 'AI generation task created',
            'job_id': job_id,
        }), 200

    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 400
    except Exception as ex:
        return jsonify({'error': str(ex)}), 400

def upload_to_firebase(file_content, file_name):
    """Upload a file to Firebase Storage and return the public URL."""
    try:
        bucket = storage.bucket()
        blob = bucket.blob(f"ai-generated-files/{file_name}")
        blob.upload_from_string(file_content, content_type="model/gltf-binary")
        blob.make_public()  # Make the file publicly accessible
        return blob.public_url
    except Exception as e:
        raise Exception(f"Failed to upload file to Firebase Storage: {str(e)}")

@ai_generation_bp.route('/finalize-3d-model', methods=['POST'])
@swag_from({
    'tags': ['AI Generation'],
    'summary': 'Finalize a completed 3D model generation',
    'description': (
        'This endpoint should be called once the model generation task has '
        'succeeded in Meshy.ai. It will decrement the user’s AI generation token '
        'and optionally allow for any additional business logic.'
    ),
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'user_id': {
                        'type': 'string',
                        'example': 'Alkasdhjaskdj123jk',
                        'description': 'Firebase UID or other unique user identifier.'
                    },
                    'job_id': {
                        'type': 'string',
                        'example': 'abc123',
                        'description': 'The job ID returned when the task was created.'
                    }
                },
                'required': ['user_id', 'job_id']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Task finalized successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'job_id': {'type': 'string'}
                }
            }
        },
        400: {'description': 'Bad request or insufficient tokens'},
        404: {'description': 'User not found'}
    }
})
def finalize_3d_model():
    """
    Finalize a completed 3D model generation.

    Once the model's status is 'succeeded' on Meshy.ai (progress=100),
    the frontend calls this endpoint to notify the backend that the generation
    is done. We subtract one from the user's AI generation tokens. In the future,
    you could also add logic to download and store the final .stl/.glb files,
    update the database with model info, etc.
    """
    # 1. Parse JSON from request
    data = request.get_json()
    user_id = data.get('user_id')
    job_id = data.get('job_id')
    nombre = data.get('nombre')
    detalles = data.get('detalles')
    generation_type = data.get('generation_type')

    # 2. Basic validations
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    if not job_id:
        return jsonify({'error': 'job_id is required'}), 400
    if not nombre:
        return jsonify({'error': 'nombre is required'}), 400
    if not detalles:
        return jsonify({'error': 'detalles is required'}), 400
    if not generation_type:
        return jsonify({'error': 'generation_type is required'}), 400
    
    # 3. Check if job_id doesnt already exist
    existing_detail = DetallesProductosIA.query.filter_by(origin_task_id=job_id).first()
    if existing_detail:

        existing_product = Productos.query.filter_by(producto_id=existing_detail.producto_id).first()

        return jsonify({
            "message": "AI product details already created for this job",
            "producto_id": existing_product.producto_id,
            "gbl": existing_product.gbl,
            'job_id': job_id,
        }), 200

    # 4. Check if user exists
    user = Usuarios.query.filter_by(firebase_uid=user_id).first()
    if not user:
        return jsonify({"message": "Usuario no encontrado"}), 404

    # 5. Check if user has AI tokens left
    if user.ai_gen_tokens <= 0:
        return jsonify({"message": "Usuario no tiene tokens para generar productos con IA"}), 400

    # 6. Subtract one token from the user
    user.ai_gen_tokens -= 1
    
    # 7. Get task data
    if generation_type == 'text':
        status_url = f'{MESHY_BASE_URL}/v2/text-to-3d/{job_id}'
    else:  # generation_type == 'image'
        status_url = f'{MESHY_BASE_URL}/v1/image-to-3d/{job_id}'

    try:
        # 1. GET request to Meshy.ai to retrieve the job's current status
        response = requests.get(status_url, headers=HEADERS, timeout=60)
        response.raise_for_status()

        # 2. Parse the JSON response
        job_info = response.json()
        
        if job_info.get('status') != 'SUCCEEDED':
            return jsonify({'error': 'Job has not succeeded yet'}), 400

        # Extract URLs from the remesh job
        glb_url = job_info.get('model_urls', {}).get('glb')
        obj_url = job_info.get('model_urls', {}).get('obj')

        # Download the GLB file
        glb_response = requests.get(glb_url)
        glb_response.raise_for_status()

        if not glb_url or not obj_url:
            return jsonify({'error': 'Could not retrieve GLB or OBJ URLs'}), 400

        firebase_glb_url = upload_to_firebase(
            glb_response.content, f"model_{job_id}.glb"
        )

    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 400
    except Exception as ex:
        return jsonify({'error': str(ex)}), 400

    # 8. Create a new product
    new_product = Productos(
        nombre=nombre,
        descripcion='Producto generado por IA',
        alto=None,  # Empty for now
        ancho=None,  # Empty for now
        largo=None,  # Empty for now
        gbl=firebase_glb_url,
        precio=None,  # Empty for now
        categoria_producto_id=3  # Fixed category
    )
    db.session.add(new_product)
    db.session.flush()  # Flush to get the new product ID

    # Calculate expiration date (2 days from now)
    expiration_date = datetime.now(timezone.utc) + timedelta(days=2)

    # 9. Add AI product details
    ai_product_details = DetallesProductosIA(
        producto_id=new_product.producto_id,
        detalles=detalles,
        time_to_die=expiration_date,
        is_in_cart=False,
        is_in_order=False,
        obj_downloadable_url=obj_url,
        url_expiring_date=expiration_date,
        origin_task_id=job_id
    )
    db.session.add(ai_product_details)

    # 10. Commit changes to the database
    try:
        db.session.commit()
        return jsonify({
            "message": "Product and AI details saved successfully",
            "producto_id": new_product.producto_id,
            "gbl": firebase_glb_url,
            'job_id': job_id,
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f"Failed to save product: {str(e)}"}), 500

@ai_generation_bp.route('/get-model-status', methods=['POST'])
@swag_from({
    'tags': ['AI Generation'],
    'summary': 'Get the status of a Meshy.ai job (text or image)',
    'description': (
        'Fetches the current status and progress of a Meshy.ai 3D generation job. '
        'You must provide the job type (`text` or `image`) and the Meshy.ai job ID.'
    ),
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'type': {
                        'type': 'string',
                        'enum': ['text', 'image'],
                        'example': 'text',
                        'description': 'Specifies whether the job is text-to-3D or image-to-3D.'
                    },
                    'job_id': {
                        'type': 'string',
                        'example': 'abc123',
                        'description': 'The Meshy.ai job ID to check.'
                    }
                },
                'required': ['type', 'job_id']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Current job status retrieved successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string', 'example': 'succeeded'},
                    'progress': {'type': 'integer', 'example': 100}
                }
            }
        },
        400: {
            'description': 'Missing job_id/type or Meshy.ai error',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        }
    }
})
def get_model_status():
    """
    Fetches the current status and progress of a Meshy.ai job (text or image).
    
    Expects a POST request with a JSON body containing:
    {
      "type": "<text or image>",
      "job_id": "<Meshy.ai job ID>"
    }

    For 'text' tasks, it queries /openapi/v2/text-to-3d/<job_id>.
    For 'image' tasks, it queries /openapi/v1/image-to-3d/<job_id>.
    Returns { "status": "<status>", "progress": <number> } if successful.
    """
    data = request.get_json()
    generation_type = data.get('type')
    job_id = data.get('job_id')

    # Validation
    if not generation_type or generation_type not in ['text', 'image']:
        return jsonify({'error': 'type must be either "text" or "image"'}), 400
    if not job_id:
        return jsonify({'error': 'job_id is required'}), 400

    # Decide the correct Meshy.ai endpoint
    if generation_type == 'text':
        status_url = f'{MESHY_BASE_URL}/v2/text-to-3d/{job_id}'
    else:  # generation_type == 'image'
        status_url = f'{MESHY_BASE_URL}/v1/image-to-3d/{job_id}'

    try:
        # 1. GET request to Meshy.ai to retrieve the job's current status
        response = requests.get(status_url, headers=HEADERS, timeout=60)
        response.raise_for_status()

        # 2. Parse the JSON response
        job_info = response.json()
        status = job_info.get('status')
        progress = job_info.get('progress')

        if status is None or progress is None:
            return jsonify({'error': 'Could not retrieve status or progress from Meshy.ai'}), 400

        # 3. Return the status and progress
        return jsonify({
            'status': status,
            'progress': progress
        }), 200

    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 400
    except Exception as ex:
        return jsonify({'error': str(ex)}), 400

