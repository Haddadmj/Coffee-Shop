import os
import sys
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

db_drop_and_create_all()

# ROUTES


@app.route('/drinks')
def get_drinks():
    drinks = Drink.query.order_by(Drink.id).all()

    if drinks is None:
        abort(400)

    formatted_drinks = [drink.short() for drink in drinks]

    return jsonify({
        'success': True,
        'drinks': formatted_drinks
    })


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(self):
    drinks = Drink.query.order_by(Drink.id).all()

    if drinks is None:
        abort(400)

    formatted_drinks = [drink.long() for drink in drinks]

    return jsonify({
        'success': True,
        'drinks': formatted_drinks
    })


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink(self):
    body = request.get_json()

    if body is None:
        abort(422)
    title = body.get('title')
    recipe = body.get('recipe')

    if (title is None) or (recipe is None):
        abort(422)

    recipe = json.dumps(recipe)

    try:
        drink = Drink(title=title, recipe=recipe)
        drink.insert()
        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        })
    except:
        print(sys.exc_info())
        abort(422)


@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('post:drinks')
def update_drink(self, id):
    drink = Drink.query.get(id)

    if drink is None:
        abort(404)

    body = request.get_json()

    if body is None:
        abort(422)
    title = body.get('title')
    recipe = body.get('recipe')

    try:
        if title:
            drink.title = title
        elif recipe:
            drink.recipe = json.dumps(recipe)
        drink.update()
    except:
        print(sys.exc_info())
        abort(422)

    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    })


@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(self, id):
    drink = Drink.query.get(id)

    if drink is None:
        abort(404)

    drink.delete()

    return jsonify({
        'success': True,
        'deleted_id': id
    })


# Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resources Not Found"
    }), 404


@app.errorhandler(AuthError)
def handle_auth_error(e):
    response = jsonify(e.error)
    response.status_code = e.status_code
    return response
