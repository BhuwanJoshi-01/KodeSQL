"""
URL configuration for sqlplayground project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from django.views.static import serve

urlpatterns = [
    path("admin/", admin.site.urls),
    path("ckeditor5/", include('django_ckeditor_5.urls')),

    path("", include("core.urls")),
    path("auth/", include("users.urls")),
    path("accounts/", include("allauth.urls")),  # Django Allauth URLs
    path("editor/", include("editor.urls")),
    path("challenges/", include("challenges.urls")),
    path("tutorials/", include("tutorials.urls")),
    path("courses/", include("courses.urls")),
]

# Custom error handlers
def custom_404_view(request, exception):
    """Custom 404 error handler"""
    return render(request, '404.html', status=404)

def custom_500_view(request):
    """Custom 500 error handler"""
    return render(request, '500.html', status=500)

# Error handler assignments
handler404 = custom_404_view
handler500 = custom_500_view

# Test URL for 404 page (for development/testing)
urlpatterns += [
    path('test-404/', lambda request: render(request, '404.html'), name='test_404'),
]

# Serve media files (both development and production)
# Using Django's serve view which works regardless of DEBUG setting
if settings.MEDIA_URL and settings.MEDIA_ROOT:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]
