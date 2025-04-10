# yookassa_handler.py
from yookassa import Payment
from config import YOOKASSA_API_KEY, YOOKASSA_SHOP_ID, PREMIUM_PRICE

Payment.account_id = YOOKASSA_SHOP_ID
Payment.secret_key = YOOKASSA_API_KEY

def create_payment_link(user_id):
    payment = Payment.create({
        "amount": {
            "value": str(PREMIUM_PRICE),
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": f"https://t.me/SeoTextGen4bot?start=paid_{user_id}"
        },
        "capture": True,
        "description": f"Премиум-доступ для пользователя {user_id}",
        "metadata": {
            "user_id": str(user_id)
        }
    })
    return payment.confirmation.confirmation_url
