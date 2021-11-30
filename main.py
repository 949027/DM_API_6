import os
import random

from dotenv import load_dotenv
import requests


def check_api_error(response):
    if response.get('error'):
        error_code = response['error']['error_code']
        error_msg = response['error']['error_msg']
        raise requests.HTTPError(
            f'VK API ERROR! Code: {error_code}. Message: {error_msg}'
        )


def get_comic(comic_number):
    url = f'https://xkcd.com/{comic_number}/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    comic = response.json()
    image_url = comic['img']
    title = comic['safe_title']
    return image_url, title


def download_image(url, filename):
    response = requests.get(url)
    response.raise_for_status()
    with open(filename, 'wb') as file:
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
    decoded_response = response.json()
    check_api_error(decoded_response)
    upload_url = decoded_response['response']['upload_url']
    return upload_url


def upload_to_server(url, filename):
    with open(filename, 'rb') as file:
        files = {'photo': file}
        response = requests.post(url, files=files)
    response.raise_for_status()
    uploaded_image = response.json()
    check_api_error(uploaded_image)
    image, server, img_hash = \
        uploaded_image['photo'], \
        uploaded_image['server'], \
        uploaded_image['hash']
    return image, server, img_hash


def save_to_server(image, server, hash, token):
    url = 'https://api.vk.com/method/photos.saveWallPhoto'
    payload = {
        'photo': image,
        'server': server,
        'hash': hash,
        'access_token': token,
        'v': '5.131',
    }
    response = requests.post(url, params=payload)
    response.raise_for_status()
    decoded_response = response.json()
    check_api_error(decoded_response)
    saved_image = decoded_response['response'][0]
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
    check_api_error(response.json())


def main():
    load_dotenv()
    token = os.getenv('VK_TOKEN')
    group_id = os.getenv('GROUP_ID')
    filename = 'comic.png'

    try:
        comic_number = get_random_comic_number()
        image_url, title = get_comic(comic_number)
        download_image(image_url, filename)
        upload_url = get_upload_url(token)
        image, server, img_hash = upload_to_server(upload_url, filename)
        media_id, owner_id = save_to_server(image, server, img_hash, token)
        publish_comic(group_id, media_id, owner_id, token, title)
    except requests.HTTPError as error:
        print(error)
    finally:
        os.remove(filename)


if __name__ == '__main__':
    main()
