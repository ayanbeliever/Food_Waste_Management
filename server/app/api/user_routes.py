from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

from app.models.User import User

user_bp = Blueprint('user', __name__)

def _sanitize_user_data(user):
    """Remove sensitive information from user data before sending it in a response."""
    if not user:
        return None
    user.pop('password', None)
    user.pop('_id', None)
    return user

@user_bp.route('/profile', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def get_profile():
    try:
        if request.method == 'GET':
            user_id = get_jwt_identity()
            user = User.find_by_id(ObjectId(user_id))
            if not user:
                return jsonify({'message': 'User not found'}), 404
            return jsonify({'user': _sanitize_user_data(user)}), 200
        elif request.method == 'PUT':
            user_id = get_jwt_identity()
            data = request.get_json()
            name = data.get('name', None)
            phone = data.get('phone', None)

            update_data = {}
            if name:
                update_data['name'] = name
            if phone:
                update_data['phone'] = phone

            if not update_data:
                return jsonify({'message': 'No data to update'}), 400

            update_data['updated_at'] = datetime.utcnow()
            
            updated_user = User.find_one_and_update(
                {'_id': ObjectId(user_id)}, 
                update_data,
                return_document=True
            )

            if not updated_user:
                return jsonify({'message': 'User not found'}), 404

            return jsonify({'message': 'Profile updated', 'user': _sanitize_user_data(updated_user)}), 200
    except Exception as e:
        return jsonify({'error': f"Internal Server Error : {str(e)}"}), 500