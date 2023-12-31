from auth import get_current_user
from fastapi import FastAPI, HTTPException, Depends, status, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import json
import hashlib

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

USERS_DB_PATH = 'temp_db/users.json'

def read_cart_data():
    # Read cart data from the JSON file
    with open("temp_db/cart.json", "r") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return {}

def save_cart_data(cart_data):
    # Save cart data to the JSON file
    with open("temp_db/cart.json", "w") as file:
        json.dump(cart_data, file)

# User model for registration
class UserCreate(BaseModel):
    username: str
    password: str


# User model for authentication
class User(BaseModel):
    username: str

class CartRequest(BaseModel):
    username: str

class CartUpdate(BaseModel):
    username: str
    item_id: int

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


        @app.post("/cart", response_model=List[int])
        async def get_cart(cart_request: CartRequest):
            username = cart_request.username

            # Read cart data from the JSON file
            cart_data = read_cart_data()

            if username in cart_data:
                user_item_ids = cart_data[username]
            else:
                raise HTTPException(status_code=404, detail="User not found or cart is empty.")

            user_cart = user_item_ids

            return user_cart

        @app.put("/cart", response_model=List[int])
        async def add_to_cart(cart_request: CartUpdate):
            username = cart_request.username
            item_id = cart_request.item_id
            # Read cart data from the JSON file
            cart_data = read_cart_data()

            if not username in cart_data:
                cart_data[username] = []

            # Retrieve the user's existing item IDs or create an empty list if it doesn't exist
            cart_data[username].append(item_id)

            # Save the updated cart data to the JSON file
            save_cart_data(cart_data)

            # Return the updated cart
            user_cart = cart_data[username]

            return user_cart

        @app.delete("/cart", response_model=List[int])
        async def remove_from_cart(cart_request: CartUpdate):
            username = cart_request.username
            item_id = cart_request.item_id

            cart_data = read_cart_data()

            if not username in cart_data:
                cart_data[username] = []
            
            cart_data[username] = [item for item in cart_data[username] if item != item_id]

            save_cart_data(cart_data)

            user_cart = cart_data[username]

            return user_cart
            
        

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

        @app.post("/auth")
        def isadmin(user1: dict):
            with open(USERS_DB_PATH, "r") as file:
                users = json.load(file)
            
            for user in users:
                if user["username"] == user1["username"]:
                    if user["admin"] == "true":
                        return {"admin": "true"}
            
            return {"admin": "false"}

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
