import sys
from pathlib import Path

import torch
from loguru import logger
from pytz import timezone

APP_ROOT = Path(__file__).parent.parent.resolve()
APP_DB = APP_ROOT / 'db' / 'core.db'
APP_IMAGES_ROOT = APP_ROOT / 'images'

CFG_TIMEZONE = timezone('Asia/Shanghai')
CFG_DB_ECHO = True

HTTP_HOST = '0.0.0.0'
HTTP_PORT = 23333

logger.remove()
logger.add(sys.stdout, level='INFO')

# CUDA or MPS
if torch.cuda.is_available():
    DEVICE = 'cuda'
elif torch.backends.mps.is_available():
    DEVICE = 'mps'
else:
    DEVICE = 'cpu'
