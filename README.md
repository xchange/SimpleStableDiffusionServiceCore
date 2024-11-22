# Simple Stable Diffusion Service Core

我啥也不懂，写着玩的。

基于 Python 3.12 开发。

Windows 下不要直接用 requirements.txt，得先

    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

然后

    pip install safetensors diffusers transformers accelerate sqlalchemy aiosqlite falcon uvicorn loguru better_exceptions ujson pytz

就会装好依赖。