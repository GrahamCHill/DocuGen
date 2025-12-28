
from zealgen.utils.url import get_filename_from_url, normalize_url
from urllib.parse import urljoin

def test_mismatch():
    url1 = "http://lazyfoo.net/tutorials/OpenGL/24_text_alignment/"
    url2 = "http://lazyfoo.net/tutorials/OpenGL/24_text_alignment/index.php"
    
    # Suppose url1 redirects to url2
    
    filename1 = get_filename_from_url(url1)
    filename2 = get_filename_from_url(url2)
    
    print(f"URL1: {url1} -> Filename: {filename1}")
    print(f"URL2: {url2} -> Filename: {filename2}")
    
    if filename1 != filename2:
        print("MISMATCH DETECTED!")
    else:
        print("No mismatch.")

    norm1 = normalize_url(url1)
    norm2 = normalize_url(url2)
    print(f"Norm1: {norm1}")
    print(f"Norm2: {norm2}")
    if norm1 != norm2:
        print("Normalization mismatch too!")

if __name__ == "__main__":
    test_mismatch()
