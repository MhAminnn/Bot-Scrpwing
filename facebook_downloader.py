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

class FacebookDownloader:
    """Class for handling Facebook content downloading."""
    
    def __init__(self, api_url: str, timeout: int = 15):
        """
        Initialize the Facebook downloader.
        
        Args:
            api_url: URL for the Facebook downloading API
            timeout: Request timeout in seconds
        """
        self.api_url = api_url
        self.timeout = timeout
    
    def clean_facebook_url(self, url: str) -> str:
        """
        Clean Facebook URL by removing tracking parameters.
        
        Args:
            url: Raw Facebook URL
            
        Returns:
            Cleaned URL
        """
        # Pastikan URL valid dan tidak menyebabkan error
        if not url or '?' not in url:
            return url.strip().rstrip('/')
        
        base_url = url.split('?')[0].strip().rstrip('/')
        return base_url
    
    def is_valid_facebook_url(self, url: str) -> bool:
        """
        Check if URL is a valid Facebook URL.
        
        Args:
            url: URL to validate
            
        Returns:
            True if valid Facebook URL, False otherwise
        """
        patterns = [
            'facebook.com/watch',
            'facebook.com/story',
            'facebook.com/share',
            'facebook.com/reel',
            'facebook.com/photo',     # Tambahan untuk URL foto
            'facebook.com/photo.php', # Tambahan format URL foto
            'facebook.com/p/',        # Tambahan untuk URL foto singkat
            'fb.watch/',
            'fb.com/'
        ]
        return any(pattern in url for pattern in patterns)
    
    def download_content(self, url: str) -> Dict[str, Any]:
        """
        Download Facebook content from URL.
        
        Args:
            url: Facebook post/video/reel URL
            
        Returns:
            Dictionary containing download response
            
        Raises:
            requests.Timeout: If request times out
            requests.RequestException: For other request errors
        """
        try:
            # Clean the URL
            clean_url = self.clean_facebook_url(url)
            
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
            
            logger.info(f"API Response: {data}")
            
            # Format the response to match our expected format
            if data.get('status') is True:
                media_list = []
                hd_video = None
                sd_video = None
                image = None
                
                # Periksa apakah ini adalah gambar atau video
                is_image = False
                is_video = False
                
                # Periksa apakah ini adalah gambar
                if 'photo' in url.lower() or '/p/' in url.lower():
                    is_image = True
                
                # Mencari konten (video atau gambar) berdasarkan respons API
                for video_data in data.get('data', []):
                    media_url = video_data.get('url')
                    if not media_url:
                        continue
                        
                    resolution = video_data.get('resolution', 'Unknown')
                    thumbnail = video_data.get('thumbnail', '')
                    
                    # Deteksi jenis konten berdasarkan URL atau header
                    if is_image or '.jpg' in media_url.lower() or '.jpeg' in media_url.lower() or '.png' in media_url.lower():
                        # Ini adalah gambar
                        image = {
                            "type": "photo",
                            "url": media_url,
                            "downloadUrl": media_url
                        }
                    elif '720p' in resolution:
                        hd_video = {
                            "type": "video",
                            "resolution": resolution,
                            "url": media_url,
                            "downloadUrl": media_url,
                            "thumbnail": thumbnail
                        }
                    elif '360p' in resolution or 'SD' in resolution:
                        sd_video = {
                            "type": "video",
                            "resolution": resolution,
                            "url": media_url,
                            "downloadUrl": media_url,
                            "thumbnail": thumbnail
                        }
                
                # Prioritas: Gambar > HD > SD
                if image:
                    media_list.append(image)
                elif hd_video:
                    media_list.append(hd_video)
                elif sd_video:
                    media_list.append(sd_video)
                
                if media_list:
                    return {
                        "status": "success",
                        "data": {
                            "media": media_list
                        }
                    }
            
            # Jika format respons berbeda (seperti yang kita lihat di respons API contoh)
            # Ini adalah format alternatif yang perlu ditangani
            if data.get('success') is True:
                media_list = []
                # Periksa apakah ini adalah gambar atau video
                is_image = False
                
                # Periksa apakah ini adalah gambar berdasarkan URL
                if 'photo' in url.lower() or '/p/' in url.lower() or 'photo.php' in url.lower():
                    is_image = True
                
                # Format JSON respons yang berbeda berdasarkan contoh
                if 'data' in data and isinstance(data['data'], dict) and 'data' in data['data']:
                    media_data = data['data']['data']
                    
                    # Coba cari gambar jika URL menunjukkan bahwa ini adalah gambar
                    if is_image:
                        # Cari URL gambar dari berbagai kemungkinan field
                        image_url = None
                        # Periksa semua field yang mungkin berisi URL gambar
                        for field in ['cover', 'origin_cover', 'thumbnail', 'ai_dynamic_cover']:
                            if field in media_data and media_data[field]:
                                image_url = media_data[field]
                                logger.info(f"Found image URL in field {field}: {image_url}")
                                break
                        
                        if image_url:
                            media_list.append({
                                "type": "photo",
                                "url": image_url,
                                "downloadUrl": image_url
                            })
                    
                    # Jika tidak ada gambar atau bukan URL gambar, cari video
                    if not media_list:
                        if 'hdplay' in media_data and media_data['hdplay']:
                            hd_video = {
                                "type": "video",
                                "resolution": "HD",
                                "url": media_data['hdplay'],
                                "downloadUrl": media_data['hdplay'],
                                "thumbnail": media_data.get('cover', '')
                            }
                            media_list.append(hd_video)
                        elif 'play' in media_data and media_data['play']:
                            sd_video = {
                                "type": "video",
                                "resolution": "SD",
                                "url": media_data['play'],
                                "downloadUrl": media_data['play'],
                                "thumbnail": media_data.get('cover', '')
                            }
                            media_list.append(sd_video)
                
                if media_list:
                    return {
                        "status": "success",
                        "data": {
                            "media": media_list
                        }
                    }
                
            # If we got here, something went wrong
            if 'photo' in url.lower() or '/p/' in url.lower() or 'photo.php' in url.lower():
                return {"status": "error", "message": "Tidak dapat mengekstrak gambar dari Facebook URL. Coba link lain."}
            else:
                return {"status": "error", "message": "Tidak dapat mengekstrak video dari Facebook URL. Coba link lain."}
            
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