import falcon.asgi
import uvicorn

from api.middleware import handle_uncaught_exceptions, SimpleSDCoreAPIMiddleware
from api.info import AppInfo, CreateSDModel
from api.task import CreateTask
from config import HTTP_HOST, HTTP_PORT
from config import logger


def main():
    middleware = SimpleSDCoreAPIMiddleware()

    app = falcon.asgi.App(middleware=[middleware, ])
    app.add_route('/ssdcore/app/info', AppInfo())
    app.add_route('/ssdcore/model/create', CreateSDModel())
    app.add_route('/ssdcore/task/create', CreateTask())
    app.add_error_handler(Exception, handle_uncaught_exceptions)

    logger.info('Application ready.')
    return app


if __name__ == '__main__':
    application = main()
    uvicorn.run(application, host=HTTP_HOST, port=HTTP_PORT, workers=1, loop='asyncio')
