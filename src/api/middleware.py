from asyncio import current_task
from typing import Any, Optional

from falcon import Request, Response
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine, async_sessionmaker, \
    async_scoped_session

from config import APP_DB, CFG_DB_ECHO
from config import logger


async def handle_uncaught_exceptions(req: Request, resp: Response, exception, params):
    try:
        raise exception
    except:
        logger.exception('未捕获的异常')
    resp.media = {
        'ErrCode': 500,
        'ErrMsg': 'Internal Server Error',
        'Data': {}
    }


class SimpleSDCoreAPIMiddleware:
    def __init__(self):
        self.db_engine: Optional[AsyncEngine] = None
        self.db_session_factory: Optional[async_sessionmaker] = None

    async def process_startup(self, scope: dict[str, Any], event: dict[str, Any]):
        logger.info('Starting database configuration...')
        self.db_engine = create_async_engine(f'sqlite+aiosqlite:///{APP_DB}', pool_recycle=3600, echo=CFG_DB_ECHO)
        self.db_session_factory = async_sessionmaker(self.db_engine, class_=AsyncSession)
        logger.info('Database configuration complete.')

    async def process_shutdown(self, scope: dict[str, Any], event: dict[str, Any]):
        await self.db_engine.dispose()
        logger.info('Database engine closed.')

    async def process_request(self, req: Request, resp: Response):
        try:
            req.context.session = async_scoped_session(self.db_session_factory, scopefunc=current_task)()
            logger.debug('Scoped database session initialized.')
        except Exception:
            logger.exception('Failed to create session.')

    async def process_response(self, req: Request, resp: Response, resource: object, req_succeeded: bool):
        if hasattr(req.context, 'session'):
            await req.context.session.close()
