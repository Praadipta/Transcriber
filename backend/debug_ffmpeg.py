import os
import sys
import subprocess
import imageio_ffmpeg

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
ffmpeg_dir = os.path.dirname(ffmpeg_exe)

print(f"FFmpeg exe: {ffmpeg_exe}")
print(f"FFmpeg dir: {ffmpeg_dir}")

# Update PATH
os.environ["PATH"] += os.pathsep + ffmpeg_dir

print("Current PATH includes ffmpeg dir:", ffmpeg_dir in os.environ["PATH"])

# Try running ffmpeg directly
try:
    print("\nAttempting to run ffmpeg -version...")
    subprocess.run(["ffmpeg", "-version"], check=True, capture_output=True)
    print("Success: ffmpeg found and ran.")
except FileNotFoundError:
    print("Error: ffmpeg command not found in subprocess.")
except Exception as e:
    print(f"Error running ffmpeg: {e}")

# Try running with full path
try:
    print(f"\nAttempting to run {ffmpeg_exe} -version...")
    subprocess.run([ffmpeg_exe, "-version"], check=True, capture_output=True)
    print("Success: ffmpeg executable ran with full path.")
except Exception as e:
    print(f"Error running ffmpeg with full path: {e}")

# Check video file
video_path = os.path.abspath(r"..\11_Bentuk Normal.mp4")
print(f"\nVideo path: {video_path}")
if os.path.exists(video_path):
    print("Video file exists.")
else:
    print("Video file DOES NOT exist.")

# Try whisper if ffmpeg works
if "ffmpeg found and ran" in sys.stdout.getvalue() if hasattr(sys.stdout, "getvalue") else True:
    print("\nTrying Whisper...")
    try:
        import whisper
        model = whisper.load_model("base")
        # Whisper might need explicit ffmpeg setup if it doesn't pick up PATH immediately? 
        # Actually it just calls "ffmpeg" so PATH should work.
        result = model.transcribe(video_path)
        print("Whisper success!")
    except Exception as e:
        print(f"Whisper failed: {e}")
