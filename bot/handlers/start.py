from __future__ import annotations
from aiogram import Router
from aiogram .filters import CommandStart
from aiogram .types import Message
from bot .keyboards .main import main_menu_keyboard
from core .config import get_settings
from database .repositories import UserRepository
from database .session import session_scope
router =Router ()
@router .message (CommandStart ())
async def cmd_start (message :Message )->None :
    settings =get_settings ()
    async with session_scope ()as session :
        repository =UserRepository (session )
        user =message .from_user
        await repository .get_or_create (
        telegram_id =user .id ,
        username =user .username ,
        full_name =user .full_name ,
        is_admin =user .id in settings .telegram_admin_ids ,
        )
    await message .answer (
    "QuestGuideRF AI Content Bot готов к работе.\n\n"
    "Я собираю материалы, улучшаю черновики, сохраняю посты и готовлю публикации для канала.",
    reply_markup =main_menu_keyboard (),
    )