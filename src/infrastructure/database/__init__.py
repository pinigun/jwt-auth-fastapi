from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from settings import settings

engine = create_async_engine(settings.POSTGRES_DSN)
async_session_maker = async_sessionmaker(bind=engine)


async def get_async_session():
    async with async_session_maker() as session:
        yield session
