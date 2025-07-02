
from django.shortcuts import render
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt
import json

def csrf_debug(request):
    """Debug view to check CSRF token"""
    context = {
        'csrf_token': get_token(request),
        'method': request.method,
        'has_session': hasattr(request, 'session'),
        'session_key': getattr(request.session, 'session_key', None) if hasattr(request, 'session') else None,
    }
    
    if request.method == 'POST':
        context.update({
            'post_data': dict(request.POST),
            'csrf_token_from_post': request.POST.get('csrfmiddlewaretoken', 'Not found'),
        })
    
    return JsonResponse(context, indent=2)

@csrf_exempt
def csrf_test_form(request):
    """Test form for CSRF debugging"""
    if request.method == 'POST':
        return JsonResponse({
            'status': 'success',
            'message': 'Form submitted successfully',
            'csrf_token_received': request.POST.get('csrfmiddlewaretoken', 'Not found')
        })
    
    return render(request, 'csrf_test.html')
