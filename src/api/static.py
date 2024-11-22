import os.path

import aiofiles

from falcon import Request, Response
from falcon.errors import HTTPBadRequest, HTTPInternalServerError

from config import APP_STATIC_ROOT
from config import logger

class Static:
    async def on_get(self, req: Request, resp: Response, file_path: str):
        file_path = file_path.strip()
        if not file_path:
            raise HTTPBadRequest
        file_path = str((APP_STATIC_ROOT / file_path).resolve())
        if not file_path.startswith(str(APP_STATIC_ROOT) + os.path.sep):
            raise HTTPBadRequest

        try:
            async with aiofiles.open(file_path, mode='rb') as file:
                content = await file.read()
            if file_path.endswith('.html'):
                content_type = 'text/html'
            elif file_path.endswith('.css'):
                content_type = 'text/css'
            elif file_path.endswith('.js'):
                content_type = 'text/javascript'
            else:
                content_type = 'text/plain'
            resp.content_type = content_type
            resp.data = content
        except:
            logger.error('Read file error: {}', file_path)
            raise HTTPInternalServerError
