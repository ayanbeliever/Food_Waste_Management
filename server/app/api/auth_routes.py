from flask import Blueprint, current_app, make_response, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.User import User
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token, 
    jwt_required, 
    get_jwt_identity,
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies
)
from datetime import timedelta

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        if request.method != 'POST':
            return jsonify({'error': 'Method not allowed'}), 405
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone', None)
        password = data.get('password')
        role = data.get('role', 'customer')

        if not name or not email or not password:
            return jsonify({'message': 'All fields are required'}), 400

        if User.find_by_email(email):
            return jsonify({'message': 'User already exists'}), 400

        user_id = User.create_user(name, email, phone, generate_password_hash(password), role)
        return jsonify({'message': 'User created', 'user_id': user_id}), 201
    except Exception as e:
        return jsonify({'error': f"Internal Server Error : {str(e)}"}), 500
    
@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        if request.method != 'POST':
            return jsonify({'error': 'Method not allowed'}), 405
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        user = User.find_by_email(email)
        if not user or not check_password_hash(user['password'], password):
            return jsonify({'message': 'Invalid credentials'}), 401

        access_token, refresh_token = jwt_tokens_generation(user['_id'])

        response = make_response(jsonify({'message': 'Login successful'}), 200)
        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)

        return response
    except Exception as e:
        return jsonify({'error': f"Internal Server Error : {str(e)}"}), 500
    
@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    try:
        identity = get_jwt_identity()
        access_token = create_access_token(identity=identity, expires_delta=timedelta(seconds=current_app.config['JWT_ACCESS_TOKEN_EXPIRES']))
        response = make_response(jsonify({'message': 'Token refreshed'}), 200)
        set_access_cookies(response, access_token)
        return response
    except Exception as e:
        return jsonify({'error': f"Internal Server Error : {str(e)}"}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    try:
        identity = get_jwt_identity()
        user = User.find_by_id(identity)
        if not user:
            return jsonify({"msg": "User not found"}), 404
        # remove sensitive fields
        user.pop('password', None)
        user['_id'] = str(user['_id'])
        return jsonify(user), 200
    except Exception as e:
        return jsonify({'error': f"Internal Server Error : {str(e)}"}), 500
    
@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    try:
        response = make_response(jsonify({'message': 'Logout successful'}), 200)
        unset_jwt_cookies(response)
        return response
    except Exception as e:
        return jsonify({'error': f"Internal Server Error : {str(e)}"}), 500


def jwt_tokens_generation(user_id):
    access_token = create_access_token(identity=str(user_id), expires_delta=timedelta(seconds=current_app.config['JWT_ACCESS_TOKEN_EXPIRES']))
    refresh_token = create_refresh_token(identity=str(user_id), expires_delta=timedelta(seconds=current_app.config['JWT_REFRESH_TOKEN_EXPIRES']))
    return access_token, refresh_token