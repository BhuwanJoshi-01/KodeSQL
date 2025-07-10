from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from challenges.models import UserChallengeSubscription


class Command(BaseCommand):
    help = 'Send subscription expiration notifications'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be sent without actually sending emails',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write('DRY RUN MODE - No emails will be sent')
        
        self.stdout.write('Checking for subscription notifications...')
        
        # Send expiration warnings (7 days before expiry)
        self.send_expiration_warnings(dry_run)
        
        # Send final notifications (1 day before expiry)
        self.send_final_notifications(dry_run)
        
        # Send expired notifications
        self.send_expired_notifications(dry_run)
        
        self.stdout.write(
            self.style.SUCCESS('Subscription notification check completed!')
        )

    def send_expiration_warnings(self, dry_run=False):
        """Send warning emails 7 days before expiration"""
        seven_days_from_now = timezone.now() + timedelta(days=7)
        
        subscriptions = UserChallengeSubscription.objects.filter(
            status='active',
            end_date__date=seven_days_from_now.date(),
            expiry_notification_sent=False
        )
        
        count = 0
        for subscription in subscriptions:
            if subscription.is_active and subscription.is_expiring_soon:
                if not dry_run:
                    self.send_expiration_email(subscription, 'warning')
                    subscription.expiry_notification_sent = True
                    subscription.save()
                
                self.stdout.write(f'Expiration warning: {subscription.user.email}')
                count += 1
        
        self.stdout.write(f'Sent {count} expiration warning emails')

    def send_final_notifications(self, dry_run=False):
        """Send final notification 1 day before expiration"""
        tomorrow = timezone.now() + timedelta(days=1)
        
        subscriptions = UserChallengeSubscription.objects.filter(
            status='active',
            end_date__date=tomorrow.date(),
            final_notification_sent=False
        )
        
        count = 0
        for subscription in subscriptions:
            if subscription.is_active:
                if not dry_run:
                    self.send_expiration_email(subscription, 'final')
                    subscription.final_notification_sent = True
                    subscription.save()
                
                self.stdout.write(f'Final notification: {subscription.user.email}')
                count += 1
        
        self.stdout.write(f'Sent {count} final notification emails')

    def send_expired_notifications(self, dry_run=False):
        """Send notifications for recently expired subscriptions"""
        yesterday = timezone.now() - timedelta(days=1)
        
        subscriptions = UserChallengeSubscription.objects.filter(
            status='active',
            end_date__lt=timezone.now(),
            end_date__gte=yesterday
        )
        
        count = 0
        for subscription in subscriptions:
            if not subscription.is_active:
                if not dry_run:
                    subscription.expire()
                    self.send_expiration_email(subscription, 'expired')
                
                self.stdout.write(f'Expired notification: {subscription.user.email}')
                count += 1
        
        self.stdout.write(f'Sent {count} expired notification emails')

    def send_expiration_email(self, subscription, notification_type):
        """Send expiration email notification"""
        user = subscription.user
        plan = subscription.plan
        
        # Email templates based on notification type
        templates = {
            'warning': {
                'subject': 'Your Challenge Subscription Expires Soon',
                'template': 'challenges/emails/expiration_warning.html'
            },
            'final': {
                'subject': 'Final Notice: Your Challenge Subscription Expires Tomorrow',
                'template': 'challenges/emails/final_notification.html'
            },
            'expired': {
                'subject': 'Your Challenge Subscription Has Expired',
                'template': 'challenges/emails/expired_notification.html'
            }
        }
        
        template_info = templates.get(notification_type)
        if not template_info:
            return
        
        context = {
            'user': user,
            'subscription': subscription,
            'plan': plan,
            'days_remaining': subscription.days_remaining,
            'site_name': 'KodeSQL',
            'renewal_url': f"{settings.SITE_URL}/challenges/subscription/",
        }
        
        try:
            # Render email content
            html_content = render_to_string(template_info['template'], context)
            
            # Send email
            send_mail(
                subject=template_info['subject'],
                message='',  # Plain text version (optional)
                html_message=html_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            
            self.stdout.write(f'Email sent to {user.email}')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to send email to {user.email}: {str(e)}')
            )
