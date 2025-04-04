import re
from typing import Dict, Any, Tuple
import urllib.parse

def clean_url(url: str) -> str:
    """
    Clean URL by removing tracking parameters and extracting the base URL.
    
    Args:
        url: Raw URL
        
    Returns:
        Cleaned URL
    """
    # Remove query parameters
    base_url = url.split('?')[0].strip().rstrip('/')
    return base_url

def clean_instagram_url(url: str) -> str:
    """
    Clean Instagram URL by removing tracking parameters and extracting the base URL.
    
    Args:
        url: Raw Instagram URL
        
    Returns:
        Cleaned Instagram URL
    """
    return clean_url(url)

def clean_facebook_url(url: str) -> str:
    """
    Clean Facebook URL by removing tracking parameters.
    
    Args:
        url: Raw Facebook URL
        
    Returns:
        Cleaned Facebook URL
    """
    # Clean basic URL first
    basic_cleaned = clean_url(url)
    
    # Handle special Facebook URL formats
    if '/photo/?fbid=' in basic_cleaned:
        # Format: facebook.com/photo/?fbid=123456&set=123456
        try:
            # Extract fbid parameter
            parsed = urllib.parse.urlparse(url)
            query_params = urllib.parse.parse_qs(parsed.query)
            fbid = query_params.get('fbid', [''])[0]
            if fbid:
                return f"https://www.facebook.com/photo.php?fbid={fbid}"
        except:
            # If extraction fails, return basic cleaned URL
            pass
    
    # Handle photo.php URLs
    if 'photo.php' in basic_cleaned:
        try:
            # Keep only fbid parameter if exists
            parsed = urllib.parse.urlparse(url)
            query_params = urllib.parse.parse_qs(parsed.query)
            fbid = query_params.get('fbid', [''])[0]
            if fbid:
                return f"https://www.facebook.com/photo.php?fbid={fbid}"
        except:
            # If extraction fails, return basic cleaned URL
            pass
    
    return basic_cleaned
    
def clean_tiktok_url(url: str) -> str:
    """
    Clean TikTok URL by removing tracking parameters.
    
    Args:
        url: Raw TikTok URL
        
    Returns:
        Cleaned TikTok URL
    """
    return clean_url(url)

def clean_youtube_url(url: str) -> str:
    """
    Clean YouTube URL by removing tracking parameters and retaining only the video ID.
    
    Args:
        url: Raw YouTube URL
        
    Returns:
        Cleaned YouTube URL
    """
    # Remove URL fragments
    url = url.split('#')[0]
    
    # Parse URL
    parsed_url = urllib.parse.urlparse(url)
    
    # Extract video ID
    query_params = urllib.parse.parse_qs(parsed_url.query)
    video_id = query_params.get('v', [''])[0]
    
    if video_id:
        # Reconstruct URL with only video ID parameter
        cleaned_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}?v={video_id}"
        return cleaned_url
    
    # For youtu.be format
    if 'youtu.be' in url:
        path = parsed_url.path.strip('/')
        if path:
            return f"https://youtube.com/watch?v={path}"
    
    return url

def detect_url_type(url: str) -> str:
    """
    Detect the type of URL (Instagram, Facebook, TikTok, YouTube, or Unknown).
    
    Args:
        url: URL to check
        
    Returns:
        String indicating URL type: 'instagram', 'facebook', 'tiktok', 'youtube', or 'unknown'
    """
    url = url.lower()
    
    if is_valid_instagram_url(url):
        return 'instagram'
    elif is_valid_facebook_url(url):
        return 'facebook'
    elif is_valid_tiktok_url(url):
        return 'tiktok'
    elif is_valid_youtube_url(url):
        return 'youtube'
    else:
        return 'unknown'

def is_valid_instagram_url(url: str) -> bool:
    """
    Check if URL is a valid Instagram URL.
    
    Args:
        url: URL to check
        
    Returns:
        True if valid Instagram URL, False otherwise
    """
    patterns = [
        'instagram.com/p/',
        'instagram.com/reel/',
        'instagram.com/stories/',
        'instagram.com/tv/'
    ]
    return any(pattern in url for pattern in patterns)

def is_valid_facebook_url(url: str) -> bool:
    """
    Check if URL is a valid Facebook URL.
    
    Args:
        url: URL to check
        
    Returns:
        True if valid Facebook URL, False otherwise
    """
    patterns = [
        'facebook.com/watch',
        'facebook.com/story',
        'facebook.com/share',
        'facebook.com/reel',
        'facebook.com/photo',
        'facebook.com/photo.php',
        'facebook.com/p/',
        'fb.watch/',
        'fb.com/'
    ]
    return any(pattern in url for pattern in patterns)

def is_valid_tiktok_url(url: str) -> bool:
    """
    Check if URL is a valid TikTok URL.
    
    Args:
        url: URL to check
        
    Returns:
        True if valid TikTok URL, False otherwise
    """
    patterns = [
        'tiktok.com/',
        'vm.tiktok.com/',
        'vt.tiktok.com/'
    ]
    return any(pattern in url for pattern in patterns)

def is_valid_youtube_url(url: str) -> bool:
    """
    Check if URL is a valid YouTube URL.
    
    Args:
        url: URL to check
        
    Returns:
        True if valid YouTube URL, False otherwise
    """
    patterns = [
        'youtube.com/watch',
        'youtu.be/',
        'youtube.com/embed/',
        'youtube.com/v/',
        'music.youtube.com/watch'
    ]
    return any(pattern in url for pattern in patterns)

def get_content_type(url: str) -> str:
    """
    Determine the type of Instagram content from the URL.
    
    Args:
        url: Instagram URL
        
    Returns:
        Type of content ('post', 'reel', 'story', 'igtv', or 'unknown')
    """
    if 'instagram.com/p/' in url:
        return 'post'
    elif 'instagram.com/reel/' in url:
        return 'reel'
    elif 'instagram.com/stories/' in url:
        return 'story'
    elif 'instagram.com/tv/' in url:
        return 'igtv'
    else:
        return 'unknown'

def create_media_caption(url: str) -> str:
    """
    Create a caption for media based on content type and source.
    
    Args:
        url: Social media URL
        
    Returns:
        Caption text
    """
    url_type = detect_url_type(url)
    
    if url_type == 'instagram':
        content_type = get_content_type(url)
        if content_type == 'post':
            return "📷 Instagram Post"
        elif content_type == 'reel':
            return "🎬 Instagram Reel"
        elif content_type == 'story':
            return "⏱️ Instagram Story"
        elif content_type == 'igtv':
            return "📺 Instagram TV"
        else:
            return "📥 Instagram Media"
    elif url_type == 'facebook':
        if 'watch' in url:
            return "📺 Facebook Video"
        elif 'story' in url:
            return "⏱️ Facebook Story"
        elif 'reel' in url:
            return "🎬 Facebook Reel" 
        elif 'photo' in url.lower() or '/p/' in url.lower() or 'photo.php' in url.lower():
            return "📷 Facebook Photo"
        else:
            return "📥 Facebook Content"
    elif url_type == 'tiktok':
        return "🎵 TikTok Video"
    elif url_type == 'youtube':
        if 'music.youtube.com' in url.lower():
            return "🎵 YouTube Music"
        else:
            return "🎵 YouTube Audio"
    else:
        return "📥 Media Content"