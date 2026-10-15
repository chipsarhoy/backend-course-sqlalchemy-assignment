import uuid
from flask import jsonify

def validate_uuid(id):
    try:
        uuid.UUID(str(id))
    except ValueError:
        return jsonify({"message": "Invalid ID type"}), 400