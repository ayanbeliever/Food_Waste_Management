from flask import Flask
from app.config import Config
from app.db import init_db
from flask_cors import CORS
from flask_jwt_extended import JWTManager

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    init_db(app)

    CORS(app, supports_credentials=True)
    jwt = JWTManager(app)

    from app.api.auth_routes import auth_bp
    from app.api.user_routes import user_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/user')

    return app