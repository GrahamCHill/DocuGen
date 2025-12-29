import anyio
import os
from zealgen.core import generate

async def test():
    urls = ["https://wiki.libsdl.org/SDL3/FrontPage"]
    output = "docTest/SDL3.docset"
    if not os.path.exists("docTest"):
        os.makedirs("docTest")
    
    # We use a larger max_pages to try to catch the cross-domain crawl
    await generate(urls, output, js=False, max_pages=100)

if __name__ == "__main__":
    anyio.run(test)
