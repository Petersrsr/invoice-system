from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

# SQLite 需要关闭线程检查，便于 FastAPI 请求线程复用连接。
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    # 每个请求分配独立会话，请求结束后统一释放。
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
