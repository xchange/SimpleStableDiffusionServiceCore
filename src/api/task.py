from pprint import pprint

from falcon import Request, Response
from falcon.errors import HTTPBadRequest, HTTPInternalServerError
from sqlalchemy.future import select

from config import logger
from data.db import SDModel, SDScheduler, SDTask
from library.datetime import now
from library.utils import json_loads, valid_int, valid_float


class CreateTask:
    async def on_post(self, req: Request, resp: Response):
        payload = await req.bounded_stream.read()
        logger.info(f'Request payload: {payload}')
        data = json_loads(payload)
        pprint(data)
        try:
            assert data
            assert isinstance(data, dict)
            assert data.get('model')
            assert data.get('scheduler')
            assert data.get('prompt')
            assert data.get('width')
            assert isinstance(data.get('width'), int)
            assert 128 <= data['width'] <= 3840
            assert data.get('height')
            assert isinstance(data.get('height'), int)
            assert 128 <= data['height'] <= 3840
        except AssertionError:
            logger.error(f'Invalid payload received: {payload}')
            raise HTTPBadRequest

        task = SDTask(prompt=data['prompt'], width=data['width'], height=data['height'])

        # Check model
        q = select(SDModel).filter_by(id=data['model'])
        result = await req.context.session.execute(q)
        record = result.scalars().first()
        if not record:
            logger.error(f'No model found for id: {data["model"]}')
            raise HTTPBadRequest
        task.model = data['model']

        # Check scheduler
        q = select(SDScheduler).filter_by(id=data['scheduler'])
        result = await req.context.session.execute(q)
        record = result.scalars().first()
        if not record:
            logger.error(f'No model found for id: {data["scheduler"]}')
            raise HTTPBadRequest
        task.scheduler = data['scheduler']

        # Check other params
        task.negative_prompt = data.get('negative_prompt', '')
        task.size = valid_int(data.get('size', 1), 1, 1, 50)
        task.steps = valid_int(data.get('steps', 30), 30, 5, 50)
        task.scale = valid_float(data.get('scale', 7.0), 7.0, 1.0, 15.0)
        task.seed = valid_int(data.get('seed', -1), -1, -1, 4294967295)

        # default
        current_time = now()
        task.status = 0
        task.created_at = current_time
        task.duration = -1
        task.success = -1
        task.images = ''

        req.context.session.add(task)
        await req.context.session.commit()

        q = select(SDTask).filter_by(created_at=current_time, status=0)
        result = await req.context.session.execute(q)
        record = result.scalars().first()
        if not record:
            logger.error(f'No task found for request: {current_time}, {payload}')
            raise HTTPInternalServerError
        resp.media = {
            'code': 0,
            'msg': 'OK',
            'data': {
                'task_id': record.id,
            }
        }