from flask import jsonify, request

from db import db
from helpers.validate_uuid import validate_uuid
from models.category import Categories
from models.company import Companies
from models.product import Products
from models.warranty import Warranties

def _format_product_response(product_query, company_query, warranty_query=False):

    warranty_dict = {}

    if warranty_query:
        warranty_dict["warranty_id"] = warranty_query.warranty_id
        warranty_dict["warranty_months"] = warranty_query.warranty_months
    
    company_dict = {
        "company_id": company_query.company_id,
        "company_name": company_query.company_name
    }
     
    product_dict = {
        "product_id": product_query.product_id,
        "company": company_dict,
        "product_name": product_query.product_name,
        "description": product_query.description,
        "price": product_query.price,
        "active": product_query.active,
        "categories": [
            {
                "category_id": category.category_id,
                "category_name": category.category_name
            }
        for category in product_query.categories
        ],
        "warranty": warranty_dict if warranty_query else warranty_query
    }
    
    return product_dict

def add_product():
    post_data = request.form if request.form else request.json

    fields = ["company_id", "product_name", "description", "price"]
    required_fields = ["company_id", "product_name", "price"]
    values = {}

    for field in fields:
        field_data = post_data.get(field)

        if field in required_fields and not field_data:
            return jsonify({"message": f"{field} is required"}), 400

        values[field] = field_data

    new_product = Products(company_id=values["company_id"], product_name=values["product_name"], description=values["description"], price=values["price"])

    db.session.add(new_product)
    db.session.commit()

    product_query = db.session.query(Products).filter(Products.product_name == values["product_name"]).first()
    company_query = db.session.query(Companies).filter(Companies.company_id == values["company_id"]).first()

    return jsonify({"messasge": "product created", "result": _format_product_response(product_query, company_query)}), 201


def create_product_category():
    post_data = request.form if request.form else request.json

    fields = ["product_id", "category_id"]
    required_fields = ["product_id", "category_id"]
    values = {}

    for field in fields:
            field_data = post_data.get(field)
    
            if field in required_fields and not field_data:
                return jsonify({"message": f"{field} is required"}), 400
    
            values[field] = field_data
    
    product_query = db.session.query(Products).filter(Products.product_id == values["product_id"]).first()
    category_query = db.session.query(Categories).filter(Categories.category_id == values["category_id"]).first()

    if not product_query:
         return jsonify({"message": "product does not exist"}), 404

    if not category_query:
         return jsonify({"message": "category does not exist"}), 404

    product_query.categories.append(category_query)

    db.session.commit()

    category_list = []
    for category in product_query.categories:
         category_dict = {
              "category_id": category.category_id,
              "category_name": category.category_name
         }

         category_list.append(category_dict)

    company_dict = {
        "company_id": product_query.company.company_id,
        "company_name": product_query.company.company_name
    }

    if product_query.warranty:
        warranty_dict = {
             "warranty_id": product_query.warranty.warranty_id,
             "warranty_months": product_query.warranty.warranty_months
        }
    else:
        warranty_dict = {}

    product_dict = {
        "product_id": product_query.product_id,
        "product_name": product_query.product_name,
        "description": product_query.description,
        "price": product_query.price,
        "active": product_query.active,
        "company": company_dict,
        "categories": category_list,
        "warranty": warranty_dict
    }

    return jsonify({"message": "category added to product", "result": product_dict}), 200

def get_all_products():
    products_query = db.session.query(Products).all()
    products_list = []

    for product in products_query:
        warranty_query = db.session.query(Warranties).filter(Warranties.product_id == product.product_id).first()
        company_query = db.session.query(Companies).filter(Companies.company_id == product.company_id).first()

        products_list.append(_format_product_response(product, company_query, warranty_query))
    
    return jsonify({"message": "products found", "results": products_list}), 200

def get_product_by_id(product_id):

    if validate_uuid(product_id):
        return validate_uuid(product_id)

    product_query = db.session.query(Products).filter(Products.product_id == product_id).first()

    if not product_query:
        return jsonify({"message": "product not found"}), 404

    warranty_query = db.session.query(Warranties).filter(Warranties.product_id == product_id).first()

    company_query = db.session.query(Companies).filter(Companies.company_id == product_query.company_id).first()

    return jsonify({"message": "product found", "result": _format_product_response(product_query, company_query, warranty_query)}), 200
    
def get_active_products():

    product_query = db.session.query(Products).filter(Products.active == True).all()
    products_list = []

    for product in product_query:
        warranty_query = db.session.query(Warranties).filter(Warranties.product_id == product.product_id).first()
        company_query = db.session.query(Companies).filter(Companies.company_id == product.company_id).first()

        products_list.append(_format_product_response(product, company_query, warranty_query))

    return jsonify({"message": "products found", "results": products_list}), 200

def get_products_by_company_id(company_id):

    if validate_uuid(company_id):
        return validate_uuid(company_id)

    company_query = db.session.query(Companies).filter(Companies.company_id == company_id).first()

    if not company_query:
        return jsonify({"message": "company does not exist"}), 404

    product_query = db.session.query(Products).filter(Products.company_id == company_id).all()

    products_list = []

    for product in product_query:
        warranty_query = db.session.query(Warranties).filter(Warranties.product_id == product.product_id).first()

        products_list.append(_format_product_response(product, company_query, warranty_query))

    return jsonify({"message": "products found", "results": products_list}), 200


def update_product_by_id(product_id):
    post_data = request.form if request.form else request.json

    if validate_uuid(product_id):
        return validate_uuid(product_id)
    
    product_query = db.session.query(Products).filter(Products.product_id == product_id).first()

    product_query.product_name = post_data.get("product_name", product_query.product_name) 
    product_query.description = post_data.get("description", product_query.description)
    product_query.price = post_data.get("price", product_query.price)
    product_query.active = post_data.get("active", product_query.active) 

    db.session.commit()

    warranty_query = db.session.query(Warranties).filter(Warranties.product_id == product_id).first()
    company_query = db.session.query(Companies).filter(Companies.company_id == product_query.company_id).first()

    return jsonify({"message": "product updated", "result": _format_product_response(product_query, company_query, warranty_query)})

def delete_product_by_id(product_id):

    if validate_uuid(product_id):
        return validate_uuid(product_id)

    product_query = db.session.query(Products).filter(Products.product_id == product_id).first()

    if not product_query:
        return jsonify({"message": "product does not exist"}), 404

    try:
        db.session.delete(product_query)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"{e}: unable to delete product"}), 400

    return jsonify({"message": "product deleted"}), 200
        