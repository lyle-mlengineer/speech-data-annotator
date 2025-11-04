import json
import os
import redis
from utils import download_youtube_audio


from config import config


class AudioDownloadService:
    def __init__(self):
        self._data_dir: str = os.path.join(config.DATA_DIR, "raw")
        self.redis = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB)
    
    def download_audio(self, audio_id: str, audio_url: str) -> None:
        audio_dir: str = os.path.join(self._data_dir, audio_id)
        audio_file_path: str = os.path.join(audio_dir, f"{audio_id}.mp3")
        if not os.path.exists(audio_file_path):
            if not os.path.exists(audio_dir):
                os.makedirs(audio_dir)
            download_youtube_audio(audio_id, audio_url, audio_dir)
    
    def run(self):
        while True:
            try:
                task = self.redis.brpop(config.REDIS_AUDIO_DOWNLOAD_QUEUE, timeout=0)
                if task:
                    data = json.loads(task[1].decode("utf-8"))
                    print(data)
                    # self.download_audio(data["audio_id"], data["audio_url"])
                    self.redis.lpush(config.REDIS_AUDIO_DOWNLOAD_QUEUE, json.dumps({"audio_id": data["audio_id"]}))
            except Exception as e:
                print("exception in audio download service: ", e)
                print(e)
    
if __name__ == "__main__":
    service = AudioDownloadService()
    # service.download_audio(audio_id="m8NQHvLh_eU", audio_url="https://www.youtube.com/watch?v=m8NQHvLh_eU")
    # service.run()