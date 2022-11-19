from linguee_api.downloaders.interfaces import IDownloader

MESSAGE = "Hello world!"


class MockDownloader(IDownloader):
    """
    A downloader that always return "Hello world!".

    Helpful to test the cache layer.
    """

    def __init__(self, message: str = MESSAGE):
        self.message = message

    async def download(self, url: str) -> str:
        return self.message
