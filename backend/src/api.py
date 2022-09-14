from importlib.metadata import requires
import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the database
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this function will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks')
def get_drinks():
    all_drinks = Drink.query.order_by(Drink.id).all()
    
    if len(all_drinks) == 0:
        abort(404)
        
    drinks = [drink.short() for drink in all_drinks]
    
    return jsonify(
        {
            "success": True,
            "drinks": drinks
        }
    ),200

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail():
    all_drinks = Drink.query.order_by(Drink.id).all()
    
    if len(all_drinks) == 0:
        abort(404)
        
    drinks = [drink.long() for drink in all_drinks]
    
    return jsonify(
        {
            "success": True,
            "drinks": drinks
        }
    ),200

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drinks():
    body = request.get_json()
    
    new_title = body.get("title", None)
    new_recipe = body.get("recipe", None)
    
    if new_title == "" or new_recipe == "":
        abort(422)
        
    try:
        new_drink = Drink(title=new_title, recipe=new_recipe)
        new_drink.insert()
        
        created_drink = Drink.query.filter(Drink.id==new_drink.id).one_or_none()
        drink = created_drink.long()
        
        return jsonify(
            {
                "success": True,
                "drinks": drink
            }
        ), 200
        
    except:
        abort(422)
        
'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<int: drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(drink_id):
    get_drink = Drink.query.filter_by(id == drink_id).one_or_none()
    
    if get_drink.id is None:
        abort(404)
        
    body = request.get_json()
    edited_title = body.get('title', None)
    edited_recipe = body.get('recipe', None)
    
    try:
        get_drink.title = edited_title
        get_drink.recipe = edited_recipe
        get_drink.update()
        
        updated_drink = Drink.query.filter(Drink.id==get_drink.id).one_or_none()
        drink = updated_drink.long()
        
        return jsonify(
            {
                "success": True,
                "drinks": drink
            }
        ), 200
        
    except:
        abort(422)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<int:drink_id>')
@requires_auth('delete:drinks')
def delete_drink(drink_id):
    get_drink = Drink.query.filter_by(id == drink_id).one_or_none()
    
    if get_drink.id is None:
        abort(404)
        
    try:
        get_drink.delete()
        return jsonify(
            {
                "success": True,
                "delete": get_drink.id
            }
        ),200
        
    except:
        abort(422)


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with appropriate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
