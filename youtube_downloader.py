import os
import logging
import requests
import urllib.parse
from typing import Dict, Any, Optional
from io import BytesIO

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class YoutubeDownloader:
    """Class for handling YouTube music content downloading."""
    
    def __init__(self, api_url: str, timeout: int = 15):
        """
        Initialize the YouTube downloader.
        
        Args:
            api_url: URL for the YouTube downloading API
            timeout: Request timeout in seconds
        """
        self.api_url = api_url
        self.timeout = timeout
    
    def clean_youtube_url(self, url: str) -> str:
        """
        Clean YouTube URL by removing tracking parameters.
        
        Args:
            url: Raw YouTube URL
            
        Returns:
            Cleaned URL
        """
        # Remove URL fragments
        url = url.split('#')[0]
        
        # Parse URL to extract essential parameters
        parsed_url = urllib.parse.urlparse(url)
        
        # Extract video ID
        query_params = urllib.parse.parse_qs(parsed_url.query)
        video_id = query_params.get('v', [''])[0]
        
        if video_id:
            # Reconstruct URL with only video ID parameter
            cleaned_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}?v={video_id}"
            return cleaned_url
        
        return url
    
    def is_valid_youtube_url(self, url: str) -> bool:
        """
        Check if URL is a valid YouTube URL.
        
        Args:
            url: URL to validate
            
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
    
    def download_content(self, url: str) -> Dict[str, Any]:
        """
        Download YouTube music content from URL.
        
        Args:
            url: YouTube music URL
            
        Returns:
            Dictionary containing download response
            
        Raises:
            requests.Timeout: If request times out
            requests.RequestException: For other request errors
        """
        try:
            # Clean URL
            cleaned_url = self.clean_youtube_url(url)
            
            # Encode URL for API request
            encoded_url = urllib.parse.quote(cleaned_url)
            request_url = f"{self.api_url}?url={encoded_url}"
            
            logger.info(f"Requesting content from: {request_url}")
            
            # Make request with application/json accept header
            headers = {'accept': 'application/json'}
            response = requests.get(
                request_url, 
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # Parse JSON response
            data = response.json()
            
            # Format the response to match our expected format
            title = data.get('title', 'Unknown Title')
            author = data.get('author', 'Unknown Artist')
            thumbnail = data.get('thumbnail', '')
            audio_url = data.get('url', '')
            quality = data.get('quality', 'Unknown Quality')
            
            media_list = []
            if audio_url:
                media_list.append({
                    "type": "audio",
                    "title": title,
                    "author": author,
                    "url": audio_url,
                    "downloadUrl": audio_url,
                    "thumbnail": thumbnail,
                    "quality": quality,
                    "metadata": {
                        "title": title,
                        "performer": author,
                        "duration": int(data.get('lengthSeconds', 0)),  # Pastikan duration berupa integer
                        "views": int(data.get('views', 0)),            # Pastikan views berupa integer
                        "description": data.get('description', ''),
                        "quality": quality
                    }
                })
            
            if media_list:
                return {
                    "status": "success",
                    "data": {
                        "title": title, 
                        "author": author,
                        "media": media_list
                    }
                }
            
            # If we got here, something went wrong
            return {"status": "error", "message": "Tidak dapat mengekstrak audio dari YouTube URL. Coba link lain."}
            
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
            
            file_data = BytesIO(response.content)
            file_data.seek(0)
            
            return file_data
        except Exception as e:
            logger.error(f"Error downloading media file: {str(e)}")
            return None