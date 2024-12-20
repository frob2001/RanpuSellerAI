from flasgger import Swagger

def init_swagger(app):
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": "api_docs",
                "route": "/api/docs.json",
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/api/docs/"
    }
    Swagger(app, config=swagger_config)
