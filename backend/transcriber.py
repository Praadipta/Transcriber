import os
import re
import subprocess
import tempfile
from typing import Any, Dict, List, Tuple


def _get_ffmpeg_path() -> str:
    """Get ffmpeg path, preferring imageio-ffmpeg's bundled binary."""
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        return "ffmpeg"


def _extract_audio(video_path: str, output_path: str) -> None:
    """Extract audio from video file as mp3 at 64kbps."""
    ffmpeg = _get_ffmpeg_path()
    subprocess.run(
        [ffmpeg, "-i", video_path, "-vn", "-acodec", "libmp3lame",
         "-b:a", "64k", "-y", output_path],
        check=True, capture_output=True,
    )


def _get_audio_duration(audio_path: str) -> float:
    """Get audio duration in seconds using ffmpeg."""
    ffmpeg = _get_ffmpeg_path()
    result = subprocess.run(
        [ffmpeg, "-i", audio_path, "-f", "null", "-"],
        capture_output=True, text=True,
    )
    match = re.search(r"Duration:\s*(\d+):(\d+):(\d+)\.(\d+)", result.stderr)
    if not match:
        return 0.0
    h, m, s, cs = match.groups()
    return int(h) * 3600 + int(m) * 60 + int(s) + int(cs) / 100


def _split_audio(audio_path: str, tmpdir: str, chunk_secs: int = 600) -> List[Tuple[str, float]]:
    """Split audio into chunks of chunk_secs seconds. Returns (path, offset) pairs."""
    duration = _get_audio_duration(audio_path)
    if duration == 0:
        return [(audio_path, 0.0)]

    ffmpeg = _get_ffmpeg_path()
    chunks: List[Tuple[str, float]] = []
    offset = 0.0
    idx = 0
    while offset < duration:
        chunk_path = os.path.join(tmpdir, f"chunk_{idx}.mp3")
        subprocess.run(
            [ffmpeg, "-i", audio_path, "-ss", str(offset), "-t", str(chunk_secs),
             "-acodec", "libmp3lame", "-b:a", "64k", "-y", chunk_path],
            check=True, capture_output=True,
        )
        chunks.append((chunk_path, offset))
        offset += chunk_secs
        idx += 1
    return chunks


def _transcribe_single(client: Any, audio_path: str) -> Dict[str, Any]:
    """Transcribe a single audio file via Groq API."""
    with open(audio_path, "rb") as f:
        response = client.audio.transcriptions.create(
            file=(os.path.basename(audio_path), f),
            model="whisper-large-v3",
            response_format="verbose_json",
        )

    segments = []
    for seg in (getattr(response, "segments", []) or []):
        if isinstance(seg, dict):
            segments.append({
                "start": seg.get("start", 0),
                "end": seg.get("end", 0),
                "text": seg.get("text", ""),
            })
        else:
            segments.append({
                "start": getattr(seg, "start", 0),
                "end": getattr(seg, "end", 0),
                "text": getattr(seg, "text", ""),
            })

    return {
        "text": response.text,
        "segments": segments,
        "language": getattr(response, "language", None),
    }


def transcribe_video(video_path: str) -> Dict[str, Any]:
    """
    Transcribes a video file using Groq's Whisper API.
    Extracts audio, handles large files by chunking, and returns
    the same structure as before: text, segments, and language.
    """
    from groq import Groq

    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    max_size = 24 * 1024 * 1024  # 24MB safety margin under Groq's 25MB limit

    with tempfile.TemporaryDirectory() as tmpdir:
        audio_path = os.path.join(tmpdir, "audio.mp3")
        _extract_audio(video_path, audio_path)

        # Small enough for a single API call
        if os.path.getsize(audio_path) <= max_size:
            return _transcribe_single(client, audio_path)

        # Large file: split into 10-min chunks, transcribe each, merge
        chunks = _split_audio(audio_path, tmpdir)
        all_text: List[str] = []
        all_segments: List[Dict[str, Any]] = []
        language = None

        for chunk_path, offset in chunks:
            result = _transcribe_single(client, chunk_path)
            all_text.append(result["text"])
            if not language:
                language = result.get("language")
            for seg in result["segments"]:
                all_segments.append({
                    "start": seg["start"] + offset,
                    "end": seg["end"] + offset,
                    "text": seg["text"],
                })

        return {
            "text": " ".join(all_text),
            "segments": all_segments,
            "language": language,
        }
