from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class SDModel(Base):
    __tablename__ = 't_sd_models'

    id = Column(Integer, autoincrement=True, primary_key=True)      # 主键
    name = Column(String(100), unique=True, nullable=False)         # 模型名称, 唯一索引
    model_type = Column(Integer, nullable=False)                    # 模型类型: 1-完整的模型, 2-只有检查点文件
    path = Column(String(1000), nullable=False)                     # 模型存储位置
    description = Column(String(1000), nullable=False)              # 模型说明
    valid = Column(Integer, default=1, nullable=False)              # 是否有效: 0-无效, 1-有效
    created_at = Column(DateTime(timezone=True), nullable=False)    # 记录创建时间
    updated_at = Column(DateTime(timezone=True), nullable=False)    # 记录更新时间


class SDScheduler(Base):
    __tablename__ = 't_sd_schedulers'

    id = Column(Integer, autoincrement=True, primary_key=True)      # 主键
    name = Column(String(100), unique=True, nullable=False)         # 调度器名称
    valid = Column(Integer, default=1, nullable=False)              # 是否有效: 0-无效, 1-有效
    created_at = Column(DateTime(timezone=True), nullable=False)    # 记录创建时间
    updated_at = Column(DateTime(timezone=True), nullable=False)    # 记录更新时间


class SDTask(Base):
    __tablename__ = 't_sd_tasks'

    id = Column(Integer, autoincrement=True, primary_key=True)      # 主键
    model = Column(Integer, nullable=False)                         # 使用模型的id
    scheduler = Column(Integer, nullable=False)                     # 使用调度器的id
    prompt = Column(String(1000), nullable=False)                   # 提示词
    negative_prompt = Column(String(1000), nullable=False)          # 反向提示词
    width = Column(Integer, nullable=False)                         # 生成图片宽度, 像素
    height = Column(Integer, nullable=False)                        # 生成图片高度, 像素
    size = Column(Integer, nullable=False)                          # 生成图片数量
    steps = Column(Integer, nullable=False)                         # 迭代步数
    scale = Column(Float, nullable=False)                           # 指导权重
    seed = Column(Integer, default=-1, nullable=False)              # 随机数种子, 设置为-1时将由程序生成一个伪随机数作为种子
    status = Column(Integer, nullable=False)                        # 任务状态: 0-新创建, 1-执行中, 2-已完成
    created_at = Column(DateTime(timezone=True), nullable=False)    # 记录创建时间
    started_at = Column(DateTime(timezone=True))                    # 任务开始执行的时间
    ended_at = Column(DateTime(timezone=True))                      # 任务执行结束的时间
    duration = Column(Integer, nullable=False)                      # 任务花费的总时间, 毫秒, -1代表任务还未执行完
    success = Column(Integer, nullable=False)                       # 任务是否成功: 0-失败, 1-成功, -1代表任务还未执行完
    images = Column(Text, nullable=False)                           # 生成的图像地址, 多个图片地址用半角逗号隔开
