"""
Jinja2 environment configuration for Django.
"""

from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse
from django.middleware.csrf import get_token
from django.contrib.messages import get_messages
from jinja2 import Environment


def csrf_token(request):
    """Get CSRF token for the request."""
    return get_token(request)


def pluralize(value, singular='', plural='s'):
    """
    Jinja2 pluralize filter similar to Django's pluralize.
    """
    if value == 1:
        return singular
    return plural


def url_reverse(viewname, *args, **kwargs):
    """
    Custom URL reverse function for Jinja2 that handles arguments properly.
    """
    try:
        return reverse(viewname, args=args, kwargs=kwargs)
    except Exception as e:
        print(f"URL reverse error: {e}, viewname: {viewname}, args: {args}, kwargs: {kwargs}")
        return "#"


def truncatewords(value, length=20):
    """
    Jinja2 truncatewords filter similar to Django's truncatewords.
    """
    if not value:
        return ""

    words = str(value).split()
    if len(words) <= length:
        return value

    return " ".join(words[:length]) + "..."


def forloop_counter(loop):
    """
    Jinja2 equivalent of Django's forloop.counter.
    """
    return loop.index


def linebreaks(value):
    """
    Jinja2 linebreaks filter similar to Django's linebreaks.
    """
    if not value:
        return ""

    import re
    from markupsafe import Markup

    # Normalize line endings
    value = str(value).replace('\r\n', '\n').replace('\r', '\n')

    # Split into paragraphs (double newlines)
    paragraphs = re.split(r'\n\s*\n', value)

    # Process each paragraph
    processed_paragraphs = []
    for para in paragraphs:
        if para.strip():
            # Replace single newlines with <br> tags
            para = re.sub(r'\n', '<br>', para.strip())
            processed_paragraphs.append(f'<p>{para}</p>')

    return Markup('\n'.join(processed_paragraphs))


def escapejs(value):
    """
    Jinja2 escapejs filter similar to Django's escapejs.
    """
    if not value:
        return ""

    import json
    return json.dumps(str(value))[1:-1]  # Remove the surrounding quotes


def urlencode_filter(value):
    """
    Jinja2 urlencode filter similar to Django's urlencode.
    """
    if not value:
        return ""

    from urllib.parse import quote
    return quote(str(value))


def date_filter(value, format_string="M d, Y"):
    """
    Jinja2 date filter similar to Django's date filter.
    """
    if not value:
        return ""

    from django.utils.dateformat import format as django_format
    return django_format(value, format_string)


def environment(**options):
    """
    Create and configure Jinja2 environment.
    """
    env = Environment(**options)
    env.globals.update({
        'static': staticfiles_storage.url,
        'url': url_reverse,
        'csrf_token': csrf_token,
        'get_messages': get_messages,
    })

    # Add custom filters
    env.filters['pluralize'] = pluralize
    env.filters['truncatewords'] = truncatewords
    env.filters['linebreaks'] = linebreaks
    env.filters['escapejs'] = escapejs
    env.filters['urlencode'] = urlencode_filter
    env.filters['date'] = date_filter
    return env
