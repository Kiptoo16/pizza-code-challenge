#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

class Restaurants(Resource):
    def get(self):
        restaurants = [n.to_dict() for n in Restaurant.query.all()]

        for hero in restaurants:
            hero.pop('restaurant_pizzas', None)

        return make_response(restaurants, 200)

api.add_resource(Restaurants, "/restaurants")

class RestaurantByID(Resource):
    def get(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()
        if restaurant is None:
            return {"error": "Restaurant not found"}, 404
        
    
        response_dict = {
            'id': restaurant.id,
            'name': restaurant.name,
            'address': restaurant.address,
            'restaurant_pizzas': [
                {
                    'id': rp.id,
                    'pizza_id': rp.pizza_id,
                    'price': rp.price
                } for rp in restaurant.pizzas
            ]
        }
        return make_response(response_dict, 200)
    
    def delete(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()
        if restaurant is None:
            return {"error": "Restaurant not found"}, 404

        db.session.delete(restaurant)
        db.session.commit()
        return {}, 204

api.add_resource(RestaurantByID, "/restaurants/<int:id>")

class Pizzas(Resource):
    def get(self):
        response_dict_list = [n.to_dict() for n in Pizza.query.all()]
        return make_response(response_dict_list, 200)
    
api.add_resource(Pizzas, "/pizzas")

class RestaurantPizzas(Resource):
    def post(self):
        data = request.get_json()
        
        # Validate input data
        price = data.get('price')
        if price is None or not isinstance(price, int):
            return {"errors": ["Price is required and must be an integer"]}, 400
        if price < 1 or price > 30:
            return {"errors": ["Price must be between 1 and 30"]}, 400

        restaurant_pizza = RestaurantPizza(
            pizza_id=data.get('pizza_id'),
            restaurant_id=data.get('restaurant_id'),
            price=price,
        )
        
        db.session.add(restaurant_pizza)
        db.session.commit()
        response_dict = restaurant_pizza.to_dict()
        return make_response(response_dict, 201)

api.add_resource(RestaurantPizzas, "/restaurant_pizzas")

if __name__ == "__main__":
    app.run(port=5555, debug=True)
