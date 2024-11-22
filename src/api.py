import falcon.asgi
import uvicorn
from falcon.routing import PathConverter

from api.middleware import handle_uncaught_exceptions, SimpleSDCoreAPIMiddleware
from api.image import Image
from api.info import AppInfo, CreateSDModel
from api.static import Static
from api.task import CreateTask, CheckTaskStatus, ListTask
from config import HTTP_HOST, HTTP_PORT
from config import logger


def main():
    middleware = SimpleSDCoreAPIMiddleware()

    app = falcon.asgi.App(middleware=[middleware, ])
    app.router_options.converters['path'] = PathConverter

    app.add_route('/ssdscore/app/info', AppInfo())
    app.add_route('/ssdscore/model/create', CreateSDModel())
    app.add_route('/ssdscore/task/create', CreateTask())
    app.add_route('/ssdscore/task/status', CheckTaskStatus())
    app.add_route('/ssdscore/task/list', ListTask())
    app.add_route('/ssdscore/images/{file_dir}/{file_name}', Image())
    app.add_route('/ssdscore/static/{file_path:path}', Static())
    app.add_error_handler(Exception, handle_uncaught_exceptions)

    logger.info('Application ready.')
    return app


if __name__ == '__main__':
    application = main()
    uvicorn.run(application, host=HTTP_HOST, port=HTTP_PORT, workers=1, loop='asyncio')
