import json
import os
import redis
from utils import download_youtube_audio
from pydub import AudioSegment
import librosa
import soundfile as sf


from config import config


class AudioSliceService:
    def __init__(self, max_duration: int = 30, min_duration: int = 10):
        self._data_dir: str = os.path.join(config.DATA_DIR, "raw")
        self.max_duration = max_duration
        self.min_duration = min_duration
    
    def slice_audio(self, audio_id: str):
        audio_dir: str = os.path.join(self._data_dir, audio_id)
        audio_file_path: str = os.path.join(audio_dir, f"{audio_id}.mp3")
        audio , sr = librosa.load(audio_file_path)
        if len(audio.shape) > 1:
            audio = audio.mean(axis=0)
        for start_idx in range(0, len(audio), self.max_duration * sr):
            end_idx = start_idx + self.max_duration * sr
            audio_segment = audio[start_idx:end_idx]
            if len(audio_segment) < self.min_duration * sr:
                continue
            sf.write(os.path.join(audio_dir, f"{audio_id}_{start_idx}.wav"), audio_segment, sr)
    
    def run(self):
        try:
            r = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB)
            while True:
                task = r.brpop(config.REDIS_AUDIO_SLICE_QUEUE, timeout=0)
                if task:
                    data = json.loads(task[1].decode("utf-8"))
                    print(data)
                    audio_id = data["audio_id"]
                    self.slice_audio(audio_id)
                    data: dict = {
                        "audio_id": audio_id
                    }
                    r.lpush(config.REDIS_AUDIO_UPLOAD_QUEUE, json.dumps(data))
        except Exception as e:
            print(e)
    
if __name__ == "__main__":
    service = AudioSliceService()
    service.run()