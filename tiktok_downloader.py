import logging
import requests
import urllib.parse
from typing import Dict, Any, Optional, Union
from io import BytesIO

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TiktokDownloader:
    """Class for handling TikTok content downloading."""
    
    def __init__(self, api_url: str, timeout: int = 15):
        """
        Initialize the TikTok downloader.
        
        Args:
            api_url: URL for the TikTok downloading API
            timeout: Request timeout in seconds
        """
        self.api_url = api_url
        self.timeout = timeout
    
    def clean_tiktok_url(self, url: str) -> str:
        """
        Clean TikTok URL by removing tracking parameters.
        
        Args:
            url: Raw TikTok URL
            
        Returns:
            Cleaned URL
        """
        base_url = url.split('?')[0].strip().rstrip('/')
        return base_url
    
    def is_valid_tiktok_url(self, url: str) -> bool:
        """
        Check if URL is a valid TikTok URL.
        
        Args:
            url: URL to validate
            
        Returns:
            True if valid TikTok URL, False otherwise
        """
        patterns = [
            'tiktok.com/',
            'vm.tiktok.com/',
            'vt.tiktok.com/'
        ]
        return any(pattern in url for pattern in patterns)
    
    def download_content(self, url: str) -> Dict[str, Any]:
        """
        Download TikTok content from URL.
        
        Args:
            url: TikTok video URL
            
        Returns:
            Dictionary containing download response
            
        Raises:
            requests.Timeout: If request times out
            requests.RequestException: For other request errors
        """
        try:
            # Clean the URL
            clean_url = self.clean_tiktok_url(url)
            
            # Encode URL for API request
            encoded_url = urllib.parse.quote(clean_url)
            
            # Construct API request URL
            request_url = f"{self.api_url}?url={encoded_url}"
            
            logger.info(f"Requesting content from: {request_url}")
            
            # Make the request with 'accept: application/json' header
            headers = {'accept': 'application/json'}
            response = requests.get(request_url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            
            # Parse response
            data = response.json()
            
            logger.info(f"API Response status: {data.get('success', 'unknown')}")
            
            # Format the response to match our expected format
            if data.get('success') is True:
                # Extract relevant data
                tiktok_data = data.get('data', {}).get('data', {})
                
                # Kita akan memiliki dua daftar terpisah: video dan audio
                media_list = []
                
                # Extract video URLs
                play = tiktok_data.get('play')  # No watermark
                wmplay = tiktok_data.get('wmplay')  # With watermark
                hdplay = tiktok_data.get('hdplay')  # HD version
                music = tiktok_data.get('music')  # Audio/music
                cover = tiktok_data.get('cover')  # Thumbnail
                images = tiktok_data.get('images', [])  # Gambar (untuk TikTok yang berisi gambar)
                
                # Check for slideshow/image content
                if images and len(images) > 0:
                    # TikTok berisi gambar, tambahkan semua gambar
                    for i, image_url in enumerate(images):
                        media_list.append({
                            "type": "photo",
                            "quality": "HD",
                            "url": image_url,
                            "downloadUrl": image_url,
                            "thumbnail": cover,
                            "index": i
                        })
                    
                    # Tambahkan audio jika ada
                    if music:
                        media_list.append({
                            "type": "audio",
                            "url": music,
                            "downloadUrl": music
                        })
                
                # Jika bukan slideshow (tidak ada images), proses sebagai video biasa
                else:
                    # Prioritaskan video HD
                    if hdplay:
                        media_list.append({
                            "type": "video",
                            "quality": "HD",
                            "url": hdplay,
                            "downloadUrl": hdplay,
                            "thumbnail": cover
                        })
                    # Jika tidak ada HD, gunakan versi tanpa watermark
                    elif play:
                        media_list.append({
                            "type": "video",
                            "quality": "SD (No Watermark)",
                            "url": play,
                            "downloadUrl": play,
                            "thumbnail": cover
                        })
                    # Terakhir, gunakan versi dengan watermark jika tidak ada pilihan lain
                    elif wmplay:
                        media_list.append({
                            "type": "video",
                            "quality": "SD (Watermarked)",
                            "url": wmplay,
                            "downloadUrl": wmplay,
                            "thumbnail": cover
                        })
                    # Jika tidak ada video, tambahkan audio saja (jika ada)
                    elif music:
                        media_list.append({
                            "type": "audio",
                            "url": music,
                            "downloadUrl": music
                        })
                
                if media_list:
                    return {
                        "status": "success",
                        "data": {
                            "media": media_list,
                            "title": tiktok_data.get('title', '')
                        }
                    }
                
            # If we got here, something went wrong
            return {"status": "error", "message": "Tidak dapat mengekstrak konten dari TikTok URL. Coba link lain."}
            
        except requests.Timeout:
            logger.error("Request timeout")
            return {"status": "error", "message": "Request timed out"}
        except requests.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            return {"status": "error", "message": f"Request error: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return {"status": "error", "message": f"Unexpected error: {str(e)}"}
    
    def download_media_file(self, url: str) -> Union[BytesIO, str, None]:
        """
        Download media file from URL.
        
        Args:
            url: Media URL
            
        Returns:
            BytesIO object containing media file data, or None if download failed
            Returns string "TOO_LARGE" if file is too large
        """
        try:
            # Get file size with HEAD request first to check if it's too large
            head_response = requests.head(url, timeout=self.timeout)
            head_response.raise_for_status()
            
            # Check if Content-Length header exists
            if 'Content-Length' in head_response.headers:
                content_length = int(head_response.headers['Content-Length'])
                # Convert bytes to MB
                size_mb = content_length / (1024 * 1024)
                
                # Check if file size exceeds 100 MB
                if size_mb > 100:
                    logger.warning(f"File size too large: {size_mb:.2f} MB > 100 MB")
                    return "TOO_LARGE"
            
            # If size is acceptable or unknown, proceed with download
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # Double-check actual content size
            content_size = len(response.content) / (1024 * 1024)  # Convert to MB
            if content_size > 100:
                logger.warning(f"Downloaded content too large: {content_size:.2f} MB > 100 MB")
                return "TOO_LARGE"
            
            file_data = BytesIO(response.content)
            file_data.seek(0)
            
            return file_data
        except Exception as e:
            logger.error(f"Error downloading media file: {str(e)}")
            return None