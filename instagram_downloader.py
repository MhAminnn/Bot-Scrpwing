import logging
import requests
import urllib.parse
from typing import Dict, Any, Optional
from io import BytesIO

logger = logging.getLogger(__name__)

class InstagramDownloader:
    """Class for handling Instagram content downloading."""
    
    def __init__(self, api_url: str, timeout: int = 15):
        """
        Initialize the Instagram downloader.
        
        Args:
            api_url: URL for the Instagram downloading API
            timeout: Request timeout in seconds
        """
        self.api_url = api_url
        self.timeout = timeout
    
    def clean_instagram_url(self, url: str) -> str:
        """
        Clean Instagram URL by removing tracking parameters.
        
        Args:
            url: Raw Instagram URL
            
        Returns:
            Cleaned URL
        """
        return url.split('?')[0].strip().rstrip('/')
    
    def is_valid_instagram_url(self, url: str) -> bool:
        """
        Check if URL is a valid Instagram URL.
        
        Args:
            url: URL to validate
            
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
    
    def download_content(self, url: str) -> Dict[str, Any]:
        """
        Download Instagram content from URL.
        
        Args:
            url: Instagram post/reel/story URL
            
        Returns:
            Dictionary containing download response
            
        Raises:
            requests.Timeout: If request times out
            requests.RequestException: For other request errors
        """
        try:
            # Clean and validate URL
            cleaned_url = self.clean_instagram_url(url)
            if not self.is_valid_instagram_url(cleaned_url):
                return {"status": "error", "message": "Invalid Instagram URL"}
            
            # Encode URL for API request
            encoded_url = urllib.parse.quote(cleaned_url)
            request_url = f"{self.api_url}?url={encoded_url}"
            
            logger.info(f"Requesting content from: {request_url}")
            
            # Make API request
            response = requests.get(request_url, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"API Response status: {data.get('status')}")
            
            return data
            
        except requests.Timeout:
            logger.error("Request timeout")
            return {"status": "error", "message": "Request timed out"}
        except requests.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            return {"status": "error", "message": f"Request error: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return {"status": "error", "message": f"Unexpected error: {str(e)}"}
    
    def download_media_file(self, url: str) -> Optional[BytesIO]:
        """
        Download media file from URL.
        
        Args:
            url: Media URL
            
        Returns:
            BytesIO object containing media file data, or None if download failed
        """
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # Create BytesIO object from response content
            file_obj = BytesIO(response.content)
            file_obj.name = urllib.parse.urlsplit(url).path.split('/')[-1]
            
            return file_obj
        except Exception as e:
            logger.error(f"Error downloading media file: {str(e)}")
            return None