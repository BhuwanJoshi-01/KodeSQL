# Stripe Payment Integration Setup Guide

## Overview

This guide explains how to set up real Stripe payment processing for the challenge subscription system. The implementation includes:

- ✅ Real Stripe checkout sessions
- ✅ Pending payment expiration (30 minutes)
- ✅ Automatic cleanup of expired payments
- ✅ Webhook handling for payment confirmations
- ✅ Cancel and retry payment functionality

## 1. Stripe Account Setup

### Create Stripe Account
1. Go to [https://stripe.com](https://stripe.com)
2. Create an account or log in
3. Complete account verification

### Get API Keys
1. Go to Stripe Dashboard → Developers → API keys
2. Copy your **Publishable key** (starts with `pk_test_` for test mode)
3. Copy your **Secret key** (starts with `sk_test_` for test mode)

### Create Webhook Endpoint
1. Go to Stripe Dashboard → Developers → Webhooks
2. Click "Add endpoint"
3. Set endpoint URL: `https://yourdomain.com/challenges/stripe/webhook/`
4. Select events to listen for:
   - `checkout.session.completed`
   - `payment_intent.succeeded`
5. Copy the **Webhook signing secret** (starts with `whsec_`)

## 2. Environment Configuration

### Set Environment Variables

Create a `.env` file or set these environment variables:

```bash
# Stripe Configuration
STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
STRIPE_SECRET_KEY=sk_test_your_secret_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
STRIPE_LIVE_MODE=False

# Site URL for redirects
SITE_URL=https://yourdomain.com
```

### Update Django Settings

The settings are already configured in `sqlplayground/settings.py`:

```python
# Stripe settings
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY', 'pk_test_...')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_...')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET', 'whsec_...')
STRIPE_LIVE_MODE = os.environ.get('STRIPE_LIVE_MODE', 'False').lower() == 'true'
SITE_URL = os.environ.get('SITE_URL', 'http://127.0.0.1:8000')
```

## 3. Testing the Integration

### Test Cards
Use Stripe's test card numbers:

- **Successful payment**: `4242424242424242`
- **Declined payment**: `4000000000000002`
- **Requires authentication**: `4000002500003155`

### Test Flow
1. Go to `/challenges/subscription/`
2. Select a subscription plan
3. Click "Choose [Plan Name]"
4. Click "Pay with Stripe"
5. Use test card details
6. Verify payment success

## 4. Key Features Implemented

### Pending Payment Management
- **Automatic Expiration**: Pending payments expire after 30 minutes
- **Cleanup Process**: Expired pending payments are automatically marked as expired
- **Cancel Functionality**: Users can cancel pending payments and choose different plans
- **Retry Logic**: Users can retry failed payments or switch plans seamlessly

### Payment Flow
1. User selects subscription plan
2. System creates pending subscription with 30-minute expiration
3. User is redirected to Stripe checkout
4. Payment is processed securely by Stripe
5. Webhook confirms payment and activates subscription
6. User is redirected back with success message

### Error Handling
- **Payment Failures**: Clear error messages and retry options
- **Expired Sessions**: Automatic cleanup and new session creation
- **Network Issues**: Graceful handling with user feedback
- **Webhook Failures**: Fallback verification on success page

## 5. Database Schema Changes

### New Fields Added
```python
# UserChallengeSubscription model
stripe_payment_intent_id = models.CharField(max_length=255, null=True, blank=True)
pending_expires_at = models.DateTimeField(null=True, blank=True)
```

### New Methods Added
```python
# Pending payment management
def set_pending_expiration(self, minutes=30)
def cancel_pending(self)
def is_pending_expired(self)
def cleanup_expired_pending(cls)  # Class method
```

## 6. URL Structure

### New URLs Added
```python
# Stripe payment URLs
path('subscription/stripe-checkout/<int:subscription_id>/', views.create_stripe_checkout, name='create_stripe_checkout'),
path('subscription/payment-success/<int:subscription_id>/', views.payment_success, name='payment_success'),
path('subscription/payment-cancel/<int:subscription_id>/', views.payment_cancel, name='payment_cancel'),
path('subscription/cancel/<int:subscription_id>/', views.cancel_pending_subscription, name='cancel_pending_subscription'),
path('stripe/webhook/', views.stripe_webhook, name='stripe_webhook'),
```

## 7. Production Deployment

### Security Considerations
- ✅ All payments processed by Stripe (PCI compliant)
- ✅ No credit card data stored locally
- ✅ Webhook signature verification
- ✅ CSRF protection on all forms
- ✅ Secure redirect URLs

### Monitoring
- Set up monitoring for webhook failures
- Monitor payment success/failure rates
- Track pending payment expiration rates
- Set up alerts for unusual payment patterns

### Live Mode Setup
1. Complete Stripe account verification
2. Switch to live API keys
3. Set `STRIPE_LIVE_MODE=True`
4. Update webhook endpoint to production URL
5. Test with real payment methods

## 8. Troubleshooting

### Common Issues

**Webhook not receiving events:**
- Check webhook URL is accessible
- Verify webhook secret is correct
- Check Stripe dashboard for delivery attempts

**Payment not activating subscription:**
- Check webhook is properly configured
- Verify payment_intent metadata includes subscription_id
- Check Django logs for webhook processing errors

**Pending payments not expiring:**
- Run cleanup command: `python manage.py shell -c "from challenges.models import UserChallengeSubscription; UserChallengeSubscription.cleanup_expired_pending()"`
- Set up cron job for automatic cleanup

### Support Commands
```bash
# Clean up expired pending payments
python manage.py shell -c "from challenges.models import UserChallengeSubscription; print(f'Cleaned up {UserChallengeSubscription.cleanup_expired_pending()} expired pending payments')"

# Check subscription status
python manage.py shell -c "from challenges.models import UserChallengeSubscription; [print(f'{s.user.email}: {s.status} - {s.plan.name}') for s in UserChallengeSubscription.objects.all()]"
```

## 9. Success Metrics

The implementation successfully addresses both original issues:

### ✅ Pending Payment Issue - RESOLVED
- Users can cancel pending payments
- Automatic 30-minute expiration prevents stuck states
- Seamless plan switching and retry functionality
- Clear user feedback and error handling

### ✅ Real Stripe Integration - IMPLEMENTED
- Complete removal of mock payment system
- Real Stripe checkout sessions with secure processing
- Webhook handling for payment confirmations
- Production-ready payment flow with proper error handling

The system is now production-ready with a fully functional payment system that provides a seamless user experience while maintaining security and reliability.
