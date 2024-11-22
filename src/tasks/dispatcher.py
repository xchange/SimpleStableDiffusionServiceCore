import time
from multiprocessing import Process, Queue

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import APP_DB
from config import logger
from data.db import SDModel, SDTask
from tasks.worker import worker


def fetch_models(session_factory: sessionmaker):
    session = session_factory()
    records = session.query(SDModel).filter_by(valid=1).all()
    models = {}
    for record in records:
        record_id = int(record.id)
        models[record_id] = {
            'id': record_id,
            'name': str(record.name),
            'model_type': int(record.model_type),
            'path': str(record.path),
        }
    session.close()
    return models


def fetch_tasks(session_factory: sessionmaker):
    session = session_factory()
    records = session.query(SDTask).filter_by(status=0).order_by(SDTask.created_at.asc()).all()
    tasks = []
    for record in records:
        tasks.append({
            'id': int(record.id),
            'model_id': int(record.model),
        })
    session.close()
    return tasks


def dispatch():
    logger.info('Loading database {} ...', APP_DB)
    db_engine = create_engine(f'sqlite:///{APP_DB}', pool_recycle=3600, echo=False)
    db_session_factory = sessionmaker(bind=db_engine)
    logger.info('Loading database successfully.')

    queues = {}
    processes = {}
    dispatched_tasks = {}

    while True:
        _start_ts = time.time()

        models = fetch_models(db_session_factory)
        tasks = fetch_tasks(db_session_factory)

        for item in tasks:
            task_id = item['id']
            model_id = item['model_id']
            model = models[model_id]
            if task_id in dispatched_tasks:
                continue
            if model_id not in processes:
                logger.info('New model process required: Id={}, Name={}, Type={}', model_id, model['name'], model['model_type'])
                queues[model_id] = Queue()
                processes[model_id] = Process(target=worker, args=(queues[model_id], model_id, model['name'], model['model_type'], model['path']))
                processes[model_id].start()
                logger.info('New model process started.')
            queues[model_id].put(task_id)
            dispatched_tasks[task_id] = model_id
        time.sleep(2)
