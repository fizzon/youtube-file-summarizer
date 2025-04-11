from yt_dlp import YoutubeDL

def download_audio(youtube_url):
    output_path = "audio.%(ext)s"  
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'ffmpeg_location': 'C:/ffmpeg/bin', 
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])

    return "audio.mp3"  
