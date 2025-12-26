from urllib.parse import urlparse

def get_filename_from_url(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path
    if not path or path.endswith("/"):
        path += "index.html"
    
    filename = path.split("/")[-1]
    if not filename.endswith(".html"):
        filename += ".html"
    return filename
