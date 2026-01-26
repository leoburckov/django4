import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    """Service for working with Stripe API."""

    @staticmethod
    def create_product(name: str, description: str = None) -> str:
        """
        Create product in Stripe.

        Args:
            name: Product name
            description: Product description

        Returns:
            Stripe product ID
        """
        try:
            product = stripe.Product.create(
                name=name,
                description=description,
            )
            return product.id
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe product creation error: {str(e)}")

    @staticmethod
    def create_price(product_id: str, amount: float, currency: str = "usd") -> str:
        """
        Create price for product in Stripe.

        Args:
            product_id: Stripe product ID
            amount: Price amount
            currency: Currency code

        Returns:
            Stripe price ID
        """
        try:
            # Convert amount to cents
            amount_in_cents = int(amount * 100)

            price = stripe.Price.create(
                product=product_id,
                unit_amount=amount_in_cents,
                currency=currency,
            )
            return price.id
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe price creation error: {str(e)}")

    @staticmethod
    def create_checkout_session(
        price_id: str,
        success_url: str,
        cancel_url: str,
        metadata: dict = None,
    ) -> dict:
        """
        Create checkout session in Stripe.

        Args:
            price_id: Stripe price ID
            success_url: Success redirect URL
            cancel_url: Cancel redirect URL
            metadata: Session metadata

        Returns:
            Dictionary with session data
        """
        try:
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
                metadata=metadata or {},
            )

            return {
                "session_id": session.id,
                "payment_url": session.url,
                "payment_intent_id": session.payment_intent,
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe session creation error: {str(e)}")

    @staticmethod
    def retrieve_session(session_id: str) -> dict:
        """
        Retrieve session from Stripe.

        Args:
            session_id: Stripe session ID

        Returns:
            Session data
        """
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            return session
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe session retrieval error: {str(e)}")
