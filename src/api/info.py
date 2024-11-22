from pathlib import Path

from falcon import Request, Response
from falcon.errors import HTTPBadRequest
from sqlalchemy.future import select

from config import logger
from data.db import SDModel, SDScheduler
from library.datetime import date_format, now
from library.utils import json_loads


class AppInfo:
    async def on_get(self, req: Request, resp: Response):
        models = []
        q = select(SDModel).filter_by(valid=1).order_by(SDModel.created_at.desc())
        result = await req.context.session.execute(q)
        records = result.scalars().all()
        for record in records:
            models.append({
                'id': record.id,
                'name': record.name,
                'description': record.description,
                'created_at': date_format(record.created_at),
                'updated_at': date_format(record.created_at),
            })

        schedulers = []
        q = select(SDScheduler).filter_by(valid=1).order_by(SDScheduler.id.asc())
        result = await req.context.session.execute(q)
        records = result.scalars().all()
        for record in records:
            schedulers.append({
                'id': record.id,
                'name': record.name,
            })
        resp.media = {
            'code': 0,
            'msg': 'OK',
            'data': {
                'models': models,
                'schedulers': schedulers,
            }
        }


class CreateSDModel:
    async def on_post(self, req: Request, resp: Response):
        payload = await req.bounded_stream.read()
        logger.info(f'Request payload: {payload}')
        data = json_loads(payload)
        try:
            assert data
            assert isinstance(data, dict)
            assert data.get('name')
            assert data.get('model_type')
            assert data.get('path')
        except AssertionError:
            logger.error(f'Invalid payload received: {payload}')
            raise HTTPBadRequest

        q = select(SDModel).filter_by(name=data['name'])
        result = await req.context.session.execute(q)
        records = result.scalars().all()
        if records:
            logger.error('Stable Diffusion model already exists: {}', data['name'])
            raise HTTPBadRequest

        if data['model_type'] not in (1, 2):
            logger.error('Invalid model type: {}', data['model_type'])
            raise HTTPBadRequest

        path = Path(data['path']).resolve()
        if not path.exists():
            logger.error('Invalid model path: {}', data['path'])
            raise HTTPBadRequest

        if (path.is_dir() and data['model_type'] != 1) or (path.is_file() and data['model_type'] != 2):
            logger.error('Invalid model type: {}', data['model_type'])
            raise HTTPBadRequest

        current_time = now()
        model = SDModel(
            name=data['name'],
            model_type=data['model_type'],
            path=str(path),
            description=data.get('description'),
            valid=1,
            created_at=current_time,
            updated_at=current_time,
        )
        req.context.session.add(model)
        await req.context.session.commit()

        q = select(SDModel).filter_by(name=data['name'])
        result = await req.context.session.execute(q)
        records = result.scalars().all()
        model = records[0]
        logger.info('Created new SDModel: Id={}, Name={}, Path={}', model.id, model.name, model.path)

        resp.media = {
            'code': 0,
            'msg': 'OK',
            'data': {
                'id': model.id,
            }
        }
