from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)

class Restaurant(db.Model, SerializerMixin):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)

    restaurant_pizzas = db.relationship(
        "RestaurantPizza", back_populates="restaurant", cascade="all, delete-orphan"
    )

    serialize_rules = ("-restaurant_pizzas.restaurant",)


class Pizza(db.Model, SerializerMixin):
    __tablename__ = "pizzas"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    ingredients = db.Column(db.String, nullable=False)

    restaurant_pizzas = db.relationship(
        "RestaurantPizza", back_populates="pizza", cascade="all, delete-orphan"
    )

    serialize_rules = ("-restaurant_pizzas.pizza",)


class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = "restaurant_pizzas"

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)

    # 🔑 FOREIGN KEYS
    pizza_id = db.Column(db.Integer, db.ForeignKey("pizzas.id"), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurants.id"), nullable=False)

    # relationships
    pizza = db.relationship("Pizza", back_populates="restaurant_pizzas")
    restaurant = db.relationship("Restaurant", back_populates="restaurant_pizzas")

    serialize_rules = ("-pizza.restaurant_pizzas", "-restaurant.restaurant_pizzas")
   
    # add validation
    @validates("price")
    def validate_price(self, key, value):
        if value is None:
            raise ValueError("price must be provided")
        if not isinstance(value, int):
            raise ValueError("price must be an integer")
        if value < 1 or value > 30:
            raise ValueError("price must be between 1 and 30")
        return value


    def __repr__(self):
        return f"<RestaurantPizza ${self.price}>"
