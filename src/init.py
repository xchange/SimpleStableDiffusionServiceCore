from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import APP_DB
from config import logger
from data.db import Base, SDScheduler
from library.datetime import now


def main():
    engine = create_engine(f'sqlite:///{APP_DB}', echo=True)
    Base.metadata.create_all(bind=engine)
    logger.info('创建数据表成功')

    schedulers = [
        'EulerAncestral',
        'DDIM',
        'LMSDiscrete',
        'PNDM',
        'DPMSolver',
    ]

    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    for scheduler in schedulers:
        current_time = now()
        record = SDScheduler(name=scheduler, valid=1, created_at=current_time, updated_at=current_time)
        session.add(record)
        session.commit()
        logger.info('添加调度器记录成功: {}', record)


if __name__ == '__main__':
    main()
