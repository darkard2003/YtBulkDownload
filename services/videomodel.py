class Thumbnail:
    def __init__(self, url: str, width: int, height: int):
        self.url: str = url
        self.width: int = width
        self.height: int = height

class YtVideo:
    def __init__(
        self,
        title: str,
        id_: str,
        url: str,
        thumbnail: Thumbnail,
        duration: int,
        uploader: str,
    ):
        self.title: str = title
        self.id_: str = id_
        self.thumbnail: Thumbnail = thumbnail
        self.duration: int = duration
        self.uploader: str = uploader
        self.url: str = url
