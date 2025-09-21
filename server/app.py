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


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


#--------------------Restful Resources-------------------------------------
class Restaurants(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return [r.to_dict(only=("id", "name", "address")) for r in restaurants], 200


class RestaurantById(Resource):
    def get(self, id):
        r = Restaurant.query.get(id)
        if not r:
            return {"error": "Restaurant not found"}, 404

        # include pizzas through restaurant_pizzas
        restaurant_data = r.to_dict(only=("id", "name", "address"))
        restaurant_data["restaurant_pizzas"] = []
        for rp in r.restaurant_pizzas:
            rp_dict = rp.to_dict()
            rp_dict["pizza"] = rp.pizza.to_dict(only=("id", "name", "ingredients"))
            restaurant_data["restaurant_pizzas"].append(rp_dict)

        return restaurant_data, 200

    def delete(self, id):
        r = Restaurant.query.get(id)
        if not r:
            return {"error": "Restaurant not found"}, 404

        db.session.delete(r)
        db.session.commit()
        return {}, 204


class Pizzas(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return [p.to_dict(only=("id", "name", "ingredients")) for p in pizzas], 200


class RestaurantPizzas(Resource):
    def post(self):
        data = request.get_json()

        price = data.get("price")
        pizza_id = data.get("pizza_id")
        restaurant_id = data.get("restaurant_id")

        pizza = Pizza.query.get(pizza_id)
        restaurant = Restaurant.query.get(restaurant_id)

        if not pizza or not restaurant:
            return {"errors": ["validation errors"]}, 400

        try:
            rp = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
            db.session.add(rp)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {"errors": ["validation errors"]}, 400

        rp_data = rp.to_dict()
        rp_data["pizza"] = pizza.to_dict(only=("id", "name", "ingredients"))
        rp_data["restaurant"] = restaurant.to_dict(only=("id", "name", "address"))
        return rp_data, 201



#-------------------------- Add routes to API---------------------------------------------
api.add_resource(Restaurants, "/restaurants")
api.add_resource(RestaurantById, "/restaurants/<int:id>")
api.add_resource(Pizzas, "/pizzas")
api.add_resource(RestaurantPizzas, "/restaurant_pizzas")
    


if __name__ == "__main__":
    app.run(port=5555, debug=True)
