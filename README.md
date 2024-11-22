# Simple Stable Diffusion Service Core

我啥也不懂，写着玩的。

基于 Python 3.12 开发。

Windows 下不要直接用 requirements.txt，得先

    pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

然后

    pip3 install safetensors diffusers transformers accelerate sqlalchemy aiosqlite falcon uvicorn loguru better_exceptions ujson pytz

就会装好依赖。

然后在 db 目录下新建一个空白文件 core.db 作为 SQLite 数据库的存储文件。

初始化数据：

    python3 init.py

API 启动：

    python3 api.py

真正生成图片的打工人：

    python task.py

-- EOF --