import os
import sys
from transcriber import transcribe_video

# Add local bin directory to PATH
bin_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin")
os.environ["PATH"] += os.pathsep + bin_dir

# Path to the sample video
video_path = os.path.abspath(r"..\11_Bentuk Normal.mp4")

print(f"Testing transcription for: {video_path}")
print(f"Bin dir added to PATH: {bin_dir}")

if not os.path.exists(video_path):
    print("Error: Video file not found at", video_path)
    sys.exit(1)

try:
    result = transcribe_video(video_path)
    print("\nTranscription Success!")
    print("-" * 20)
    text = result.get("text", "")
    print(text[:500] + "..." if len(text) > 500 else text)
    print("-" * 20)
except Exception as e:
    print(f"\nTranscription Failed: {e}")
    import traceback
    traceback.print_exc()
