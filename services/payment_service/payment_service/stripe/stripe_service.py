import random
import stripe
from payment_service import models

stripe.api_key = "stripe_secret_key"

async def create_payment(payment_request: models.PaymentRequest):
    result = random_boolean()
    if result:
        return models.PaymentResponse(
            payment_status="success",
            message="Payment Successful",
        )
    else:
         return models.PaymentResponse(
            payment_status="failed",
            message="Payment Failed",
        )




def random_boolean():
    return random.random() < 0.9