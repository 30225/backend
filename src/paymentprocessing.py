import json


class PaymentProcessing:
    """A class that processes payment_data.

    Attributes:
        payment_data: A dictionary of payment data.

    Payment JSON format:
        {
            "id": "1234567890",
            "amount": 100.00,
            "currency": "USD",
            "type": "credit_card",
            "timestamp": "2019-01-01T12:00:00Z"
        }
    """

    def __init__(self):
        data = open("temp_db/payments.json", "r")
        self.payment_data = json.load(data)

    def save_payments(self):
        """Saves the payment_data to a file."""
        with open("temp_db/payments.json", "w") as outfile:
            json.dump(self.payment_data, outfile)

    def get_payment(self, payment_id):
        """Gets a payment by ID.

        Args:
            payment_id: The ID of the payment to get.

        Returns:
            The payment data.
        """
        for existing_payment in self.payment_data["payments"]:
            if existing_payment["id"] == payment_id:
                return existing_payment
        return "Payment not found"

    def get_payments(self):
        """Gets all payment_data.

        Returns:
            A list of payment_data.
        """
        return self.payment_data["payments"]

    def create_payment(self, payment):
        """Adds a payment.

        Args:
            payment: The payment to add.
        """
        for existing_payment in self.payment_data["payments"]:
            if existing_payment["id"] == payment["id"]:
                return "Payment already exists"

        self.payment_data["payments"].append(payment)
        self.save_payments()
        return "Payment added"

    def update_payment(self, payment_id, payment):
        """Updates a payment.

        Args:
            payment_id: The ID of the payment to update.
            payment: The payment data.
        """
        for i, existing_payment in enumerate(self.payment_data["payments"]):
            if existing_payment["id"] == payment_id:
                self.payment_data["payments"][i] = payment
                self.save_payments()
                return "Payment updated"
        return "Payment not found"

    def delete_payment(self, payment_id):
        """Deletes a payment.

        Args:
            payment_id: The ID of the payment to delete.
        """
        for i, existing_payment in enumerate(self.payment_data["payments"]):
            if existing_payment["id"] == payment_id:
                del self.payment_data["payments"][i]
                self.save_payments()
                return "Payment deleted"
        return "Payment not found"
