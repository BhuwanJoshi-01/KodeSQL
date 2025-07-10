from django import template
from django.utils import timezone
import pytz

register = template.Library()

@register.filter
def to_indian_time(value):
    """Convert datetime to Indian timezone (IST)"""
    if not value:
        return value
    
    # Define Indian timezone
    indian_tz = pytz.timezone('Asia/Kolkata')
    
    # If the value is naive, assume it's in UTC
    if timezone.is_naive(value):
        value = timezone.make_aware(value, timezone.utc)
    
    # Convert to Indian timezone
    indian_time = value.astimezone(indian_tz)
    
    return indian_time

@register.filter
def format_indian_datetime(value, format_string="M d, Y g:i A"):
    """Format datetime in Indian timezone with custom format"""
    if not value:
        return value
    
    # Convert to Indian time first
    indian_time = to_indian_time(value)
    
    # Format the datetime
    from django.template.defaultfilters import date
    return date(indian_time, format_string) + " IST"
