"""
Stripe payment service for challenge subscriptions
"""
import stripe
from django.conf import settings
from django.urls import reverse
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    """Service class for handling Stripe payments"""
    
    @staticmethod
    def create_payment_intent(subscription, request):
        """
        Create a Stripe Payment Intent for a subscription
        """
        try:
            # Convert amount to cents (Stripe uses cents)
            amount_cents = int(subscription.amount_paid * 100)
            
            # Create payment intent
            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency='usd',
                metadata={
                    'subscription_id': subscription.id,
                    'user_id': subscription.user.id,
                    'plan_id': subscription.plan.id,
                    'plan_name': subscription.plan.name,
                },
                description=f'Challenge Subscription: {subscription.plan.name}',
                receipt_email=subscription.user.email,
            )
            
            # Store the payment intent ID
            subscription.stripe_payment_intent_id = intent.id
            subscription.save()
            
            return intent
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating payment intent: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating payment intent: {e}")
            raise
    
    @staticmethod
    def create_checkout_session(subscription, request):
        """
        Create a Stripe Checkout Session for a subscription
        """
        try:
            # Convert amount to cents (Stripe uses cents)
            amount_cents = int(subscription.amount_paid * 100)
            
            # Build URLs
            success_url = request.build_absolute_uri(
                reverse('challenges:payment_success', kwargs={'subscription_id': subscription.id})
            )
            cancel_url = request.build_absolute_uri(
                reverse('challenges:payment_cancel', kwargs={'subscription_id': subscription.id})
            )
            
            # Create checkout session
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': f'Challenge Subscription - {subscription.plan.name}',
                            'description': subscription.plan.description,
                        },
                        'unit_amount': amount_cents,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                customer_email=subscription.user.email,
                metadata={
                    'subscription_id': subscription.id,
                    'user_id': subscription.user.id,
                    'plan_id': subscription.plan.id,
                },
                expires_at=int(subscription.pending_expires_at.timestamp()) if subscription.pending_expires_at else None,
            )
            
            # Store the session ID
            subscription.stripe_payment_intent_id = session.id
            subscription.save()
            
            return session
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating checkout session: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating checkout session: {e}")
            raise
    
    @staticmethod
    def retrieve_payment_intent(payment_intent_id):
        """
        Retrieve a Stripe Payment Intent
        """
        try:
            return stripe.PaymentIntent.retrieve(payment_intent_id)
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error retrieving payment intent: {e}")
            raise
    
    @staticmethod
    def retrieve_checkout_session(session_id):
        """
        Retrieve a Stripe Checkout Session
        """
        try:
            return stripe.checkout.Session.retrieve(session_id)
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error retrieving checkout session: {e}")
            raise
    
    @staticmethod
    def construct_webhook_event(payload, sig_header):
        """
        Construct and verify a Stripe webhook event
        """
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
            return event
        except ValueError as e:
            logger.error(f"Invalid payload in webhook: {e}")
            raise
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid signature in webhook: {e}")
            raise
    
    @staticmethod
    def handle_payment_success(event_data):
        """
        Handle successful payment from webhook
        """
        try:
            # Extract subscription ID from metadata
            metadata = event_data.get('metadata', {})
            subscription_id = metadata.get('subscription_id')
            
            if not subscription_id:
                logger.error("No subscription_id in payment metadata")
                return False
            
            # Import here to avoid circular imports
            from .models import UserChallengeSubscription
            
            # Get the subscription
            try:
                subscription = UserChallengeSubscription.objects.get(id=subscription_id)
            except UserChallengeSubscription.DoesNotExist:
                logger.error(f"Subscription {subscription_id} not found")
                return False
            
            # Activate the subscription
            subscription.activate()
            subscription.payment_reference = event_data.get('id', 'stripe_payment')
            subscription.save()
            
            logger.info(f"Successfully activated subscription {subscription_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error handling payment success: {e}")
            return False
    
    @staticmethod
    def format_amount(amount):
        """
        Format amount for display (convert from cents to dollars)
        """
        return Decimal(amount) / 100
    
    @staticmethod
    def get_publishable_key():
        """
        Get the Stripe publishable key
        """
        return settings.STRIPE_PUBLISHABLE_KEY
