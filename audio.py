import yt_dlp

def parse_video_id(url: str) -> str:
    video_id: str
    try:
        video_id: str = url.split("=")[1].split("&")[0]
    except IndexError:
        video_id = url
    return video_id

def download_youtube_audio(url, output_path='.'):
    """
    Downloads the audio from a YouTube video.

    Args:
        url (str): The URL of the YouTube video.
        output_path (str): The directory where the audio file will be saved.
    """
    
    video_id: str = parse_video_id(url)
    print(f"Downloading audio for video ID: {video_id}")
    
    ydl_opts = {
        'format': 'bestaudio/best',  # Selects the best audio format
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',  # Converts to MP3
            'preferredquality': '192', # Audio quality
        }],
        'outtmpl': f'{output_path}/{video_id}.%(ext)s', # Output file name template
        'noplaylist': True, # Download only the specified video, not a playlist
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print(f"Audio downloaded successfully from: {url}")
    except Exception as e:
        print(f"Error downloading audio: {e}")

if __name__ == "__main__":
    youtube_url = "YOUR_YOUTUBE_VIDEO_URL_HERE" # Replace with your YouTube URL
    youtube_url = "https://www.youtube.com/watch?v=IAdc4QebyYA"
    download_youtube_audio(youtube_url)