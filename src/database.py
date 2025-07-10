from sqlalchemy.ext.asyncio import (AsyncSession,
                                    async_sessionmaker,
                                    create_async_engine)

async_engine = create_async_engine(
    url='sqlite+aiosqlite:///db_file/complaints.db',
    echo=True
)
async_session_maker = async_sessionmaker(bind=async_engine,
                                         class_=AsyncSession,
                                         expire_on_commit=False)
