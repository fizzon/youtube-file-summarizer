from yt_dlp import YoutubeDL

# Завантаження аудіо з YouTube
def download_audio(youtube_url):
    output_path = "audio.%(ext)s"  # Це дозволить yt_dlp самостійно визначити формат
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'ffmpeg_location': 'C:/ffmpeg/bin',  # якщо потрібно явно вказати
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])

    return "audio.mp3"  # Після конвертації воно буде мати саме таку назву
