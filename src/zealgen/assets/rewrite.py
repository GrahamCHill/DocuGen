from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import httpx
import pathlib
import hashlib


async def rewrite_assets(html, base_url, out_dir):
    soup = BeautifulSoup(html, "lxml")

    async with httpx.AsyncClient(follow_redirects=True) as client:
        for tag, attr in [("link", "href"), ("script", "src")]:
            for el in soup.find_all(tag):
                if not el.get(attr):
                    continue

                url = urljoin(base_url, el[attr])
                if not url.startswith("http"):
                    continue

                try:
                    data = (await client.get(url)).content
                    fname = pathlib.Path(url).name
                    # Avoid empty filenames or weird ones
                    if not fname:
                         fname = "asset_" + hashlib.md5(url.encode()).hexdigest()[:8]
                    
                    path = out_dir / fname
                    path.write_bytes(data)

                    el[attr] = fname
                except Exception as e:
                    print(f"Failed to download asset {url}: {e}")

    return str(soup)

def get_favicon_url(html, base_url):
    soup = BeautifulSoup(html, "lxml")
    # Look for common favicon patterns
    icon_link = soup.find("link", rel=lambda x: x and "icon" in x.lower())
    if icon_link and icon_link.get("href"):
        return urljoin(base_url, icon_link["href"])
    
    # Fallback to /favicon.ico on the same domain
    parsed = urlparse(base_url)
    return f"{parsed.scheme}://{parsed.netloc}/favicon.ico"
