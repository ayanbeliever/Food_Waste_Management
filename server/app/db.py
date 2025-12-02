from pymongo import MongoClient

_client = None
_db = None

def init_db(app):
    """Initialize Mongo client and attach to app context"""
    global _client, _db
    mongo_uri = app.config['MONGO_URI']
    mongo_db_name = app.config.get('MONGO_DB_NAME', 'food_waste_db')
    _client = MongoClient(mongo_uri)
    _db = _client[mongo_db_name]

    # @app.teardown_appcontext
    # def _close_db(exc):
    #     global _client, _db
    #     if _client is not None:
    #         _client.close()
    #         _client = None
    #         _db = None

def get_db():
    """Get the Mongo database instance"""
    global _db
    if _db is None:
        raise RuntimeError("Database not initialized. Call init_db(app) first.")
    return _db