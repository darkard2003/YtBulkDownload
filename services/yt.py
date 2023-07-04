import json
from yt_dlp import YoutubeDL
from .videomodel import Thumbnail, YtVideo
from typing import Callable, Literal


class YoutubeDownloader:
    def __init__(self, ffmpeg_path=None):
        self.ffmepg_path = ffmpeg_path

    def search(self, query: str, limit: int = 10):
        ydl_opts = {
            "format": "bestaudio/best",
            "quiet": True,
            "extract_flat": True,
            "noplaylist": True,
            "limit": 10,
        }
        with YoutubeDL(ydl_opts) as self.ydl:
            info = self.ydl.extract_info(f"ytsearch{limit}:{query}", download=False)
            if info is None:
                return []
            enteris = [e for e in info["entries"] if e.get("duration")]
            videos = []
            for e in enteris:
                title = e["title"]
                id_ = e["id"]
                uploader = e["uploader"]
                duration = e["duration"]
                url = e["url"]
                thumbnail = e["thumbnails"][0]
                thumbnail = Thumbnail(
                    url=thumbnail["url"] if thumbnail["url"] else "Unknown",
                    width=thumbnail["width"] if thumbnail["width"] else 0,
                    height=thumbnail["height"] if thumbnail["height"] else 0,
                ) 
                video = YtVideo(
                    title=title if title else "Unknown",
                    id_=id_ if id_ else "Unknown",
                    url=url if url else "Unknown",
                    thumbnail=thumbnail,
                    duration=duration if duration else 0,
                    uploader=uploader if uploader else "Unknown",
                )
                videos.append(video)

            return videos

    def download(
        self,
        videos: list[YtVideo],
        download_location: str = "downloads",
        format: Literal["mp3", "mp4"] = "mp3",
        progress_hook: Callable[[dict], None] | None = None,
    ):
        video_urls = [v.url for v in videos]
        self.download_audio_url(
            video_urls,
            download_location=download_location,
            progress_hook=progress_hook,
        )

    def download_audio_url(
        self,
        urls: list[str],
        download_location: str = "downloads",
        progress_hook=None,
    ):
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": f"{download_location}/%(title)s.%(ext)s",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
            "ffmpeg_location": self.ffmepg_path if self.ffmepg_path else "ffmpeg",
            "progress_hooks": [progress_hook] if progress_hook else None,
            "quiet": True,
        }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download(urls)

    def download_video_url(
        self,
        urls: list[str],
        download_location: str = "downloads",
        progress_hook=None,
    ):
        ydl_opts = {
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "outtmpl": f"{download_location}/%(title)s.%(ext)s",
            "ffmpeg_location": self.ffmepg_path,
            "progress_hooks": [progress_hook] if progress_hook else None,
            "quiet": True,
        }
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download(urls)
