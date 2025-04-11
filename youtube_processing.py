from yt_dlp import YoutubeDL
import logging 

logging.basicConfig(level=logging.INFO)

def download_audio(youtube_url):
    """Завантажує аудіо з YouTube URL та конвертує в mp3."""
    output_path = "downloaded_audio.%(ext)s"
    mp3_output_path = "downloaded_audio.mp3" 

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path,     
        'noplaylist': True,         
        'postprocessors': [{
            'key': 'FFmpegExtractAudio', 
            'preferredcodec': 'mp3',    
            'preferredquality': '192',  
        }],
        'quiet': True, 
        'no_warnings': True, 
    }
    try:
        logging.info(f"Завантаження та конвертація аудіо з: {youtube_url}")
        with YoutubeDL(ydl_opts) as ydl:
            error_code = ydl.download([youtube_url])
            if error_code != 0:
                 logging.error(f"yt-dlp повернув помилку {error_code} для URL: {youtube_url}")
                 return None #

        logging.info(f"Аудіо успішно завантажено та конвертовано в {mp3_output_path}")
        return mp3_output_path # 

    except Exception as e:
        logging.error(f"Помилка під час завантаження/конвертації аудіо з {youtube_url}: {e}")
        return None

