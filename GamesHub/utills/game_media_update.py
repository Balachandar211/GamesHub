import os
import requests
import time
from django.core.files.base import ContentFile
from django.utils.text import slugify
from Store.models import Game, GamesMedia
import re
from .storage_supabase import upload_file_to_supabase
import mimetypes
from urllib.parse import quote_plus
import os


IGDB_CLIENT_ID = os.getenv("IGDB_CLIENT_ID")
IGDB_ACCESS_TOKEN = os.getenv("IGDB_ACCESS_TOKEN")
IGDB_HEADERS = {
    "Client-ID": IGDB_CLIENT_ID,
    "Authorization": f"Bearer {IGDB_ACCESS_TOKEN}",
}

def download_image(url, game_name, num):
    try:
        r = requests.get("https:" + url, stream=True, timeout=15)
        r.raise_for_status()

        content_type = r.headers.get('Content-Type', '').split(';')[0].strip()
        
        extension = mimetypes.guess_extension(content_type) or '.jpg'
        
        if extension not in ['.jpg', '.jpeg', '.png', '.webp', '.gif']:
            extension = '.jpg'

        filename = f"{game_name}_{num}{extension}"
        return ContentFile(r.content, name=filename) 

    except Exception as e:
        return None

def get_igdb_screenshots(game_name):
    query = f'fields screenshots.url, screenshots.width, screenshots.height; where name ~ *"{game_name}"*; limit 5;'
    resp = requests.post("https://api.igdb.com/v4/games", headers=IGDB_HEADERS, data=query)
    if not resp.ok:
        return []
    data = resp.json()
    if not data:
        return []
    
    urls = []
    for game in data:
        for ss in game.get('screenshots', []):
            if ss.get('width', 0) > ss.get('height', 0):
                urls.append(ss['url'].replace('t_thumb', 't_screenshot_huge'))
                if len(urls) >= 5:
                    return urls
                
    return urls

def get_youtube_trailer(game_name):
    query = f'''
    fields videos.video_id;
    where name ~ *"{game_name}"* & videos.video_id != null;
    limit 1;
    '''
    resp = requests.post("https://api.igdb.com/v4/games", headers=IGDB_HEADERS, data=query)
    if not resp.ok:
        return None
    data = resp.json()
    if not data:
        return None
    video_id = data[0].get("videos", [{}])[0].get("video_id")
    return f"https://www.youtube.com/watch?v={video_id}" if video_id else None

def populate_gamemedia(game):
    logs = {}
    
    game_name = game.get_name()

    logs["game_processed"] = game_name

    added = 0

    trailer_url = get_youtube_trailer(game.name)
    if trailer_url:
        obj, created = GamesMedia.objects.get_or_create(
            game=game,
            media_type=2,
            defaults={"url": trailer_url}
        )

        logs["game_trailer"] = "updated"

        if created:
            logs["game_trailer"] = "added"

    
    screenshot_urls = get_igdb_screenshots(game_name)
    
    for i, img_url in enumerate(screenshot_urls):
        file_content = download_image(img_url, game_name, i)
        safe_path  = re.sub(r'[^a-zA-Z0-9\-_/\.]', '', game_name)
        screenshot = file_content

        if screenshot:
            public_url = upload_file_to_supabase(screenshot, f"{safe_path}/Screen_Shots")
        else:
            continue
    
        GamesMedia(game = game, media_type = 1, url = public_url).save()

        added += 1

    logs["screenshots_added"] = added

    return logs


# def get_cover_url(game_name):
#     query = f'fields cover.url; where name = "{game_name}"; limit 1;'
#     resp = requests.post(
#         "https://api.igdb.com/v4/games",
#         headers=IGDB_HEADERS,
#         data=query
#     )
#     if resp.ok and resp.json():
#         cover = resp.json()[0].get("cover", {})
#         url = cover.get("url", "")
#         if url:
#             url = url.replace("t_thumb", "t_cover_big")
#             return download_image(url, game_name, '')
#     return None

def get_cover_url(game_name):
    query = f'fields cover; where name = "{game_name}"; limit 1;'
    resp = requests.post(
        "https://api.igdb.com/v4/games",
        headers=IGDB_HEADERS,
        data=query
    )
    if not resp.ok or not resp.json():
        return None

    cover_id = resp.json()[0].get("cover")
    if not cover_id:
        return None
    
    cover_query = f'fields url; where id = {cover_id};'
    cover_resp = requests.post(
        "https://api.igdb.com/v4/covers",
        headers=IGDB_HEADERS,
        data=cover_query
    )
    if not cover_resp.ok or not cover_resp.json():
        return None

    url = cover_resp.json()[0].get("url")
    if not url:
        return None

    if "t_thumb" in url:
        url = url.replace("t_thumb", "t_1080p")
    elif "t_cover_big" in url:
        url = url.replace("t_cover_big", "t_1080p")

    return download_image(url, game_name, '')
