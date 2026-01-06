import stripe
from django.conf import settings
from django.core.exceptions import ValidationError

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    """Service for working with Stripe API."""

    @staticmethod
    def create_product(name, description=None):
        """Create product in Stripe."""
        try:
            product = stripe.Product.create(
                name=name,
                description=description
            )
            return product.id
        except stripe.error.StripeError as e:
            raise ValidationError(f'Stripe error: {str(e)}')

    @staticmethod
    def create_price(product_id, amount, currency='rub'):
        """Create price for product in Stripe."""
        try:
            # Convert amount to cents/kopecks
            amount_in_cents = int(float(amount) * 100)

            price = stripe.Price.create(
                product=product_id,
                unit_amount=amount_in_cents,
                currency=currency,
            )
            return price.id
        except stripe.error.StripeError as e:
            raise ValidationError(f'Stripe error: {str(e)}')

    @staticmethod
    def create_checkout_session(price_id, success_url, cancel_url, metadata=None):
        """Create checkout session in Stripe."""
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata=metadata or {},
            )
            return {
                'session_id': session.id,
                'payment_url': session.url,
                'payment_intent_id': session.payment_intent,
            }
        except stripe.error.StripeError as e:
            raise ValidationError(f'Stripe error: {str(e)}')

    @staticmethod
    def get_session(session_id):
        """Retrieve session from Stripe."""
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            return session
        except stripe.error.StripeError as e:
            raise ValidationError(f'Stripe error: {str(e)}')

    @staticmethod
    def verify_webhook_signature(payload, sig_header):
        """Verify Stripe webhook signature."""
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
            return event
        except ValueError as e:
            raise ValidationError(f'Invalid payload: {str(e)}')
        except stripe.error.SignatureVerificationError as e:
            raise ValidationError(f'Invalid signature: {str(e)}')