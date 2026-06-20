from llm_prettified import browse
import requests
def get_photo(id, cover):
    return f"https://img.cityexpert.rs/properties/1280x/{str(id)[:2]}000/{id}/slike/{cover}@avif"

def get_all_photos(id, cover):
    base = str(id)[:2]+'000'
    parts = cover.split('-')
    try:
        num = int(parts[3])
    except (ValueError, IndexError):
        return [f"https://img.cityexpert.rs/properties/1280x/{base}/{id}/slike/{cover}@avif"]
    urls=[]
    for i in range(10):
        name = cover.replace(f'-{cover.split("-")[3]}-', f'-{str(num - i).zfill(5)}-')
        url = f"https://img.cityexpert.rs/properties/1280x/{base}/{id}/slike/{name}@avif"
        resp = requests.head(url)
        if resp.status_code != 200:
            break
        urls.append(url)
    return urls
