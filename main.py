from __future__ import annotations
import asyncio
from aiogram import Bot ,Dispatcher
from aiogram .client .default import DefaultBotProperties
from aiogram .enums import ParseMode
from bot .handlers import register_handlers
from core .config import get_settings
from core .logging import setup_logging
from database .session import init_db
from scheduler .tasks import setup_scheduler
async def main ()->None :
    settings =get_settings ()
    setup_logging (settings .log_level )
    await init_db ()
    bot =Bot (
    token =settings .bot_token ,
    default =DefaultBotProperties (parse_mode =ParseMode .HTML ),
    )
    dp =Dispatcher ()
    register_handlers (dp )
    scheduler =setup_scheduler (bot )
    try :
        await dp .start_polling (bot )
    finally :
        scheduler .shutdown (wait =False )
        await bot .session .close ()
if __name__ =="__main__":
    asyncio .run (main ())