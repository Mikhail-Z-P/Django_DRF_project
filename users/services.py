import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_product(name, description=""):
    """Создаёт продукт в Stripe и возвращает его ID."""
    product = stripe.Product.create(name=name, description=description)
    return product.id


def create_price(product_id, amount):
    """Создаёт цену в Stripe. Amount передаётся в копейках."""
    price = stripe.Price.create(
        product=product_id,
        unit_amount=amount,
        currency="rub",
    )
    return price.id


def create_checkout_session(price_id, success_url, cancel_url):
    """Создаёт Stripe Checkout Session и возвращает session_id и URL."""
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price": price_id,
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url,
    )
    return {"session_id": session.id, "payment_url": session.url}


def retrieve_session(session_id):
    """Получает статус платёжной сессии из Stripe по session_id."""
    session = stripe.checkout.Session.retrieve(session_id)
    return {"status": session.status, "payment_status": session.payment_status}
