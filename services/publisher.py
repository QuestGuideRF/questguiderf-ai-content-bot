from __future__ import annotations
from aiogram import Bot
from aiogram .types import BufferedInputFile
from core .config import get_settings
from core .utils import join_non_empty
class Publisher :
    def __init__ (self ,bot :Bot )->None :
        self .bot =bot
        self .settings =get_settings ()
    async def preview_text (self ,title :str ,content :str ,hashtags :str |None ,cta :str |None )->str :
        return join_non_empty ([f"<b>{title }</b>"if title else "",content ,hashtags ,cta ])
    async def publish (self ,title :str ,content :str ,hashtags :str |None =None ,cta :str |None =None ,image_bytes :bytes |None =None ,image_name :str ="cover.jpg"):
        text =await self .preview_text (title =title ,content =content ,hashtags =hashtags ,cta =cta )
        if image_bytes :
            media =BufferedInputFile (image_bytes ,filename =image_name )
            return await self .bot .send_photo (chat_id =self .settings .channel_id ,photo =media ,caption =text )
        return await self .bot .send_message (chat_id =self .settings .channel_id ,text =text )