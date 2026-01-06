import whisper
import os

def transcribe_video(video_path: str) -> str:
    """
    Transcribes a video file using OpenAI's Whisper model.
    """
    # Load the model. 
    # 'base' is faster but less accurate. 'medium' or 'large' are better for accuracy but slower.
    # For a 3-hour video, 'base' or 'small' might be a good starting point for speed.
    # We can make this configurable.
    model = whisper.load_model("base")
    
    # Whisper can handle video files directly by extracting audio with ffmpeg
    result = model.transcribe(video_path)
    
    return result["text"]
