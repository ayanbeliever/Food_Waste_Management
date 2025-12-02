from app.db import get_db
from datetime import datetime
from pymongo import ReturnDocument

class User:
    user_collection = get_db().get_collection('users')

    @staticmethod
    def create_user(name, email, phone, password_hash, role='customer'):
        """Create a new user in the database."""
        user_data = {
            'name': name,
            'email': email,
            'phone': phone,
            'password': password_hash,
            'role': role,
            'restaurant_ids': [],
            'favourites': [],
            'notifications': [],
            'loyalty_points': 0,
            'last_seen': datetime.utcnow(),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        result = User.user_collection.insert_one(user_data)
        return str(result.inserted_id)
        
    @staticmethod
    def find_by_email(email):
        """Find a user by email."""
        return User.user_collection.find_one({'email': email})
    
    @staticmethod
    def find_by_id(user_id):
        """Find a user by their ID."""
        return User.user_collection.find_one({'_id': user_id})
    
    @staticmethod
    def find_one_and_update(filter_query, update_data, return_document=False):
        """Find one user and update their data."""
        return User.user_collection.find_one_and_update(
            filter_query,
            {'$set': update_data},
            return_document=ReturnDocument.AFTER if return_document else ReturnDocument.BEFORE
        )
    
    @staticmethod
    def update_last_seen(user_id):
        """Update the last seen timestamp for a user."""
        User.user_collection.update_one(
            {'_id': user_id},
            {'$set': {'last_seen': datetime.utcnow()}}
        )