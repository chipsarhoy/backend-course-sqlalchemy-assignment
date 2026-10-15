from flask import jsonify, request

from db import db
from helpers.validate_uuid import validate_uuid
from models.warranty import Warranties

def _format_warranty_response(warranty_query):
    warranty = {
        "warranty_id": warranty_query.warranty_id,
        "product_id": warranty_query.product_id,
        "warranty_months": warranty_query.warranty_months
    }

    return warranty

def add_warranty():
    post_data = request.form if request.form else request.json

    fields = ["product_id", "warranty_months"]
    required_fields = ["product_id", "warranty_months"]
    values = {}

    for field in fields:
        field_data = post_data.get(field)

        if field in required_fields and not field_data:
            return jsonify({"message": f"{' '.join(field.split('_'))} is a required field"})

        values[field] = field_data

    new_warranty = Warranties(product_id=values["product_id"], warranty_months=values["warranty_months"])
    db.session.flush()

    db.session.add(new_warranty)
    db.session.commit()

    warranty_query = db.session.query(Warranties).filter(Warranties.warranty_id == new_warranty.warranty_id).first()

    return jsonify({"message": "warranty created", "result": _format_warranty_response(warranty_query)}), 201


def get_warranty_by_id(warranty_id):

    if validate_uuid(warranty_id):
        return validate_uuid(warranty_id)

    warranty_query = db.session.query(Warranties).filter(Warranties.warranty_id == warranty_id).first()

    if not warranty_query:
        return jsonify({"message": "warranty does not exist"}), 404

    return jsonify({"message": "warranty found", "result": _format_warranty_response(warranty_query)}), 200


def update_warranty_by_id(warranty_id):
    post_data = request.form if request.form else request.json

    if validate_uuid(warranty_id):
        return validate_uuid(warranty_id)

    warranty_query = db.session.query(Warranties).filter(Warranties.warranty_id == warranty_id).first()

    if not warranty_query:
        return jsonify({"message": "warranty does not exist"}), 404

    warranty_query.warranty_months = post_data.get("warranty_months", warranty_query.warranty_months)

    db.session.commit()

    return jsonify({"message": "warranty updated", "result": _format_warranty_response(warranty_query)}), 200


def delete_warranty_by_id(warranty_id):

    if validate_uuid(warranty_id):
        return validate_uuid(warranty_id)

    warranty_query = db.session.query(Warranties).filter(Warranties.warranty_id == warranty_id).first()

    if not warranty_query:
        return jsonify({"message": "warranty does not exist"}), 404

    try:
        db.session.delete(warranty_query)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"message": "unable to delete warranty"}), 400

    return jsonify({"message": "warranty deleted"}), 200