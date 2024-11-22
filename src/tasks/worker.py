import os
from copy import deepcopy
from multiprocessing import Queue
from random import randint

import torch
from diffusers import DiffusionPipeline, StableDiffusionXLPipeline
from diffusers.schedulers import EulerAncestralDiscreteScheduler, DDIMScheduler, LMSDiscreteScheduler, PNDMScheduler, DPMSolverMultistepScheduler
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import APP_DB, APP_IMAGES_ROOT, DEVICE, CFG_DB_ECHO
from config import logger
from data.db import SDTask
from library.datetime import now


def worker(queue: Queue, model_id: int, model_name: str, model_type: int, model_path: str):
    logger.info('Worker model info: Id={}, Name={}, Type={}, Path={}', model_id, model_name, model_type, model_path)
    
    db_engine = create_engine(f'sqlite:///{APP_DB}', pool_recycle=3600, echo=CFG_DB_ECHO)
    db_session_factory = sessionmaker(bind=db_engine)

    if model_type == 1:
        pipeline = DiffusionPipeline.from_pretrained(
            model_path,
            torch_dtype=torch.float16,
            use_safetensors=True,
        ).to(DEVICE)
    else:
        pipeline = StableDiffusionXLPipeline.from_single_file(
            model_path,
            torch_dtype=torch.float16,
            use_safetensors=True,
        ).to(DEVICE)
    logger.info('Pipeline loaded: {}', model_name)

    scheduler_config = deepcopy(pipeline.scheduler.config)
    schedulers = [
        EulerAncestralDiscreteScheduler,
        DDIMScheduler,
        LMSDiscreteScheduler,
        PNDMScheduler,
        DPMSolverMultistepScheduler,
    ]

    while True:
        task_id = queue.get()
        if task_id is None:
            continue

        logger.info(f'Start task: {task_id}')
        session = db_session_factory()
        task = session.query(SDTask).filter_by(id=task_id).first()
        if not task:
            logger.error('Task not found: {}', task_id)
            continue
        task_scheduler_id = int(task.scheduler)
        task_prompt = str(task.prompt)
        task_negative_prompt = str(task.negative_prompt) or None
        task_width = int(task.width)
        task_height = int(task.height)
        task_steps = int(task.steps)
        task_scale = float(task.scale)
        task_seed = int(task.seed)
        task_size = int(task.size)

        started_at = now()
        task.status = 1
        task.started_at = started_at
        session.add(task)
        session.commit()
        session.close()
        logger.info('Update task status to 1: {}', task_id)

        if task_seed == -1:
            generator = torch.manual_seed(randint(10, 100000))
        else:
            generator = torch.manual_seed(task_seed)
        images = []

        try:
            pipeline.scheduler = schedulers[task_scheduler_id - 1].from_config(scheduler_config)
            for _ in range(task_size):
                res = pipeline(
                    prompt=task_prompt,
                    negative_prompt=task_negative_prompt,
                    height=task_height,
                    width=task_width,
                    num_inference_steps=task_steps,
                    guidance_scale=task_scale,
                    generator=generator,
                    num_images_per_prompt=1,
                    batch_size=1,
                )
                for image in res.images:
                    current_time = now()
                    image_dir = current_time.strftime('%Y%m%d')
                    image_path = current_time.strftime('%H%M%S.%f')[:-3] + '.png'
                    image_db_path = f'{image_dir}/{image_path}'
                    image_save_dir = str(APP_IMAGES_ROOT) + '/' + image_dir
                    os.makedirs(image_save_dir, exist_ok=True)
                    image.save(f'{image_save_dir}/{image_path}')
                    images.append(image_db_path)
                    logger.info('Saved image at {}', image_db_path)
            success = 1
        except:
            success = 0
            logger.exception('Failed to inference images: Id={}', task_id)

        session = db_session_factory()
        new_task = session.query(SDTask).filter_by(id=task_id).first()
        ended_at = now()
        new_task.status = 2
        new_task.ended_at = ended_at
        new_task.duration = (ended_at - started_at).total_seconds() * 1000
        if success:
            new_task.success = 1
            new_task.images = ','.join(images)
        else:
            new_task.success = 0
            new_task.images = ''
        session.add(new_task)
        session.commit()
        logger.info('Task finished: {}', task_id)
