# 🛸 SOCIAL MEDIA SCRAPER PRO 🛸

<div align="center">
  <img src="https://i.imgur.com/waxVImv.png" alt="Separator" width="600"/>
</div>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python Version"/>
  <img src="https://img.shields.io/badge/Telegram_Bot_API-v6.5+-green.svg" alt="Telegram Bot API"/>
  <img src="https://img.shields.io/badge/Async-Powered-purple.svg" alt="Async"/>
  <img src="https://img.shields.io/badge/HD_Quality-4K-orange.svg" alt="HD Quality"/>
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License"/>
</p>

## 🔥 Ringkasan

**Social Media Scraper Pro** adalah bot Telegram canggih yang dirancang untuk mengekstrak dan mengunduh konten media dari berbagai platform sosial media populer. Bot ini memanfaatkan teknologi canggih untuk menghasilkan media berkualitas tinggi tanpa watermark dan metadata yang tidak diperlukan.

## ✨ Fitur Utama

- **🌐 Multi-Platform Support:**
  - Instagram: Post, Reels, Stories, IGTV, Carousel
  - TikTok: Video HD tanpa watermark, Audio
  - Facebook: Video, Reels, Stories
  - YouTube: Audio/Musik berkualitas tinggi dengan metadata lengkap

- **🔧 Kemampuan Teknis:**
  - Kualitas 4K Ultra HD untuk video
  - Ekstraksi audio MP3 320kbps 
  - Download tanpa watermark
  - Menampilkan thumbnail untuk audio
  - Metadata lengkap (judul, artis, durasi, views)

- **👤 Manajemen Pengguna:**
  - Batas 10 penggunaan per pengguna per hari
  - Sistem reset kuota otomatis pada pukul 00:00
  - Tracking pengguna dengan ID Telegram
  - Perintah `/quota` untuk mengecek sisa batasan

## 🚀 Teknologi yang Digunakan

### Backend Core

- **Python 3.10+**: Bahasa pemrograman utama, memberikan fleksibilitas dan kemudahan pengembangan
- **python-telegram-bot**: Library asinkron untuk interaksi dengan API Telegram
- **asyncio**: Memungkinkan operasi asinkron dan konkurensi yang efisien
- **requests**: Untuk melakukan HTTP requests ke API eksternal

### Pemrosesan Media

- **BytesIO**: Penanganan file secara efisien di memory tanpa perlu penyimpanan lokal
- **urllib.parse**: Manipulasi URL dan sanitasi parameter
- **datetime**: Manajemen perhitungan waktu untuk sistem kuota
- **JSON Processing**: Penanganan data terstruktur dari API responses

### Arsitektur

- **Class-Based Design**: Penerapan prinsip OOP dengan kelas downloader terpisah per platform
- **Asynchronous Architecture**: Meningkatkan responsivitas dan throughput dengan operasi non-blocking
- **Modular Structure**: Komponen terpisah untuk downloader, utility functions, dan handlers
- **Error Handling**: Sistem penanganan error komprehensif dengan logging

## 💡 Keunggulan Teknis

1. **Performa Tinggi**
   - Penggunaan memori efisien dengan streaming file langsung ke Telegram
   - Pendekatan asinkron mengurangi waktu tunggu

2. **Ketahanan**
   - Penanganan error dengan graceful recovery
   - Validasi URL komprehensif
   - Retry mechanism untuk menghadapi kegagalan jaringan

3. **Skalabilitas**
   - Arsitektur modular memudahkan penambahan platform baru
   - Sistem kuota mencegah overload server
   - Configurasi terpusat untuk parameter API

4. **User Experience**
   - Feedback real-time dengan pesan status dan typing indicators
   - Format Markdown untuk tampilan pesan yang superior
   - Kustomisasi caption berdasarkan platform
   - Deteksi otomatis jenis platform dari URL

## 🔧 Peran Teknologi Kunci

### Asynchronous Framework
Implementasi `asyncio` memungkinkan bot menangani banyak permintaan secara bersamaan, membuatnya terasa sangat responsif bahkan saat berhadapan dengan media yang besar.

### Media Enhancer System
Bot ini menggunakan teknik khusus untuk meningkatkan metadata konten, terutama untuk YouTube Music, mengekstrak dan mempresentasikan data seperti judul, artis, jumlah views, dan durasi dalam format yang menarik.

### Smart URL Processor
Sistem deteksi platform dan sanitasi URL yang canggih dengan regular expressions memungkinkan bot untuk memproses berbagai format URL dan varian dari setiap platform.

### User Quota Manager
Sistem pembatasan berbasis waktu memberikan pengalaman yang adil untuk semua pengguna, dengan mekanisme refresh otomatis dan feedback yang informatif tentang status kuota mereka.

## 📜 Penggunaan Perintah

- `/start` - Memulai bot dan melihat informasi selamat datang
- `/help` - Menampilkan informasi penggunaan dan platform yang didukung
- `/quota` - Memeriksa kuota penggunaan harian Anda

## 🔐 Privasi & Keamanan

- Tidak ada penyimpanan data jangka panjang
- Tidak mengumpulkan informasi pribadi pengguna
- Media diproses dan dikirim secara real-time 
- Enkripsi end-to-end via Telegram
- Tidak ada riwayat pencarian yang disimpan

## 🔧 Pengembangan Lokal

```bash
# Clone repository
git clone https://github.com/yourusername/social-media-scraper-pro.git

# Install dependencies
pip install -r requirements.txt

# Configure environment variables (buat file .env dari .env.example)

# BOT_TOKEN=your_token_here
# ITZPIRE_API_URL=
# FACEBOOK_API_URL=
# TIKTOK_API_URL=
# YOUTUBE_API_URL=

# Run the bot
python main.py
```

## 🌟 Kontributor

Dikembangkan oleh MhAminn dengan bantuan dari komunitas open source.

## 📄 Lisensi

Didistribusikan di bawah Lisensi MIT. Lihat `LICENSE` untuk informasi lebih lanjut.


<div align="center">
  <p>Made with ❤️ in Makassar</p>
  <p>© 2025 MhAminn - All Rights Reserved</p>
</div>
