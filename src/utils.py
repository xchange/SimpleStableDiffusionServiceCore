import os

from huggingface_hub import snapshot_download

from config import HF_HUB_ENDPOINT, MODEL_PATH
from config import logger

def download_model(repo: str) -> str:
    target_dir = f'{MODEL_PATH}/{repo}'
    os.makedirs(target_dir, exist_ok=True)
    logger.info('Start downloading model: {}', repo)
    snapshot = snapshot_download(repo, local_dir=target_dir, endpoint=HF_HUB_ENDPOINT)
    logger.info('Model saved to: {}', snapshot)
    return snapshot
