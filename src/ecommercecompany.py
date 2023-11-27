from fastapi import FastAPI
import uvicorn
from starlette.middleware.cors import CORSMiddleware


class ECommerceCompany:
    """An e-commerce company.

    Attributes:
        customer_data: A dictionary of customer data.
        product_data: A dictionary of product data.
    """

    def __init__(self, gateway):
        self.gateway = gateway

    def main(self):
        """Starts the e-commerce company."""
        # Create the FastAPI app.
        app = FastAPI()
        app.add_middleware(
            CORSMiddleware,
            allow_origins=['https://angel-fenix-front.onrender.com'],
            allow_credentials=True,
            allow_methods=['*'],
            allow_headers=['*'],
        )
        self.gateway.create_api(app)

        # Run the FastAPI app.
        uvicorn.run(app, host='0.0.0.0', port=8000)
