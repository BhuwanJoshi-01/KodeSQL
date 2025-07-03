from django import template
import re

register = template.Library()

@register.filter
def youtube_embed(url):
    """Convert YouTube URL to embed URL"""
    if not url:
        return url
    
    # Handle youtube.com/watch?v= format
    if 'youtube.com/watch?v=' in url:
        video_id = url.split('v=')[1].split('&')[0]
        return f"https://www.youtube.com/embed/{video_id}"
    
    # Handle youtu.be/ format
    if 'youtu.be/' in url:
        video_id = url.split('youtu.be/')[1].split('?')[0]
        return f"https://www.youtube.com/embed/{video_id}"
    
    # Handle already embedded URLs
    if 'youtube.com/embed/' in url:
        return url
    
    return url

@register.filter
def vimeo_embed(url):
    """Convert Vimeo URL to embed URL"""
    if not url:
        return url
    
    # Handle vimeo.com/ format
    if 'vimeo.com/' in url:
        video_id = url.split('vimeo.com/')[1].split('?')[0].split('/')[0]
        return f"https://player.vimeo.com/video/{video_id}"
    
    # Handle already embedded URLs
    if 'player.vimeo.com/video/' in url:
        return url
    
    return url

@register.filter
def format_duration(minutes):
    """Format duration in minutes to human readable format"""
    if not minutes or minutes == 0:
        return "No duration set"
    
    hours = minutes // 60
    mins = minutes % 60
    
    if hours > 0:
        return f"{hours}h {mins}m"
    return f"{mins}m"

@register.filter
def format_file_size(bytes_size):
    """Format file size in bytes to human readable format"""
    if not bytes_size or bytes_size == 0:
        return "Unknown size"
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"
