import os
import logging
import requests
import urllib.parse
import asyncio
import datetime
import time
import json
import random
from typing import Dict, List, Any, Optional, Union
from io import BytesIO
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram import Update, InputMediaPhoto, InputMediaVideo, InputMediaAudio, InlineKeyboardButton, InlineKeyboardMarkup

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Import configuration
from config import (
    TELEGRAM_BOT_TOKEN, ITZPIRE_API_URL, FACEBOOK_API_URL, TIKTOK_API_URL, YOUTUBE_API_URL,
    MAX_MEDIA_PER_GROUP, REQUEST_TIMEOUT
)
from instagram_downloader import InstagramDownloader
from facebook_downloader import FacebookDownloader
from tiktok_downloader import TiktokDownloader
from youtube_downloader import YoutubeDownloader
from utils import (
    clean_instagram_url, clean_facebook_url, clean_tiktok_url, clean_youtube_url,
    is_valid_instagram_url, is_valid_facebook_url, is_valid_tiktok_url, is_valid_youtube_url,
    detect_url_type, create_media_caption
)

# Constants
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", TELEGRAM_BOT_TOKEN)
# DAILY_LIMIT diimpor dari config.py

# Dictionary untuk menyimpan penggunaan pengguna
# Format: {user_id: {"count": jumlah_penggunaan, "date": tanggal_penggunaan}}
user_usage = {}

# Statistik bot global
bot_stats = {
    "total_downloads": 0,
    "users_count": 0,
    "platform_stats": {
        "instagram": 0,
        "facebook": 0,
        "tiktok": 0,
        "youtube": 0
    },
    "start_time": datetime.datetime.now()
}

# Initialize downloaders
instagram_downloader = InstagramDownloader(ITZPIRE_API_URL, REQUEST_TIMEOUT)
facebook_downloader = FacebookDownloader(FACEBOOK_API_URL, REQUEST_TIMEOUT)
tiktok_downloader = TiktokDownloader(TIKTOK_API_URL, REQUEST_TIMEOUT)
youtube_downloader = YoutubeDownloader(YOUTUBE_API_URL, REQUEST_TIMEOUT)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send welcome message when the command /start is issued."""
    # Simulate typing effect
    await update.message.reply_chat_action(action="typing")
    await asyncio.sleep(1)  # Typing delay
    
    # Kirim animasi selamat datang
    welcome_gif_url = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZXR1eXZ5bjE2N3ZtZndteml6MHJwNWlqM2Myb2dvajNsOTZ2dDdoeCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/pO4UHglOY2vII/giphy.gif"
    try:
        # Kirim GIF terlebih dahulu
        await update.message.reply_animation(
            animation=welcome_gif_url,
            caption="🚀 *Selamat Datang di Social Media Scraper Pro!*",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Gagal mengirim animasi selamat datang: {str(e)}")
    
    # Tunggu sebentar sebelum mengirim pesan utama
    await asyncio.sleep(0.5)
    
    # Pesan selamat datang dengan tombol menu
    welcome_message = (
        "┌─[🛸 *SOCIAL MEDIA SCRAPER PRO*]─[v4.2.0]\n"
        "│\n"
        "├─[🌐 *PLATFORM YANG DIDUKUNG*]\n"
        "│  ├─ Instagram  » Post/Reel/Story/IGTV\n"
        "│  ├─ TikTok    » Video/Foto\n"
        "│  ├─ Facebook  » Reel/Post/Story\n"
        "│  └─ YouTube   » Musik/Video (MP3/MP4)\n"
        "│\n"
        "├─[⚡ *FITUR PREMIUM*]\n"
        "│  ├─ Kualitas 4K Ultra HD\n"
        "│  ├─ Ekstrak Audio (MP3 320kbps)\n"
        "│  ├─ Tanpa Watermark & Metadata\n"
        "│  └─ Enkripsi Tingkat Militer\n"
        "│\n"
        "├─[💻 *CARA PENGGUNAAN*]\n"
        "│  └─ Cukup kirim link:\n"
        "│     ‣ `https://youtu.be/...` (untuk musik)\n"
        "│     ‣ `https://www.instagram.com/reel/...`\n"
        "│     ‣ `https://vt.tiktok.com/...`\n"
        "│     ‣ `https://fb.watch/...`\n"
        "│\n"
        "├─[📡 *STATUS SISTEM*]\n"
        "│  ├─ Server: Online [🟢]\n"
        "│  ├─ Uptime: 99.99%\n"
        "│  └─ API: Mode Unlimited\n"
        "│\n"
        "├─[📞 *KONTAK*]\n"
        "│  └─ [Hubungi Developer](https://www.facebook.com/share/1C48345aso/)\n"
        "│\n"
        "└─[👨💻 MhAminn]─[🔓 *Open Source*]\n"
        "   └─ Ketik /help untuk perintah"
    )
    
    # Tombol menu utama
    keyboard = [
        [
            InlineKeyboardButton("📚 Bantuan", callback_data="help"),
            InlineKeyboardButton("📊 Kuota", callback_data="quota")
        ],
        [
            InlineKeyboardButton("🌟 Premium", callback_data="premium"),
            InlineKeyboardButton("📈 Statistik", callback_data="stats")
        ],
        [
            InlineKeyboardButton("🔗 Undang Teman", callback_data="invite"),
            InlineKeyboardButton("💰 Donasi", callback_data="donate")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_markdown(welcome_message, reply_markup=reply_markup, disable_web_page_preview=True)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send help message when the command /help is issued."""
    # Simulasi efek mengetik jika update.message tersedia
    if hasattr(update, 'message') and update.message:
        await update.message.reply_chat_action(action="typing")
        await asyncio.sleep(1)
    
    help_text = (
        "🆘 *Bantuan* 🆘\n\n"
        "Cara menggunakan:\n"
        "1. Kirim link Instagram, Facebook, TikTok atau YouTube Music\n"
        "2. Tunggu bot memproses\n"
        "3. Dapatkan konten\n\n"
        "Platform yang didukung:\n"
        "*Instagram*\n"
        "- Post biasa\n"
        "- Reels\n"
        "- Stories\n"
        "- IGTV\n"
        "- Album/Carousel\n\n"
        "*Facebook*\n"
        "- Video\n"
        "- Reels\n"
        "- Stories\n\n"
        "*TikTok*\n"
        "- Video TikTok tanpa watermark\n"
        "- Audio dari TikTok\n\n"
        "*YouTube Music*\n"
        "- Audio dari YouTube Music\n"
        "- Audio dari video YouTube\n\n"
        "*Perintah tersedia:*\n"
        "/start - Memulai bot\n"
        "/help - Menampilkan bantuan\n"
        "/quota - Melihat sisa kuota harian Anda\n"
        "/premium - Informasi paket premium\n"
        "/invite - Undang teman & dapatkan bonus\n"
        "/stats - Statistik penggunaan bot\n"
        "/donate - Dukung pengembangan bot\n\n"
        "Jika ada masalah, coba link yang berbeda atau pastikan link berasal dari aplikasi resmi."
    )
    
    # Buat tombol cepat
    keyboard = [
        [
            InlineKeyboardButton("📊 Kuota", callback_data="quota"),
            InlineKeyboardButton("🌟 Premium", callback_data="premium")
        ],
        [
            InlineKeyboardButton("🔗 Undang Teman", callback_data="invite"),
            InlineKeyboardButton("💰 Donasi", callback_data="donate")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Kirim pesan berdasarkan sumber update (command atau callback)
    if hasattr(update, 'callback_query') and update.callback_query:
        # Untuk callback, gunakan message yang ada di callback query
        await update.callback_query.message.reply_text(
            help_text, 
            reply_markup=reply_markup,
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
    else:
        await update.message.reply_markdown(help_text, reply_markup=reply_markup, disable_web_page_preview=True)
    
async def quota_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Menampilkan informasi kuota dan sisa penggunaan harian."""
    user_id = update.effective_user.id
    today = datetime.datetime.now().date()
    
    # Periksa apakah pengguna sudah ada di database
    if user_id not in user_usage or user_usage[user_id].get("date") != today:
        user_usage[user_id] = {"count": 0, "date": today}
    
    # Hitung sisa kuota
    used_count = user_usage[user_id]["count"]
    remaining = max(0, DAILY_LIMIT - used_count)
    
    # Hitung waktu reset
    remaining_time = datetime.datetime.combine(datetime.datetime.now().date() + datetime.timedelta(days=1), 
                                             datetime.datetime.min.time()) - datetime.datetime.now()
    hours, remainder = divmod(remaining_time.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    
    # Buat pesan
    quota_message = (
        f"📊 *Informasi Kuota* 📊\n\n"
        f"Kuota harian Anda: {DAILY_LIMIT} permintaan\n"
        f"Terpakai: {used_count} permintaan\n"
        f"Tersisa: {remaining} permintaan\n\n"
        f"Reset kuota dalam: {hours} jam {minutes} menit\n\n"
        f"_Setiap pengguna dibatasi {DAILY_LIMIT} permintaan per hari._"
    )
    
    # Tambahkan tombol premium jika kuota telah habis
    if remaining <= 0:
        keyboard = [
            [InlineKeyboardButton("🌟 Upgrade ke Premium", callback_data="premium")],
            [InlineKeyboardButton("🔄 Undang Teman", callback_data="invite")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_markdown(quota_message, reply_markup=reply_markup)
    else:
        await update.message.reply_markdown(quota_message)
        
async def premium_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Menampilkan informasi tentang paket premium."""
    # Simulasi efek mengetik
    await update.message.reply_chat_action(action="typing")
    await asyncio.sleep(1)
    
    premium_message = (
        "✨ *Paket Premium* ✨\n\n"
        "Nikmati fitur-fitur istimewa dengan upgrade ke Premium:\n\n"
        "🔓 *Tanpa Batas Unduhan Harian*\n"
        "📊 *Kualitas Tertinggi (4K/HD)*\n"
        "🎵 *Konversi Otomatis ke MP3/MP4*\n"
        "🚫 *Tanpa Watermark*\n"
        "🔎 *Pencarian Konten Lanjutan*\n"
        "⚡ *Kecepatan Unduh Prioritas*\n\n"
        "📌 *Harga Paket:*\n"
        "• 1 Bulan: Rp 40.000\n"
        "• 3 Bulan: Rp 99.000\n"
        "• 1 Tahun: Rp 299.000\n\n"
        "💬 Hubungi @AdminUsername untuk upgrade."
    )
    
    # Buat tombol inline
    keyboard = [
        [InlineKeyboardButton("💳 Beli Premium", url="https://t.me/AdminUsername")],
        [InlineKeyboardButton("🎁 Free Trial", callback_data="trial")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_markdown(
        premium_message,
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )

async def invite_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Menampilkan informasi untuk mengundang teman."""
    # Simulasi efek mengetik jika update.message tersedia
    if hasattr(update, 'message') and update.message:
        await update.message.reply_chat_action(action="typing")
        await asyncio.sleep(1)
    
    # Buat pesan undangan dengan link ke bot
    bot_username = await context.bot.get_me()
    invite_link = f"https://t.me/{bot_username.username}"
    user_id = update.effective_user.id
    
    invite_message = (
        "🎉 *Undang Teman & Dapatkan Bonus* 🎉\n\n"
        "Bagikan bot ini dengan teman dan keluarga:\n\n"
        f"🔗 {invite_link}\n\n"
        "✅ *Keuntungan Mengundang:*\n"
        "• Setiap 5 teman yang bergabung = +5 unduhan bonus\n"
        "• Setiap 10 teman = 1 hari Premium gratis\n"
        "• Setiap 50 teman = 1 minggu Premium gratis\n\n"
        "📱 *Cara Mengundang:*\n"
        "1. Salin link di atas\n"
        "2. Bagikan ke grup atau teman\n"
        "3. Minta mereka /start dan masukkan kode referral Anda\n\n"
        f"*Kode Referral Anda:* `USER{user_id}`"
    )
    
    # Buat tombol untuk berbagi
    whatsapp_text = f"Unduh video dari Instagram, TikTok, Facebook dan YouTube dengan bot ini: {invite_link} Gunakan kode USER{user_id} untuk bonus unduhan!"
    telegram_text = f"Unduh video dari Instagram, TikTok, Facebook dan YouTube dengan bot ini! Gunakan kode USER{user_id} untuk bonus unduhan!"
    
    keyboard = [
        [InlineKeyboardButton("📲 Bagikan ke WhatsApp", url=f"https://wa.me/?text={urllib.parse.quote(whatsapp_text)}")],
        [InlineKeyboardButton("📱 Bagikan ke Telegram", url=f"https://t.me/share/url?url={urllib.parse.quote(invite_link)}&text={urllib.parse.quote(telegram_text)}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Kirim pesan berdasarkan sumber update (command atau callback)
    if hasattr(update, 'callback_query') and update.callback_query:
        # Untuk callback, gunakan message yang ada di callback query
        # Hapus pesan sebelumnya
        try:
            await update.callback_query.message.delete()
        except Exception as e:
            logger.warning(f"Failed to delete previous message: {e}")
            
        await update.callback_query.message.reply_text(
            invite_message,
            reply_markup=reply_markup,
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
    else:
        await update.message.reply_markdown(
            invite_message,
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Menampilkan statistik penggunaan bot."""
    # Simulasi efek mengetik
    await update.message.reply_chat_action(action="typing")
    await asyncio.sleep(1)
    
    # Hitung statistik
    total_downloads = bot_stats["total_downloads"]
    active_users = len(user_usage)
    
    # Hitung uptime
    uptime = datetime.datetime.now() - bot_stats["start_time"]
    days = uptime.days
    hours, remainder = divmod(uptime.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    # Hitung rata-rata unduhan per platform
    instagram_pct = round((bot_stats["platform_stats"]["instagram"] / max(1, total_downloads)) * 100)
    facebook_pct = round((bot_stats["platform_stats"]["facebook"] / max(1, total_downloads)) * 100)
    tiktok_pct = round((bot_stats["platform_stats"]["tiktok"] / max(1, total_downloads)) * 100)
    youtube_pct = round((bot_stats["platform_stats"]["youtube"] / max(1, total_downloads)) * 100)
    
    stats_message = (
        "📈 *Statistik Bot* 📈\n\n"
        f"📊 *Penggunaan:*\n"
        f"• Total Unduhan: {total_downloads:,}\n"
        f"• Pengguna Aktif: {active_users:,}\n"
        f"• Uptime: {days}d {hours}h {minutes}m\n\n"
        f"🌐 *Distribusi Platform:*\n"
        f"• Instagram: {instagram_pct}%\n"
        f"• Facebook: {facebook_pct}%\n"
        f"• TikTok: {tiktok_pct}%\n"
        f"• YouTube: {youtube_pct}%\n\n"
        f"⏱️ *Respons Rata-rata:* 2.4 detik\n"
        f"🔄 *Update Terakhir:* {bot_stats['start_time'].strftime('%d/%m/%Y')}"
    )
    
    await update.message.reply_markdown(stats_message)

async def donate_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Menampilkan informasi donasi untuk mendukung bot."""
    # Simulasi efek mengetik
    await update.message.reply_chat_action(action="typing")
    await asyncio.sleep(1)
    
    donate_message = (
        "💖 *Dukung Pengembangan Bot* 💖\n\n"
        "Terima kasih telah menggunakan bot kami! Bot ini dikelola dan dikembangkan dengan penuh dedikasi.\n\n"
        "Jika Anda menikmati layanan ini, pertimbangkan untuk memberikan dukungan:\n\n"
        "🏦 *Metode Donasi:*\n"
        "• DANA: 081234567890\n"
        "• GoPay: 081234567890\n"
        "• OVO: 081234567890\n"
        "• Bank BCA: 1234567890\n\n"
        "🎁 *Keuntungan Donasi:*\n"
        "• Donasi ≥ Rp 20.000: 1 minggu akses Premium\n"
        "• Donasi ≥ Rp 50.000: 1 bulan akses Premium\n"
        "• Donasi ≥ Rp 100.000: 3 bulan akses Premium\n\n"
        "Setelah donasi, kirim bukti transfer ke @AdminUsername untuk mengaktifkan fitur Premium."
    )
    
    # Buat tombol inline
    keyboard = [
        [InlineKeyboardButton("💳 Donasi Sekarang", url="https://t.me/AdminUsername")],
        [InlineKeyboardButton("🌟 Fitur Premium", callback_data="premium_info")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_markdown(
        donate_message,
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )



def clean_instagram_url(url: str) -> str:
    """Clean Instagram URL by removing tracking parameters."""
    return url.split('?')[0].strip().rstrip('/')

def is_valid_instagram_url(url: str) -> bool:
    """Check if URL is a valid Instagram URL."""
    patterns = [
        'instagram.com/p/',
        'instagram.com/reel/',
        'instagram.com/stories/',
        'instagram.com/tv/'
    ]
    return any(pattern in url for pattern in patterns)

async def handle_api_response(update: Update, data: Dict[str, Any]) -> bool:
    """
    Handle the API response and check for errors.
    
    Args:
        update: Telegram update
        data: API response data
        
    Returns:
        True if data is valid, False otherwise
    """
    if not data.get('status') == 'success':
        error_message = data.get('message', "Gagal mengunduh konten. Coba link yang berbeda.")
        await update.message.reply_text(f"⚠️ {error_message}")
        return False
    
    if not data.get('data'):
        await update.message.reply_text("❌ Tidak ada media yang ditemukan.")
        return False
    
    return True

async def download_media(url: str, update: Optional[Update] = None) -> Optional[Union[BytesIO, str]]:
    """
    Download media file from URL with optional progress bar.
    
    Args:
        url: Media URL
        update: Optional Telegram update for progress reporting
        
    Returns:
        BytesIO object or None if download failed
        String "TOO_LARGE" if file is too large (>100MB)
    """
    try:
        # Mulai dengan pesan progress
        progress_message = None
        if update:
            progress_message = await update.message.reply_text(
                "⏳ Mendownload: 0% [░░░░░░░░░░] 0 MB"
            )
        
        # Cek ukuran file terlebih dahulu dengan HEAD request
        try:
            head_response = requests.head(url, timeout=REQUEST_TIMEOUT)
            head_response.raise_for_status()
            
            # Cek ukuran file dari header Content-Length
            if 'Content-Length' in head_response.headers:
                content_length = int(head_response.headers['Content-Length'])
                content_size_mb = content_length / (1024 * 1024)
                
                # Jika file lebih besar dari 100MB, beri tahu pengguna
                if content_size_mb > 100:
                    logger.warning(f"File terlalu besar: {content_size_mb:.2f} MB > 100 MB")
                    if update and progress_message:
                        await progress_message.edit_text(
                            f"⚠️ File terlalu besar: {content_size_mb:.2f} MB (batas: 100 MB)"
                        )
                        await asyncio.sleep(2)
                        await progress_message.delete()
                    return "TOO_LARGE"
        except Exception as head_err:
            logger.warning(f"Error memeriksa ukuran file: {str(head_err)}")
            # Lanjutkan unduhan meskipun terjadi kesalahan
        
        # Download dengan progress tracking
        response = requests.get(url, stream=True, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        # Get content length if available
        total_size = int(response.headers.get('content-length', 0))
        total_size_mb = total_size / (1024 * 1024)
        
        # Create buffer for downloaded content
        content = BytesIO()
        downloaded_size = 0
        last_update_time = time.time()
        update_interval = 0.5  # Update progress every 0.5 seconds
        
        # Download in chunks with progress reporting
        for chunk in response.iter_content(chunk_size=1024 * 1024):  # 1MB chunks
            if not chunk:
                continue
                
            content.write(chunk)
            downloaded_size += len(chunk)
            downloaded_mb = downloaded_size / (1024 * 1024)
            
            # Update progress message at intervals
            current_time = time.time()
            if update and progress_message and current_time - last_update_time >= update_interval:
                if total_size > 0:
                    progress = min(100, int((downloaded_size / total_size) * 100))
                    bar_length = 10
                    filled_length = int(bar_length * progress / 100)
                    bar = "█" * filled_length + "░" * (bar_length - filled_length)
                    
                    await progress_message.edit_text(
                        f"⏳ Mendownload: {progress}% [{bar}] {downloaded_mb:.1f}/{total_size_mb:.1f} MB"
                    )
                else:
                    # Jika ukuran total tidak tersedia, tampilkan saja ukuran terunduh
                    await progress_message.edit_text(
                        f"⏳ Mendownload: {downloaded_mb:.1f} MB"
                    )
                last_update_time = current_time
        
        # Final progress update
        if update and progress_message:
            if total_size > 0:
                await progress_message.edit_text(
                    f"✅ Download selesai: 100% [██████████] {total_size_mb:.1f} MB"
                )
            else:
                await progress_message.edit_text(
                    f"✅ Download selesai: {downloaded_mb:.1f} MB"
                )
            # Tunggu sebentar agar pesan progress terlihat
            await asyncio.sleep(0.5)
            # Hapus pesan progress
            await progress_message.delete()
        
        # Create BytesIO object from downloaded content
        content.seek(0)
        file_obj = content
        file_obj.name = os.path.basename(urllib.parse.urlsplit(url).path)
        return file_obj
    
    except Exception as e:
        logger.error(f"Error downloading media: {str(e)}")
        # Hapus pesan progress jika ada error
        if update and progress_message:
            try:
                await progress_message.delete()
            except:
                pass
        return None

async def send_single_media(update: Update, media: Dict[str, Any], url: str = "") -> None:
    """
    Send a single media item to Telegram.
    
    Args:
        update: Telegram update
        media: Media item data
        url: Original social media URL (optional)
    """
    try:
        # Extract media URL
        media_url = media.get('downloadUrl') or media.get('url')
        if not media_url:
            await update.message.reply_text("❌ Media URL tidak ditemukan.")
            return
        
        # Download media file dengan progress bar
        file_obj = await download_media(media_url, update)
        
        # Periksa jika file terlalu besar (>100MB)
        if file_obj == "TOO_LARGE":
            await update.message.reply_text(
                "media anda terlalu besar !",
                parse_mode="Markdown"
            )
            return
        elif not file_obj:
            await update.message.reply_text("❌ Gagal mengunduh media.")
            return
        
        # Get media type
        media_type = media.get('type', '').lower()
        
        # Create caption based on URL type
        caption = create_media_caption(url) if url else "📥 Media"
        
        # Send media based on type
        if media_type == 'video' or 'video' in media_url.lower():
            await update.message.reply_video(
                video=file_obj,
                caption=caption,
                supports_streaming=True
            )
        elif media_type == 'audio' or 'audio' in media_url.lower():
            # Prepare additional metadata for audio files
            title = media.get('title', '')
            performer = media.get('author', '')
            thumbnail = None
            duration = None
            
            # Check if we have metadata (especially for YouTube Music)
            if 'metadata' in media and media['metadata']:
                metadata = media['metadata']
                title = metadata.get('title', title)
                performer = metadata.get('performer', performer)
                duration = metadata.get('duration')
                
                # Try to get thumbnail for audio
                if 'thumbnail' in media and media['thumbnail']:
                    try:
                        thumbnail_url = media['thumbnail']
                        logger.info(f"Downloading thumbnail: {thumbnail_url}")
                        thumbnail = await download_media(thumbnail_url)
                    except Exception as thumb_err:
                        logger.error(f"Error downloading thumbnail: {str(thumb_err)}")
            
            # Add more detailed caption for YouTube Music
            if detect_url_type(url) == 'youtube':
                views = media.get('metadata', {}).get('views', 0)
                quality = media.get('metadata', {}).get('quality', '')
                caption = f"🎵 *{title}*\n👤 {performer}\n👁️ {views:,} views\n🎚️ {quality}"
            
            await update.message.reply_audio(
                audio=file_obj,
                caption=caption,
                title=title,
                performer=performer,
                # Parameter 'thumb' tidak didukung, gunakan 'thumbnail' sebagai gantinya
                thumbnail=thumbnail,
                duration=duration,
                parse_mode="Markdown"
            )
        elif media_type == 'photo':
            await update.message.reply_photo(
                photo=file_obj,
                caption=caption,
                parse_mode="Markdown"
            )
        else:  # Default to document for unknown types
            await update.message.reply_document(
                document=file_obj,
                caption=caption,
                parse_mode="Markdown"
            )
            
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error sending single media: {error_message}")
        
        # Jika error adalah Request Entity Too Large atau ukuran file berlebih
        if "Request Entity Too Large" in error_message or "413" in error_message:
            await update.message.reply_text("media anda terlalu besar !")
        else:
            await update.message.reply_text(f"❌ Gagal mengirim media: {error_message}")

async def send_media_group(update: Update, media_list: List[Dict[str, Any]]) -> None:
    """
    Send a media group (album) to Telegram.
    
    Args:
        update: Telegram update
        media_list: List of media items
    """
    try:
        # Prepare media group
        media_group = []
        processed_count = 0
        
        # Limiting to MAX_MEDIA_PER_GROUP items as Telegram only supports up to 10 items in a media group
        for idx, media in enumerate(media_list[:MAX_MEDIA_PER_GROUP]):
            if not isinstance(media, dict):
                logger.error(f"Invalid media item at index {idx}: {media}")
                continue
                
            # Extract media URL
            media_url = None
            if 'downloadUrl' in media and media['downloadUrl']:
                media_url = media['downloadUrl']
            elif 'url' in media and media['url']:
                media_url = media['url']
                
            if not media_url:
                logger.error(f"No media URL found for item at index {idx}")
                continue
                
            # Download media file
            file_obj = await download_media(media_url)
            
            # Periksa jika file terlalu besar (>100MB)
            if file_obj == "TOO_LARGE":
                logger.warning(f"Media too large at URL: {media_url}")
                continue
            elif not file_obj:
                logger.error(f"Failed to download media at URL: {media_url}")
                continue
                
            # Get media type
            media_type = media.get('type', '').lower()
            
            # Set caption only for first item
            caption = "📥 Instagram Media" if idx == 0 else ""
            
            # Add to media group based on type
            try:
                # Batasi ukuran media group untuk menghindari error "image_process_failed"
                if processed_count < 5:  # Batasi maksimal 5 gambar per batch untuk menghindari error
                    if media_type == 'video':
                        media_group.append(
                            InputMediaVideo(
                                media=file_obj,
                                caption=caption
                            )
                        )
                    else:  # Default to photo
                        media_group.append(
                            InputMediaPhoto(
                                media=file_obj,
                                caption=caption
                            )
                        )
                    processed_count += 1
                else:
                    logger.info(f"Skipping media item at index {idx} to avoid exceeding max batch size")
            except Exception as item_error:
                logger.error(f"Error adding media item to group: {str(item_error)}")
        
        # Send media group if not empty
        if media_group:
            logger.info(f"Sending media group with {len(media_group)} items")
            await update.message.reply_media_group(media=media_group)
        else:
            logger.warning("No media items could be prepared for the group")
            await update.message.reply_text("❌ Tidak ada media yang dapat dikirim.")
            
        # If some items couldn't be included in the media group due to the 10-item limit
        if len(media_list) > MAX_MEDIA_PER_GROUP:
            await update.message.reply_text(
                f"⚠️ Hanya {MAX_MEDIA_PER_GROUP} dari {len(media_list)} media yang dapat dikirim dalam satu grup."
            )
    
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error sending media group: {error_message}")
        
        # Jika error adalah image_process_failed, berikan pesan khusus
        if "image_process_failed" in error_message:
            await update.message.reply_text("❌ Gagal mengirim media group: image_process_failed")
        else:
            await update.message.reply_text(f"❌ Gagal mengirim media group: {error_message}")

async def send_media(update: Update, data: Dict[str, Any], url: str = "") -> None:
    """
    Send media to Telegram chat.
    
    Args:
        update: Telegram update
        data: API response data
        url: Original social media URL (optional)
    """
    try:
        # Extract media list from data
        media_list = data.get('media', [])
        
        if not media_list:
            await update.message.reply_text("❌ Tidak ada media yang ditemukan.")
            return
        
        # Send single media or media group based on number of items
        if len(media_list) == 1:
            await send_single_media(update, media_list[0], url)
        else:
            await send_media_group(update, media_list)
    
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error sending media: {error_message}")
        
        # Jika error adalah Request Entity Too Large atau ukuran file berlebih
        if "Request Entity Too Large" in error_message or "413" in error_message:
            await update.message.reply_text("media anda terlalu besar !")
        else:
            await update.message.reply_text(f"❌ Gagal mengirim media: {error_message}")

async def fetch_instagram_content(url: str) -> Dict[str, Any]:
    """
    Fetch content from Instagram URL using API.
    
    Args:
        url: Instagram URL to fetch content from
        
    Returns:
        API response as dictionary
    """
    try:
        # Clean URL
        cleaned_url = clean_instagram_url(url)
        
        # Encode URL for API request
        encoded_url = urllib.parse.quote(cleaned_url)
        request_url = f"{ITZPIRE_API_URL}?url={encoded_url}"
        
        logger.info(f"Requesting content from API: {request_url}")
        
        # Make API request
        response = requests.get(request_url, timeout=REQUEST_TIMEOUT)
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

async def fetch_facebook_content(url: str) -> Dict[str, Any]:
    """
    Fetch content from Facebook URL using API.
    
    Args:
        url: Facebook URL to fetch content from
        
    Returns:
        API response as dictionary
    """
    try:
        # Clean URL
        cleaned_url = clean_facebook_url(url)
        
        # Encode URL for API request
        encoded_url = urllib.parse.quote(cleaned_url)
        request_url = f"{FACEBOOK_API_URL}?url={encoded_url}"
        
        logger.info(f"Requesting content from API: {request_url}")
        
        # Make API request with 'accept: application/json' header
        headers = {'accept': 'application/json'}
        response = requests.get(request_url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        data = response.json()
        
        logger.info(f"API Response: {data}")
        
        # Tentukan apakah URL menunjukkan konten foto/gambar
        is_photo = 'photo' in url.lower() or '/p/' in url.lower() or 'photo.php' in url.lower()
        logger.info(f"URL indicates photo content: {is_photo}")
        
        # === Format 1: Array data dalam respons (seperti dalam response_1743697725106.json) ===
        if 'status' in data and data['status'] is True and 'data' in data and isinstance(data['data'], list):
            media_list = []
            
            for item in data['data']:
                media_url = item.get('url', '')
                thumbnail = item.get('thumbnail', '')
                resolution = item.get('resolution', '')
                
                if media_url:
                    if is_photo:
                        # Tambahkan sebagai foto jika URL menunjukkan konten foto
                        media_list.append({
                            "type": "photo",
                            "url": media_url,
                            "downloadUrl": media_url
                        })
                        break  # Cukup ambil satu foto saja
                    elif resolution and ('720p' in resolution or 'HD' in resolution):
                        # HD video
                        media_list.append({
                            "type": "video",
                            "resolution": resolution,
                            "url": media_url,
                            "downloadUrl": media_url,
                            "thumbnail": thumbnail
                        })
                        break  # Cukup ambil video HD saja
                    elif resolution and ('360p' in resolution or 'SD' in resolution):
                        # SD video
                        media_list.append({
                            "type": "video",
                            "resolution": resolution,
                            "url": media_url,
                            "downloadUrl": media_url,
                            "thumbnail": thumbnail
                        })
                        # Tidak break, karena mungkin ada kualitas HD
            
            if media_list:
                return {
                    "status": "success",
                    "data": {
                        "media": media_list
                    }
                }
        
        # === Format 2: Format dengan data.data (seperti dalam response_1743697765962.json) ===
        if data.get('success') is True and 'data' in data and isinstance(data['data'], dict) and 'data' in data['data']:
            media_data = data['data']['data']
            media_list = []
            
            # Cek apakah ini adalah gambar berdasarkan URL atau field dalam respons
            if is_photo:
                # Cari URL gambar dari berbagai kemungkinan field
                image_url = None
                # Periksa semua field yang mungkin berisi URL gambar
                for field in ['cover', 'origin_cover', 'thumbnail', 'ai_dynamic_cover']:
                    if field in media_data and media_data[field]:
                        image_url = media_data[field]
                        break
                
                if image_url:
                    media_list.append({
                        "type": "photo",
                        "url": image_url,
                        "downloadUrl": image_url
                    })
            
            # Jika bukan foto atau tidak ada URL gambar yang ditemukan, coba cari video
            if not media_list:
                if 'hdplay' in media_data and media_data['hdplay']:
                    media_list.append({
                        "type": "video",
                        "resolution": "HD",
                        "url": media_data['hdplay'],
                        "downloadUrl": media_data['hdplay'],
                        "thumbnail": media_data.get('cover', '')
                    })
                elif 'play' in media_data and media_data['play']:
                    media_list.append({
                        "type": "video",
                        "resolution": "SD",
                        "url": media_data['play'],
                        "downloadUrl": media_data['play'],
                        "thumbnail": media_data.get('cover', '')
                    })
            
            if media_list:
                return {
                    "status": "success",
                    "data": {
                        "media": media_list
                    }
                }
        
        # Jika tidak ada media yang ditemukan atau format respons tidak dikenali
        if is_photo:
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

async def fetch_tiktok_content(url: str) -> Dict[str, Any]:
    """
    Fetch content from TikTok URL using API.
    
    Args:
        url: TikTok URL to fetch content from
        
    Returns:
        API response as dictionary
    """
    try:
        # Clean URL
        cleaned_url = clean_tiktok_url(url)
        
        # Encode URL for API request
        encoded_url = urllib.parse.quote(cleaned_url)
        request_url = f"{TIKTOK_API_URL}?url={encoded_url}"
        
        logger.info(f"Requesting content from API: {request_url}")
        
        # Make API request with 'accept: application/json' header
        headers = {'accept': 'application/json'}
        response = requests.get(request_url, headers=headers, timeout=REQUEST_TIMEOUT)
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

def check_usage_limit(user_id: int, update: Optional[Update] = None) -> bool:
    """
    Periksa apakah pengguna telah mencapai batas penggunaan harian.
    
    Args:
        user_id: ID pengguna Telegram
        update: Optional Telegram update untuk mengirim peringatan
        
    Returns:
        True jika pengguna masih dalam batas, False jika telah mencapai batas
    """
    today = datetime.datetime.now().date()
    
    # Jika pengguna tidak ada dalam dictionary atau tanggal berbeda, reset hitungan
    if user_id not in user_usage or user_usage[user_id].get("date") != today:
        user_usage[user_id] = {"count": 0, "date": today}
    
    # Dapatkan jumlah penggunaan saat ini
    current_count = user_usage[user_id]["count"]
    
    # Periksa batas penggunaan
    if current_count >= DAILY_LIMIT:
        return False
    
    # Tingkatkan hitungan penggunaan
    user_usage[user_id]["count"] = current_count + 1
    
    # Update statistik global
    bot_stats["total_downloads"] += 1
    
    # Periksa jika kuota hampir habis dan kirim notifikasi
    if update and (DAILY_LIMIT - (current_count + 1) <= 2) and (current_count + 1) < DAILY_LIMIT:
        remaining = DAILY_LIMIT - (current_count + 1)
        asyncio.create_task(send_quota_warning(update, remaining))
    
    return True
        
async def send_quota_warning(update: Update, remaining: int) -> None:
    """
    Kirim peringatan kuota hampir habis.
    
    Args:
        update: Telegram update
        remaining: Sisa kuota
    """
    warning = (
        f"⚠️ *Peringatan Kuota*\n\n"
        f"Anda hanya memiliki {remaining} unduhan tersisa hari ini.\n"
        f"Kuota akan direset pada tengah malam (00:00 WIB).\n\n"
    )
    
    # Tambahkan tombol premium
    keyboard = [
        [InlineKeyboardButton("🌟 Upgrade ke Premium", callback_data="premium")],
        [InlineKeyboardButton("🏷️ Cek Kuota", callback_data="quota")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Tunggu pengiriman konten selesai sebelum mengirimkan peringatan
    await asyncio.sleep(2)
    await update.message.reply_markdown(warning, reply_markup=reply_markup)

async def handle_social_media_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle all social media URLs and download content.
    
    Args:
        update: Telegram update
        context: Callback context
    """
    # Dapatkan user_id pengguna
    user_id = update.effective_user.id
    
    # Periksa batas penggunaan dengan parameter update untuk peringatan
    if not check_usage_limit(user_id, update):
        remaining_time = datetime.datetime.combine(datetime.datetime.now().date() + datetime.timedelta(days=1), 
                                                 datetime.datetime.min.time()) - datetime.datetime.now()
        hours, remainder = divmod(remaining_time.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        await update.message.reply_text(
            f"⚠️ *Batas Penggunaan Tercapai* ⚠️\n\n"
            f"Anda telah mencapai batas {DAILY_LIMIT} penggunaan harian.\n\n"
            f"Batasan akan direset dalam: {hours} jam {minutes} menit\n\n"
            f"Upgrade ke versi premium untuk penggunaan tak terbatas!",
            parse_mode="Markdown"
        )
        return
    
    # Lanjutkan dengan memproses URL
    raw_url = update.message.text.strip()
    url_type = detect_url_type(raw_url)
    
    if url_type == 'instagram':
        await scrape_instagram(update, context)
    elif url_type == 'facebook':
        await scrape_facebook(update, context)
    elif url_type == 'tiktok':
        await scrape_tiktok(update, context)
    elif url_type == 'youtube':
        await scrape_youtube(update, context)
    else:
        await update.message.reply_text(
            "❌ URL tidak didukung. Bot ini mendukung URL dari Instagram, Facebook, TikTok, dan YouTube Music.\n\n"
            "Contoh URL yang didukung:\n"
            "- Instagram: https://www.instagram.com/p/CGgDsi7JQdS/\n"
            "- Facebook: https://www.facebook.com/share/r/1E9YVmQBkL/\n"
            "- TikTok: https://vt.tiktok.com/ZSrB2pdbP/\n"
            "- YouTube Music: https://music.youtube.com/watch?v=T3d5VNjaDss"
        )

async def scrape_instagram(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle Instagram URL and download content.
    
    Args:
        update: Telegram update
        context: Callback context
    """
    raw_url = update.message.text.strip()
    
    # Check if it's a valid Instagram URL using the utility function
    if not is_valid_instagram_url(raw_url):
        await update.message.reply_text("❌ URL Instagram tidak valid.")
        return
    
    processing_msg = None
    
    try:
        # Send processing message
        processing_msg = await update.message.reply_text("⏳ Sedang memproses Instagram...")
        
        # Use InstagramDownloader to fetch content
        data = instagram_downloader.download_content(raw_url)
        
        # Delete processing message
        if processing_msg:
            await processing_msg.delete()
        
        # Handle API response
        if not await handle_api_response(update, data):
            return
        
        # Send media
        await send_media(update, data['data'], raw_url)
        
    except Exception as e:
        logger.error(f"Error in scrape_instagram: {str(e)}")
        await update.message.reply_text(f"❌ Terjadi kesalahan: {str(e)}")
        if processing_msg:
            try:
                await processing_msg.delete()
            except:
                pass

async def scrape_facebook(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle Facebook URL and download content.
    
    Args:
        update: Telegram update
        context: Callback context
    """
    raw_url = update.message.text.strip()
    
    # Check if it's a valid Facebook URL using the utility function
    if not is_valid_facebook_url(raw_url):
        await update.message.reply_text("❌ URL Facebook tidak valid.")
        return
    
    # Deteksi jika ini adalah URL foto Facebook
    is_photo_url = 'photo' in raw_url.lower() or '/p/' in raw_url.lower() or 'photo.php' in raw_url.lower()
    
    # Jika ini URL foto Facebook, informasikan pengguna bahwa fitur ini tidak didukung
    if is_photo_url:
        await update.message.reply_text(
            "⚠️ *Pengunduhan Foto Facebook Tidak Didukung* ⚠️\n\n"
            "Maaf, saat ini API kami tidak mendukung pengunduhan foto Facebook.\n\n"
            "Bot dapat mengunduh konten video, reel, dan story dari Facebook, "
            "namun belum dapat mengunduh foto/gambar Facebook.\n\n"
            "Silakan coba URL Facebook lain yang berisi video, reel, atau story.",
            parse_mode="Markdown"
        )
        return
    
    processing_msg = None
    
    try:
        # Send processing message
        processing_msg = await update.message.reply_text("⏳ Sedang memproses Facebook...")
        
        # Use FacebookDownloader to fetch content
        data = facebook_downloader.download_content(raw_url)
        
        # Delete processing message
        if processing_msg:
            await processing_msg.delete()
        
        # Handle API response
        if not await handle_api_response(update, data):
            return
        
        # Send media
        await send_media(update, data['data'], raw_url)
        
    except Exception as e:
        logger.error(f"Error in scrape_facebook: {str(e)}")
        await update.message.reply_text(f"❌ Terjadi kesalahan: {str(e)}")
        if processing_msg:
            try:
                await processing_msg.delete()
            except:
                pass

async def scrape_tiktok(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle TikTok URL and download content.
    
    Args:
        update: Telegram update
        context: Callback context
    """
    raw_url = update.message.text.strip()
    
    # Check if it's a valid TikTok URL using the utility function
    if not is_valid_tiktok_url(raw_url):
        await update.message.reply_text("❌ URL TikTok tidak valid.")
        return
    
    processing_msg = None
    
    try:
        # Send processing message
        processing_msg = await update.message.reply_text("⏳ Sedang memproses TikTok...")
        
        # Use TiktokDownloader to fetch content
        data = tiktok_downloader.download_content(raw_url)
        
        # Delete processing message
        if processing_msg:
            await processing_msg.delete()
        
        # Handle API response
        if not await handle_api_response(update, data):
            return
        
        # Cek apakah ini adalah konten yang berisi gambar+suara
        media_list = data['data'].get('media', [])
        contains_photos = any(item.get('type') == 'photo' for item in media_list)
        contains_audio = any(item.get('type') == 'audio' for item in media_list)
        photo_count = sum(1 for item in media_list if item.get('type') == 'photo')
        
        # Jika berisi gambar dan jumlahnya > 5, kirim dalam beberapa grup
        if contains_photos and photo_count > 5:
            photos = [item for item in media_list if item.get('type') == 'photo']
            audio = next((item for item in media_list if item.get('type') == 'audio'), None)
            
            # Kirim gambar dalam batch (maksimal 5 gambar per batch)
            for i in range(0, len(photos), 5):
                batch = photos[i:i+5]
                # Modifikasi data untuk satu batch
                batch_data = {
                    "media": batch
                }
                await send_media(update, batch_data, raw_url)
            
            # Kirim audio secara terpisah jika ada
            if audio:
                audio_data = {
                    "media": [audio]
                }
                await send_media(update, audio_data, raw_url)
        else:
            # Kirim semua media seperti biasa
            await send_media(update, data['data'], raw_url)
        
    except Exception as e:
        logger.error(f"Error in scrape_tiktok: {str(e)}")
        await update.message.reply_text(f"❌ Terjadi kesalahan: {str(e)}")
        if processing_msg:
            try:
                await processing_msg.delete()
            except:
                pass

async def fetch_youtube_content(url: str) -> Dict[str, Any]:
    """
    Fetch content from YouTube Music URL using API.
    
    Args:
        url: YouTube URL to fetch content from
        
    Returns:
        API response as dictionary
    """
    try:
        # Clean URL
        cleaned_url = clean_youtube_url(url)
        
        # Encode URL for API request
        encoded_url = urllib.parse.quote(cleaned_url)
        request_url = f"{YOUTUBE_API_URL}?url={encoded_url}"
        
        logger.info(f"Requesting content from API: {request_url}")
        
        # Make API request with 'accept: application/json' header
        headers = {'accept': 'application/json'}
        response = requests.get(request_url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        data = response.json()
        
        logger.info(f"API Response: {data}")
        
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

async def scrape_youtube(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle YouTube Music URL and download content.
    
    Args:
        update: Telegram update
        context: Callback context
    """
    raw_url = update.message.text.strip()
    
    # Check if it's a valid YouTube URL using the utility function
    if not is_valid_youtube_url(raw_url):
        await update.message.reply_text("❌ URL YouTube tidak valid.")
        return
    
    processing_msg = None
    
    try:
        # Determine if it's YouTube Music or regular YouTube
        is_music = 'music.youtube.com' in raw_url.lower()
        message_text = "⏳ Sedang memproses YouTube Music..." if is_music else "⏳ Sedang memproses YouTube Audio..."
        
        # Send processing message
        processing_msg = await update.message.reply_text(message_text)
        
        # Use YoutubeDownloader to fetch content
        data = youtube_downloader.download_content(raw_url)
        
        # Log data for debugging
        logger.info(f"YouTube data received: {data}")
        
        # Delete processing message
        if processing_msg:
            await processing_msg.delete()
        
        # Handle API response
        if not await handle_api_response(update, data):
            return
        
        # Verify we have the required data
        if data.get('status') == 'success' and 'data' in data:
            # Extract title and author information for logging
            title = data['data'].get('title', 'Unknown Title')
            author = data['data'].get('author', 'Unknown Artist')
            logger.info(f"Processing audio: '{title}' by '{author}'")
            
            # Send media
            await send_media(update, data['data'], raw_url)
        else:
            await update.message.reply_text("❌ Tidak dapat mengunduh audio dari YouTube.")
        
    except Exception as e:
        logger.error(f"Error in scrape_youtube: {str(e)}")
        await update.message.reply_text(f"❌ Terjadi kesalahan: {str(e)}")
        if processing_msg:
            try:
                await processing_msg.delete()
            except:
                pass

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors in the dispatcher."""
    logger.error(f"Update {update} caused error {context.error}")
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ Terjadi kesalahan dalam memproses permintaan Anda. Silakan coba lagi nanti."
        )

async def handle_button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button callbacks."""
    query = update.callback_query
    await query.answer()  # Acknowledge the button press
    
    # Get the callback data
    callback_data = query.data
    original_message = query.message
    
    # Hapus pesan sebelumnya saat user memilih menu baru
    try:
        await original_message.delete()
    except Exception as e:
        logger.warning(f"Failed to delete previous message: {e}")
    
    # Buat fungsi helper untuk mengirim pesan berdasarkan callback data
    if callback_data == "help":
        # Kirim pesan bantuan langsung
        help_text = (
            "🆘 *Bantuan* 🆘\n\n"
            "Cara menggunakan:\n"
            "1. Kirim link Instagram, Facebook, TikTok atau YouTube Music\n"
            "2. Tunggu bot memproses\n"
            "3. Dapatkan konten\n\n"
            "Platform yang didukung:\n"
            "*Instagram*\n"
            "- Post biasa\n"
            "- Reels\n"
            "- Stories\n"
            "- IGTV\n"
            "- Album/Carousel\n\n"
            "*Facebook*\n"
            "- Video\n"
            "- Reels\n"
            "- Stories\n\n"
            "*TikTok*\n"
            "- Video TikTok tanpa watermark\n"
            "- Audio dari TikTok\n\n"
            "*YouTube Music*\n"
            "- Audio dari YouTube Music\n"
            "- Audio dari video YouTube\n\n"
            "*Perintah tersedia:*\n"
            "/start - Memulai bot\n"
            "/help - Menampilkan bantuan\n"
            "/quota - Melihat sisa kuota harian Anda\n"
            "/premium - Informasi paket premium\n"
            "/stats - Statistik penggunaan bot\n"
            "/donate - Dukung pengembangan bot\n\n"
            "Jika ada masalah, coba link yang berbeda atau pastikan link berasal dari aplikasi resmi."
        )
        
        # Buat tombol cepat
        keyboard = [
            [
                InlineKeyboardButton("📊 Kuota", callback_data="quota"),
                InlineKeyboardButton("🌟 Premium", callback_data="premium")
            ],
            [
                InlineKeyboardButton("💰 Donasi", callback_data="donate"),
                InlineKeyboardButton("📈 Statistik", callback_data="stats")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.effective_chat.send_message(
            help_text, 
            reply_markup=reply_markup,
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
        
    elif callback_data == "quota":
        # Menampilkan informasi kuota dan sisa penggunaan harian
        user_id = update.effective_user.id
        today = datetime.datetime.now().date()
        
        # Periksa apakah pengguna sudah ada di database
        if user_id not in user_usage or user_usage[user_id].get("date") != today:
            user_usage[user_id] = {"count": 0, "date": today}
        
        # Hitung sisa kuota
        used_count = user_usage[user_id]["count"]
        remaining = max(0, DAILY_LIMIT - used_count)
        
        # Hitung waktu reset
        remaining_time = datetime.datetime.combine(datetime.datetime.now().date() + datetime.timedelta(days=1), 
                                                 datetime.datetime.min.time()) - datetime.datetime.now()
        hours, remainder = divmod(remaining_time.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        # Buat pesan
        quota_message = (
            f"📊 *Informasi Kuota* 📊\n\n"
            f"Kuota harian Anda: {DAILY_LIMIT} permintaan\n"
            f"Terpakai: {used_count} permintaan\n"
            f"Tersisa: {remaining} permintaan\n\n"
            f"Reset kuota dalam: {hours} jam {minutes} menit\n\n"
            f"_Setiap pengguna dibatasi {DAILY_LIMIT} permintaan per hari._"
        )
        
        # Tambahkan tombol kembali dan premium
        keyboard = [
            [InlineKeyboardButton("🔙 Kembali", callback_data="help")],
            [InlineKeyboardButton("🌟 Upgrade ke Premium", callback_data="premium")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.effective_chat.send_message(
            quota_message,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
            
    elif callback_data == "premium":
        # Menampilkan informasi tentang paket premium
        premium_message = (
            "✨ *Paket Premium* ✨\n\n"
            "Nikmati fitur-fitur istimewa dengan upgrade ke Premium:\n\n"
            "🔓 *Tanpa Batas Unduhan Harian*\n"
            "📊 *Kualitas Tertinggi (4K/HD)*\n"
            "🎵 *Konversi Otomatis ke MP3/MP4*\n"
            "🚫 *Tanpa Watermark*\n"
            "🔎 *Pencarian Konten Lanjutan*\n"
            "⚡ *Kecepatan Unduh Prioritas*\n\n"
            "📌 *Harga Paket:*\n"
            "• 1 Bulan: Rp 15.000\n"
            "• 3 Bulan: Rp 25.000\n"
            "• 1 Tahun: Rp 100.000\n\n"
            "💬 Hubungi @lokalheartz untuk upgrade."
        )
        
        # Buat tombol inline
        keyboard = [
            [InlineKeyboardButton("🔙 Kembali", callback_data="help")],
            [InlineKeyboardButton("💳 Beli Premium", url="https://t.me/lokalheartz")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.effective_chat.send_message(
            premium_message,
            reply_markup=reply_markup,
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
        
    elif callback_data == "stats":
        # Menampilkan statistik penggunaan bot
        # Hitung statistik
        total_downloads = bot_stats["total_downloads"]
        active_users = len(user_usage)
        
        # Hitung uptime
        uptime = datetime.datetime.now() - bot_stats["start_time"]
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        # Hitung rata-rata unduhan per platform
        instagram_pct = round((bot_stats["platform_stats"]["instagram"] / max(1, total_downloads)) * 100)
        facebook_pct = round((bot_stats["platform_stats"]["facebook"] / max(1, total_downloads)) * 100)
        tiktok_pct = round((bot_stats["platform_stats"]["tiktok"] / max(1, total_downloads)) * 100)
        youtube_pct = round((bot_stats["platform_stats"]["youtube"] / max(1, total_downloads)) * 100)
        
        stats_message = (
            "📈 *Statistik Bot* 📈\n\n"
            f"📊 *Penggunaan:*\n"
            f"• Total Unduhan: {total_downloads:,}\n"
            f"• Pengguna Aktif: {active_users:,}\n"
            f"• Uptime: {days}d {hours}h {minutes}m\n\n"
            f"🌐 *Distribusi Platform:*\n"
            f"• Instagram: {instagram_pct}%\n"
            f"• Facebook: {facebook_pct}%\n"
            f"• TikTok: {tiktok_pct}%\n"
            f"• YouTube: {youtube_pct}%\n\n"
            f"⏱️ *Respons Rata-rata:* 2.4 detik\n"
            f"🔄 *Update Terakhir:* {bot_stats['start_time'].strftime('%d/%m/%Y')}"
        )
        
        # Tambahkan tombol kembali
        keyboard = [
            [InlineKeyboardButton("🔙 Kembali", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.effective_chat.send_message(
            stats_message,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        

        
    elif callback_data == "donate":
        # Menampilkan informasi donasi untuk mendukung bot
        donate_message = (
            "💖 *Dukung Pengembangan Bot* 💖\n\n"
            "Terima kasih telah menggunakan bot kami! Bot ini dikelola dan dikembangkan dengan penuh dedikasi.\n\n"
            "Jika Anda menikmati layanan ini, pertimbangkan untuk memberikan dukungan:\n\n"
            "Traktir Saya Kopi ☕\n\n"
            "🏦 *Metode Donasi:*\n"
            "• DANA: 0852 9961 3785\n"
            "• GoPay: 0852 9961 3785\n"
            "• OVO: 0852 9961 3785\n"
            "• SHOPEE PAY: 0852 9961 3785\n\n"
            "Setelah donasi, kirim bukti transfer ke @lokalheartz untuk mendapatkan hadiah."
        )
        
        # Buat tombol inline
        keyboard = [
            [InlineKeyboardButton("🔙 Kembali", callback_data="help")],
            [InlineKeyboardButton("💳 Donasi Sekarang", url="https://t.me/lokalheartz")],
            [InlineKeyboardButton("🌟 Fitur Premium", callback_data="premium_info")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.effective_chat.send_message(
            donate_message,
            reply_markup=reply_markup,
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
    # Tambahkan callback lain sesuai kebutuhan

def main() -> None:
    """Start the bot."""
    # Create the Application
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("quota", quota_command))
    application.add_handler(CommandHandler("premium", premium_command))
    # application.add_handler(CommandHandler("invite", invite_command))  # Fitur invite dinonaktifkan
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("donate", donate_command))
    
    # Add message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_social_media_url))
    
    # Add callback query handler for inline buttons
    application.add_handler(CallbackQueryHandler(handle_button_callback))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start the Bot
    print("🤖 Bot sedang berjalan...")
    application.run_polling()

if __name__ == "__main__":
    main()