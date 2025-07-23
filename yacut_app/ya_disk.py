import aiohttp

API_HOST = 'https://cloud-api.yandex.net/'
API_VERSION = 'v1'
REQUEST_UPLOAD_URL = f'{API_HOST}{API_VERSION}/disk/resources/upload'
DOWNLOAD_LINK_URL = f'{API_HOST}{API_VERSION}/disk/resources/download'


async def upload_file_to_yadisk(file_storage, disk_token, filename):
    headers = {'Authorization': f'OAuth {disk_token}'}
    path = f'app:/{filename}'
    params = {'path': path, 'overwrite': 'true'}

    async with aiohttp.ClientSession() as session:
        async with session.get(
            REQUEST_UPLOAD_URL, headers=headers, params=params
        ) as resp:
            resp_json = await resp.json()
            upload_url = resp_json.get('href')
            if not upload_url:
                raise Exception(
                    f"Ошибка получения ссылки для загрузки: {resp.status}"
                )

        data = file_storage.read()
        async with session.put(upload_url, data=data) as resp:
            if resp.status >= 400:
                raise Exception(f"Ошибка загрузки файла: {resp.status}")

        async with session.get(
            DOWNLOAD_LINK_URL, headers=headers, params={'path': path}
        ) as resp:
            if resp.status >= 400:
                raise Exception(
                    f"Ошибка получения ссылки для скачивания: {resp.status}"
                )
            download_link = (await resp.json()).get('href')

    return download_link
