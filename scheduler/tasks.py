from __future__ import annotations
import asyncio
import logging
from apscheduler .schedulers .asyncio import AsyncIOScheduler
from aiogram import Bot
from core .config import get_settings
from database .repositories import FetchedItemRepository ,GeneratedPostRepository ,SourceRepository
from database .session import session_scope
from services .pipeline import ContentPipeline
logger =logging .getLogger (__name__ )
async def run_auto_collection (bot :Bot )->None :
    if not get_settings ().auto_fetch_enabled :
        return
    async with session_scope ()as session :
        pipeline =ContentPipeline (
        source_repo =SourceRepository (session ),
        fetched_repo =FetchedItemRepository (session ),
        generated_repo =GeneratedPostRepository (session ),
        )
        items =await pipeline .collect_and_store_materials ()
    logger .info ("Автоматический сбор завершен: %s элементов.",len (items ))
    if items :
        await bot .send_message (
        chat_id =get_settings ().channel_id ,
        text =f"Служебное уведомление: найдено {len (items )} новых материалов для редакции.",
        )
def setup_scheduler (bot :Bot )->AsyncIOScheduler :
    settings =get_settings ()
    scheduler =AsyncIOScheduler ()
    if settings .auto_fetch_enabled :
        minute_field =settings .auto_fetch_cron .split ()[0 ]
        if minute_field .startswith ("*/"):
            scheduler .add_job (
            lambda :asyncio .create_task (run_auto_collection (bot )),
            "interval",
            minutes =int (minute_field .replace ("*/","")),
            )
    scheduler .start ()
    return scheduler