import regex

import aiofiles
from falcon import Request, Response
from falcon.errors import HTTPBadRequest

from config import APP_IMAGES_ROOT


class Image:
    def __init__(self):
        self.file_dir_pattern = regex.compile(r'^\d{8}$')
        self.file_name_pattern = regex.compile(r'^\d{6}\.\d{3}\.png$')

    async def on_get(self, req: Request, resp: Response, file_dir: str, file_name: str):
        if not self.file_dir_pattern.match(file_dir):
            raise HTTPBadRequest
        if not self.file_name_pattern.match(file_name):
            raise HTTPBadRequest

        file_path = str(APP_IMAGES_ROOT / file_dir / file_name)
        async with aiofiles.open(file_path, mode='rb') as file:
            content = await file.read()
        resp.content_type = 'image/png'
        resp.data = content
