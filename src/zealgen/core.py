import anyio
import pathlib
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from .fetch.httpx_fetcher import HttpxFetcher
from .fetch.playwright_fetcher import PlaywrightFetcher
from .parsers import sphinx, docusaurus, rustdoc, generic
from .docset.builder import DocsetBuilder
from .assets.rewrite import rewrite_assets, get_favicon_url

from .utils.url import get_filename_from_url

PARSERS = [
    sphinx.SphinxParser(),
    docusaurus.DocusaurusParser(),
    rustdoc.RustdocParser(),
    generic.GenericParser(),
]

async def generate(urls, output, js=False, max_pages=100, progress_callback=None):
    fetcher = PlaywrightFetcher() if js else HttpxFetcher()
    builder = DocsetBuilder(output)
    doc_dir = pathlib.Path(builder.documents_path)
    
    visited = set()
    queue = list(urls)
    pages_count = 0

    while queue and pages_count < max_pages:
        url = queue.pop(0)
        if url in visited:
            continue
        visited.add(url)
        
        if progress_callback:
            progress_callback(pages_count, max_pages)
        
        try:
            result = await fetcher.fetch(url)
        except Exception as e:
            print(f"Failed to fetch {url}: {e}")
            continue

        if not builder.has_icon:
            favicon_url = get_favicon_url(result.html, url)
            await builder.set_icon(favicon_url)

        for parser in PARSERS:
            if parser.matches(result.html):
                # Rewrite assets to be local
                html = await rewrite_assets(result.html, url, doc_dir)
                
                # Link discovery and rewriting
                soup = BeautifulSoup(html, "lxml")
                base_parsed = urlparse(url)
                for a in soup.find_all("a", href=True):
                    raw_href = a["href"]
                    next_url = urljoin(url, raw_href)
                    clean_url = next_url.split("#")[0]
                    anchor = next_url.split("#")[1] if "#" in next_url else None
                    
                    next_parsed = urlparse(clean_url)
                    
                    # Stay within same domain and same path prefix (basic heuristic)
                    if next_parsed.netloc == base_parsed.netloc and \
                       next_parsed.path.startswith(base_parsed.path.rsplit('/', 1)[0]):
                        
                        local_name = get_filename_from_url(clean_url)
                        a["href"] = f"{local_name}#{anchor}" if anchor else local_name
                        
                        if clean_url not in visited and clean_url not in queue:
                            queue.append(clean_url)
                
                html = str(soup)
                parsed = parser.parse(html)
                builder.add_page(parsed, url)
                pages_count += 1
                break

    if progress_callback:
        progress_callback(pages_count, max_pages)

    builder.finalize()
