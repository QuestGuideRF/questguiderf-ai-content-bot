from __future__ import annotations
from contextlib import asynccontextmanager
from sqlalchemy .ext .asyncio import AsyncSession ,async_sessionmaker ,create_async_engine
from core .config import get_settings
from database .base import Base
settings =get_settings ()
engine =create_async_engine (settings .database_url ,echo =False ,future =True )
SessionLocal =async_sessionmaker (engine ,expire_on_commit =False ,class_ =AsyncSession )
async def init_db ()->None :
    async with engine .begin ()as conn :
        await conn .run_sync (Base .metadata .create_all )
@asynccontextmanager
async def session_scope ()->AsyncSession :
    session =SessionLocal ()
    try :
        yield session
        await session .commit ()
    except Exception :
        await session .rollback ()
        raise
    finally :
        await session .close ()