import time
import logging

from vk_request import vk_request

logger_API = logging.getLogger("logs/API_methods.log")
logger_API.setLevel(logging.INFO)

handler_API = logging.FileHandler("logs/API_methods.log", mode='w')
formatter_API = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")

handler_API.setFormatter(formatter_API)
logger_API.addHandler(handler_API)


## 1ый запрос к АПИ - метод videos.get - получает общую информацию о всех видео из сообщества
def get_all_videos(group_id):
    logger_API.info("ФУНКЦИЯ GET_ALL_VIDEOS!!!")
    count = 100
    offset = 0
    videos = []
    while True:
        params = {
            "owner_id": group_id,
            "count"   : count,
            "offset"  : offset,
            "extended": 1,
        }
        try:
            data = vk_request("video.get", params)
        except Exception as err:
            logger_API.error(f"Ошибка при обращении к АПИ у {group_id}: {err}")

        items = []
        try:
            items = data.get("items", [])
            if not items:
                break
        except AttributeError as err:
            logger_API.warning(f"Пустой ответ на запрос видео из сообщества {group_id}")

        videos.extend(items)
        offset += count

        try:
            if offset >= data.get("count", 0):
                break
        except AttributeError as err:
            logger_API.warning(f"Пустой ответ на запрос видео из сообщества {group_id}")

        time.sleep(0.5)
    return videos


## 2ой запрос к АПИ - метод video.getAlbums - получает ID альбомов сообщества, 
# а потом с помощью предыдущего метода получает количество уникальных видео, которые распределили по альбомам
def get_unique_album_videos(group_id):
    logger_API.info("ФУНКЦИЯ GET_UNIQUE_ALBUM_VIDEOS!!!")
    count = 100
    params = {
        "owner_id": group_id,
        "count"   : count, 
        "extended": 1,
    }
    try:
        data = vk_request("video.getAlbums", params)
    except Exception as err:
        logger_API.error(f"Ошибка при обращении к АПИ у {group_id}: {err}")

    albums = []
    try:
        albums = data.get("items", [])
    except Exception as err:
        logger_API.warning(f"Пустой ответ на запрос альбомов из сообщества {group_id}")

    unique_video = set() 

    for album in albums:
        album_id = album["id"]
        count = 100
        offset = 0

        while True:
            video_params = {
                "owner_id": group_id,
                "album_id": album_id,
                "count"   : count,
                "offset"  : offset,
                "extended": 1,
            }
            try:
                data = vk_request("video.get", video_params)
            except Exception as err:
                logger_API.error(f"Ошибка при обращении к АПИ у {group_id}: {err}")

            items = []
            try:
                items = data.get("items", [])
                if not items:
                    break
            except AttributeError as err:
                logger_API.warning(f"Пустой ответ на запрос видео из альбома из сообщества {group_id}")

            for video in items:
                unique_video.add(video["id"])

            offset += count

            try:
                if offset >= data.get("count", 0):
                    break
            except AttributeError as err:
                logger_API.warning(f"Пустой ответ на запрос видео из альбома из сообщества {group_id}")
            
        time.sleep(0.5)

    return len(unique_video)


## 3ий запрос к АПИ - метод groups.getById - получаем информацию про сообщества
def get_group_info(group_ids, optional_fields):
    logger_API.info("ФУНКЦИЯ GET_GROUP_INFO!!!")
    params = {
        "group_ids": group_ids,
        "fields"   : optional_fields,
    }

    try:
        data = vk_request("groups.getById", params)
    except Exception as err:
        logger_API.error(f"Ошибка: {err}")
        return None
    
    return data


## 4ый запрос к АПИ - метод wall.get - получаем инфу про стену сообщетва
def get_wall_info(owner_id, domain):
    logger_API.info("ФУНКЦИЯ GET_WALL_INFO!!!")
    count = 100
    posts = []
    params = {
        "owner_id": owner_id,
        "count"   : count,
        "domain"  : domain,
    }
    try:
        data = vk_request("wall.get", params)
    except Exception as err:
        logger_API.error(f"Ошибка при обращении к АПИ у {domain}: {err}")

    try: 
        posts = data.get("items", [])
        for post, reactions in zip(posts, data.get("reaction_sets")):
            post["reactions"] = reactions["items"]
            posts.append(post)
    except AttributeError as err:
        logger_API.warning(f"Пустой ответ на запрос постов из сообщества {owner_id}")

    return posts


## 5ый запрос к АПИ - метод video.getComments - получим по одному последнему комментариб на видео
def get_video_comment(batch, df):
    logger_API.info("ФУНКЦИЯ GET_VIDEO_COMMENT!!!")
    video_data = []

    for _, row in batch.iterrows():
        video_data.append({
            "owner_id": row["owner_id"],
            "video_id": row["id"]
        })

    execute_code = "return ["
    for video in video_data:
        execute_code += f'API.video.getComments({{"owner_id": {video["owner_id"]}, "video_id": {video["video_id"]}, "count": 1, "sort": "desc"}}),'
    execute_code = execute_code.rstrip(',') + "];"
    try:
        response = vk_request("execute", {"code": execute_code})
    except Exception as err:
        logger_API.error(f"Ошибка при вызове метода execute: {err}")

    if response:
        for i, video in enumerate(batch.iterrows()):
            index = video[0]
            data = response[i]

            if data and "items" in data and len(data["items"]) > 0:
                df.at[index, "top_comment_text"] = data["items"][0].get("text", "")
            else:
                video_name = df.at[index, "title"]
                logger_API.info(f"Проблема с комментариями к видео {video_name}")
                
        logger_API.info(f"Успешно получили комментарии для {len(batch)} видео")

    time.sleep(0.5)