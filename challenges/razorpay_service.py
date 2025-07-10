"""
Razorpay payment service for handling subscription payments.
"""
import logging
import razorpay
from decimal import Decimal
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
import hmac
import hashlib

logger = logging.getLogger(__name__)


class RazorpayService:
    """Service class for handling Razorpay payments"""
    
    @staticmethod
    def get_client():
        """Get Razorpay client instance"""
        return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    
    @staticmethod
    def create_order(subscription, request):
        """
        Create a Razorpay Order for a subscription
        """
        try:
            client = RazorpayService.get_client()
            
            # Convert amount to paise (Razorpay uses paise for INR)
            amount_paise = int(subscription.amount_paid * 100)
            
            # Create order
            order_data = {
                'amount': amount_paise,
                'currency': settings.RAZORPAY_CURRENCY,
                'receipt': f'subscription_{subscription.id}_{timezone.now().strftime("%Y%m%d_%H%M%S")}',
                'notes': {
                    'subscription_id': str(subscription.id),
                    'user_id': str(subscription.user.id),
                    'plan_id': str(subscription.plan.id),
                    'plan_name': subscription.plan.name,
                    'user_email': subscription.user.email,
                }
            }
            
            order = client.order.create(data=order_data)
            
            # Store the order ID
            subscription.razorpay_order_id = order['id']
            subscription.save()
            
            return order
            
        except Exception as e:
            logger.error(f"Razorpay error creating order: {e}")
            raise
    
    @staticmethod
    def verify_payment_signature(razorpay_order_id, razorpay_payment_id, razorpay_signature):
        """
        Verify Razorpay payment signature for security
        """
        try:
            client = RazorpayService.get_client()
            
            # Verify signature
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            
            client.utility.verify_payment_signature(params_dict)
            return True
            
        except Exception as e:
            logger.error(f"Razorpay signature verification failed: {e}")
            return False
    
    @staticmethod
    def get_payment_details(payment_id):
        """
        Get payment details from Razorpay
        """
        try:
            client = RazorpayService.get_client()
            return client.payment.fetch(payment_id)
        except Exception as e:
            logger.error(f"Error fetching payment details: {e}")
            return None
    
    @staticmethod
    def handle_payment_success(payment_data):
        """
        Handle successful payment from webhook or callback
        """
        try:
            # Extract order ID from payment data
            order_id = payment_data.get('order_id')
            payment_id = payment_data.get('id')
            
            if not order_id:
                logger.error("No order_id in payment data")
                return False
            
            # Import here to avoid circular imports
            from .models import UserChallengeSubscription
            
            # Get the subscription by order ID
            try:
                subscription = UserChallengeSubscription.objects.get(razorpay_order_id=order_id)
            except UserChallengeSubscription.DoesNotExist:
                logger.error(f"Subscription with order_id {order_id} not found")
                return False
            
            # Activate the subscription
            subscription.activate()
            subscription.payment_reference = payment_id
            subscription.save()
            
            logger.info(f"Successfully activated subscription {subscription.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error handling payment success: {e}")
            return False
    
    @staticmethod
    def verify_webhook_signature(payload, signature):
        """
        Verify webhook signature from Razorpay
        """
        try:
            if not settings.RAZORPAY_WEBHOOK_SECRET:
                logger.warning("Razorpay webhook secret not configured")
                return True  # Skip verification if secret not set
            
            expected_signature = hmac.new(
                settings.RAZORPAY_WEBHOOK_SECRET.encode('utf-8'),
                payload,
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(expected_signature, signature)
            
        except Exception as e:
            logger.error(f"Error verifying webhook signature: {e}")
            return False
    
    @staticmethod
    def format_amount(amount):
        """
        Format amount for display (convert from paise to rupees)
        """
        return Decimal(amount) / 100
    
    @staticmethod
    def get_key_id():
        """
        Get the Razorpay key ID for frontend
        """
        return settings.RAZORPAY_KEY_ID
    
    @staticmethod
    def create_payment_link(subscription, request):
        """
        Create a Razorpay payment link for subscription
        """
        try:
            client = RazorpayService.get_client()
            
            # Convert amount to paise
            amount_paise = int(subscription.amount_paid * 100)
            
            # Build callback URLs
            callback_url = request.build_absolute_uri(
                reverse('challenges:payment_success', kwargs={'subscription_id': subscription.id})
            )
            
            # Create payment link
            payment_link_data = {
                'amount': amount_paise,
                'currency': settings.RAZORPAY_CURRENCY,
                'accept_partial': False,
                'description': f'Challenge Subscription: {subscription.plan.name}',
                'customer': {
                    'name': f"{subscription.user.first_name} {subscription.user.last_name}".strip() or subscription.user.email,
                    'email': subscription.user.email,
                },
                'notify': {
                    'sms': False,
                    'email': True
                },
                'reminder_enable': True,
                'notes': {
                    'subscription_id': str(subscription.id),
                    'user_id': str(subscription.user.id),
                    'plan_id': str(subscription.plan.id),
                },
                'callback_url': callback_url,
                'callback_method': 'get'
            }
            
            # Set expiry if configured
            if subscription.pending_expires_at:
                payment_link_data['expire_by'] = int(subscription.pending_expires_at.timestamp())
            
            payment_link = client.payment_link.create(data=payment_link_data)
            
            return payment_link
            
        except Exception as e:
            logger.error(f"Error creating payment link: {e}")
            raise
