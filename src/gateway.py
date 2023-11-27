from auth import get_current_user
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import List, Optional
import json
import hashlib

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

USERS_DB_PATH = 'temp_db/users.json'

# User model for registration
class UserCreate(BaseModel):
    username: str
    password: str


# User model for authentication
class User(BaseModel):
    username: str

class Gateway:
    """A class that manages APIs.

    Attributes:
        order_management: An OrderManagement object.
        payment_processing: A PaymentProcessing object.
        inventory: An Inventory object.
    """

    def __init__(self, order_management, payment_processing, inventory):
        self.order_management = order_management
        self.payment_processing = payment_processing
        self.inventory = inventory

    def create_api(self, app):
        """Creates an API.
        param app: A FastAPI app.
        """

        # Route for user registration
        @app.post("/register", response_model=User)
        def register_user(user: UserCreate):
            # In a real-world scenario, you would hash and salt the password before storing it.
            with open(USERS_DB_PATH, "r") as file:
                try:
                    users = json.load(file)
                except json.JSONDecodeError:
                    users = []

            # Check if the username already exists
            if any(u["username"] == user.username for u in users):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")

            # Hash the password
            hashed_password = hashlib.sha256(user.password.encode()).hexdigest()

            # Add the new user to the database
            new_user = {"username": user.username, "password": hashed_password}
            users.append(new_user)

            # Save the updated user list to the JSON file
            with open(USERS_DB_PATH, "w") as file:
                json.dump(users, file, indent=2)

            return user


        # Route for token generation (authentication)
        @app.post("/token")
        def generate_token(form_data: UserCreate):
            # In a real-world scenario, you would validate the username and password against a database.
            # For simplicity, we'll just check if the user is in our JSON file.
            with open(USERS_DB_PATH, "r") as file:
                users = json.load(file)

            # Hash the provided password for comparison
            hashed_password = hashlib.sha256(form_data.password.encode()).hexdigest()

            for user in users:
                if user["username"] == form_data.username and user["password"] == hashed_password:
                    return {"access_token": user["username"], "token_type": "bearer"}
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        # Login endpoint
        @app.post("/login", response_model=User)
        def login(form_data: UserCreate):
            with open(USERS_DB_PATH, "r") as file:
                try:
                    users = json.load(file)
                except json.JSONDecodeError:
                    users = []

            # Hash the provided password for comparison
            hashed_password = hashlib.sha256(form_data.password.encode()).hexdigest()

            for user in users:
                if user["username"] == form_data.username and user["password"] == hashed_password:
                    return user
            raise HTTPException(status_code=401, detail="Invalid credentials")


        # Protected route that requires authentication
        @app.get("/protected", response_model=User)
        def protected_route(current_user: User = Depends(get_current_user)):
            return current_user


        @app.get('/products')
        def get_products():
            """Returns a list of products."""
            return self.inventory.get_products()

        @app.get('/products/{product_id}')
        def get_product(product_id: int):
            """Returns a product."""
            product = self.inventory.get_product(product_id)
            if product is None:
                return {'message': 'Product not found.'}
            return product

        @app.post('/products')
        def create_product(product: dict):
            """Creates a product."""
            result = self.inventory.create_product(product)
            return {'message': result}

        @app.put('/products/{product_id}')
        def update_product(product_id: int, product: dict):
            """Updates a product."""
            result = self.inventory.update_product(product_id, product)
            return {'message': result}

        @app.delete('/products/{product_id}')
        def delete_product(product_id: int):
            """Deletes a product."""
            result = self.inventory.delete_product(product_id)
            return {'message': result}

        @app.get('/orders')
        def get_orders():
            """Returns a list of orders."""
            return self.order_management.get_orders()

        @app.get('/orders/{order_id}')
        def get_order(order_id: int):
            """Returns an order."""
            order = self.order_management.get_order(order_id)
            if order is None:
                return {'message': 'Order not found.'}
            return order

        @app.post('/orders')
        def create_order(order: dict):
            """Creates an order."""
            result = self.order_management.create_order(order)
            return {'message': result}

        @app.put('/orders/{order_id}')
        def update_order(order_id: int, order: dict):
            """Updates an order."""
            result = self.order_management.update_order(order_id, order)
            return {'message': result}

        @app.delete('/orders/{order_id}')
        def delete_order(order_id: int):
            """Deletes an order."""
            result = self.order_management.delete_order(order_id)
            return {'message': result}

        @app.get('/payments')
        def get_payments():
            """Returns a list of payments."""
            return self.payment_processing.get_payments()

        @app.get('/payments/{payment_id}')
        def get_payment(payment_id: int):
            """Returns a payment."""
            payment = self.payment_processing.get_payment(payment_id)
            if payment is None:
                return {'message': 'Payment not found.'}
            return payment

        @app.post('/payments')
        def create_payment(payment: dict):
            """Creates a payment."""
            result = self.payment_processing.create_payment(payment)
            return {'message': result}

        @app.put('/payments/{payment_id}')
        def update_payment(payment_id: int, payment: dict):
            """Updates a payment."""
            result = self.payment_processing.update_payment(
                payment_id, payment)
            return {'message': result}

        @app.delete('/payments/{payment_id}')
        def delete_payment(payment_id: int):
            """Deletes a payment."""
            result = self.payment_processing.delete_payment(payment_id)
            return {'message': result}
