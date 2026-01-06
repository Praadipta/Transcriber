import os
import shutil
import imageio_ffmpeg

# Get the source executable
source_ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
print(f"Found ffmpeg at: {source_ffmpeg}")

# Create a local bin directory
bin_dir = os.path.abspath("bin")
os.makedirs(bin_dir, exist_ok=True)

# Target path
target_ffmpeg = os.path.join(bin_dir, "ffmpeg.exe")

# Copy and rename
print(f"Copying to: {target_ffmpeg}")
shutil.copy2(source_ffmpeg, target_ffmpeg)

print("Done. You can now add this bin directory to PATH.")
