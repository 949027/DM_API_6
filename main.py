import os
import random

from dotenv import load_dotenv
import requests


def get_comic(comic_number):
    url = f'https://xkcd.com/{comic_number}/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    comic = response.json()
    image_url = comic['img']
    title = comic['safe_title']
    return image_url, title


def download_image(url):
    response = requests.get(url)
    response.raise_for_status()
    with open('comic.png', 'wb') as file:
        file.write(response.content)


def get_random_comic_number():
    url = 'https://xkcd.com/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    comic_amount = response.json()['num']
    random_number = random.randint(1, comic_amount + 1)
    return random_number


def get_upload_url(token):
    url = 'https://api.vk.com/method/photos.getWallUploadServer'
    payload = {'access_token': token, 'v': '5.131'}
    response = requests.get(url, params=payload)
    response.raise_for_status()
    upload_url = response.json()['response']['upload_url']
    return upload_url


def upload_to_server(url):
    with open('comic.png', 'rb') as file:
        files = {'photo': file}
        response = requests.post(url, files=files)
        response.raise_for_status()
        uploaded_image = response.json()
    os.remove('comic.png')
    return uploaded_image


def save_to_server(uploaded_image, token):
    url = 'https://api.vk.com/method/photos.saveWallPhoto'
    payload = {
        'photo': uploaded_image['photo'],
        'server': uploaded_image['server'],
        'hash': uploaded_image['hash'],
        'access_token': token,
        'v': '5.131',
    }
    response = requests.post(url, params=payload)
    response.raise_for_status()
    saved_image = response.json()['response'][0]
    media_id = saved_image['id']
    owner_id = saved_image['owner_id']
    return media_id, owner_id


def publish_comic(group_id, media_id, owner_id, token, title):
    group_id = f'-{group_id}'
    attachments = f'photo{owner_id}_{media_id}'
    url = 'https://api.vk.com/method/wall.post'
    payload = {
        'access_token': token,
        'v': '5.131',
        'from_group': 1,
        'owner_id': group_id,
        'message': title,
        'attachments': attachments,
    }
    response = requests.get(url, params=payload)
    response.raise_for_status()


def main():
    load_dotenv()
    token = os.getenv('VK_TOKEN')
    group_id = os.getenv('GROUP_ID')

    comic_number = get_random_comic_number()
    image_url, title = get_comic(comic_number)
    download_image(image_url)
    upload_url = get_upload_url(token)
    uploaded_image = upload_to_server(upload_url)
    media_id, owner_id = save_to_server(uploaded_image, token)
    publish_comic(group_id, media_id, owner_id, token, title)


if __name__ == '__main__':
    main()
