import uuid
from flask import jsonify, request

from db import db
from helpers.validate_uuid import validate_uuid
from models.category import Categories

def _format_category_response(category_query):
    category = {
        "category_id": category_query.category_id,
        "category_name": category_query.category_name,
    }

    return category     

def add_category():
    post_data = request.form if request.form else request.json

    fields = ["category_name"]
    required_fields = ["category_name"]
    values ={}

    for field in fields:
            field_data = post_data.get(field)
    
            if field in required_fields and not field_data:
                return jsonify({"message": f"{field} is required"}), 400
    
            values[field] = field_data
    
    new_category = Categories(category_name=values["category_name"])

    db.session.add(new_category)
    db.session.commit()

    category_query = db.session.query(Categories).filter(Categories.category_name == values["category_name"]).first()

    return jsonify({"messasge": "category created", "results": _format_category_response(category_query)}), 201


def get_all_categories():
    category_query = db.session.query(Categories).all()

    return jsonify({"message": "categories found", "results":  [_format_category_response(category) for category in category_query]}), 200

def get_category_by_id(category_id):

    if validate_uuid(category_id):
        return validate_uuid(category_id)

    category_query = db.session.query(Categories).filter(Categories.category_id == category_id).first()

    if not category_query:
        return jsonify({"message": "category does not exist"}), 404

    return jsonify({"message": "category found", "result": _format_category_response(category_query)}), 200

def update_category_by_id(category_id):
    post_data = request.form if request.form else request.json

    category_name = post_data.get("category_name")

    if not category_name:
        return jsonify({"message": "category name is a required field"}), 400

    if validate_uuid(category_id):
        return validate_uuid(category_id)

    category_query = db.session.query(Categories).filter(Categories.category_id == category_id).first()

    if not category_query:
        return jsonify({"message": "category does not exist"}), 404

    category_query.category_name = post_data.get("category_name", category_query.category_name)

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"message": "unable to update category"}), 400

    return jsonify({"message": "category updated", "result": _format_category_response(category_query)})


def delete_category_by_id(category_id):

    if validate_uuid(category_id):
        return validate_uuid(category_id)
    
    category_query = db.session.query(Categories).filter(Categories.category_id == category_id).first()

    if not category_query:
        return jsonify({"message": "category does not exist"}), 404

    try:
        db.session.delete(category_query)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "unable to delete category"}), 400

    return jsonify({"message": "category deleted"}), 200