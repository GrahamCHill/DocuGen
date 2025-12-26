import os
import shutil
import plistlib
import httpx
from .index import DocsetIndex
from ..utils.url import get_filename_from_url

class DocsetBuilder:
    def __init__(self, output_path):
        self.docset_name = os.path.basename(output_path).replace(".docset", "")
        self.base_path = output_path
        self.contents_path = os.path.join(self.base_path, "Contents")
        self.resources_path = os.path.join(self.contents_path, "Resources")
        self.documents_path = os.path.join(self.resources_path, "Documents")
        
        self.index = DocsetIndex(os.path.join(self.resources_path, "docSet.dsidx"))
        self._setup_directories()
        self.first_page = None
        self.has_icon = False

    def _setup_directories(self):
        if os.path.exists(self.base_path):
            shutil.rmtree(self.base_path)
        os.makedirs(self.documents_path)
        self.index.connect()

    async def set_icon(self, icon_url):
        if self.has_icon:
            return
        
        try:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                r = await client.get(icon_url)
                if r.status_code == 200:
                    icon_path = os.path.join(self.base_path, "icon.png")
                    with open(icon_path, "wb") as f:
                        f.write(r.content)
                    self.has_icon = True
        except Exception as e:
            print(f"Failed to set icon: {e}")

    def add_page(self, parsed_page, url):
        filename = get_filename_from_url(url)
        if not self.first_page:
            self.first_page = filename
            
        dest_path = os.path.join(self.documents_path, filename)
        with open(dest_path, "w", encoding="utf-8") as f:
            f.write(parsed_page.content)

        for name, type_, anchor in parsed_page.symbols:
            path = f"{filename}#{anchor}" if anchor else filename
            self.index.add_entry(name, type_, path)

    def finalize(self):
        self._write_info_plist()
        self.index.close()

    def _write_info_plist(self):
        index_file = "index.html"
        if not os.path.exists(os.path.join(self.documents_path, index_file)):
            index_file = self.first_page or "index.html"

        info = {
            "CFBundleIdentifier": self.docset_name.lower(),
            "CFBundleName": self.docset_name,
            "DocSetPlatformFamily": self.docset_name.lower(),
            "isDashDocset": True,
            "dashIndexFilePath": index_file,
        }
        with open(os.path.join(self.contents_path, "Info.plist"), "wb") as f:
            plistlib.dump(info, f)
