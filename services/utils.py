import yt_dlp

def download_youtube_audio(audio_id: str, audio_url: str, output_path: str):
    """
    Downloads the audio from a YouTube video.

    Args:
        url (str): The URL of the YouTube video.
        output_path (str): The directory where the audio file will be saved.
    """

    print(f"Downloading audio for video ID: {audio_id}")
    
    ydl_opts = {
        'format': 'bestaudio/best',  # Selects the best audio format
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',  # Converts to MP3
            'preferredquality': '192', # Audio quality
        }],
        'outtmpl': f'{output_path}/{audio_id}.%(ext)s', # Output file name template
        'noplaylist': True, # Download only the specified video, not a playlist
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([audio_url])
        print(f"Audio downloaded successfully from: {audio_url}")
    except Exception as e:
        print(f"Error downloading audio: {e}")