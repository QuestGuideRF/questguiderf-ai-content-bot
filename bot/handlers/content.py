from __future__ import annotations
from aiogram import Bot ,F ,Router
from aiogram .fsm .context import FSMContext
from aiogram .types import Message
from bot .keyboards .main import format_keyboard ,main_menu_keyboard ,tone_keyboard
from bot .states .post_flow import PostFlow
from content .styles import TONES
from core .config import get_settings
from core .utils import join_non_empty ,trim_text
from database .repositories import (
DraftRepository ,
FetchedItemRepository ,
GeneratedPostRepository ,
PublicationRepository ,
SourceRepository ,
UserRepository ,
)
from database .session import session_scope
from services .draft_service import DraftService
from services .pipeline import ContentPipeline
from services .post_generator import PostGenerator
from services .publisher import Publisher
router =Router ()
@router .message (F .text .in_ (["Новый пост","Улучшить текст"]))
async def start_manual_flow (message :Message ,state :FSMContext )->None :
    await state .set_state (PostFlow .waiting_for_raw_text )
    await message .answer (
    "Пришлите сырой текст, идею, заметку или анонс. Затем я предложу улучшенную версию.",
    reply_markup =tone_keyboard (),
    )
@router .message (PostFlow .waiting_for_raw_text ,F .text )
async def capture_raw_text (message :Message ,state :FSMContext )->None :
    await state .update_data (raw_text =message .text )
    await state .set_state (PostFlow .waiting_for_tone )
    await message .answer ("Текст получил. Теперь выберите стиль:",reply_markup =tone_keyboard ())
@router .message (PostFlow .waiting_for_tone ,F .text .in_ (list (TONES .keys ())))
async def improve_text (message :Message ,state :FSMContext )->None :
    data =await state .get_data ()
    bundle =await PostGenerator ().improve_user_text (data ["raw_text"],message .text .strip ())
    preview =join_non_empty ([f"<b>{bundle .title }</b>",bundle .content ,bundle .hashtags ,bundle .cta ])
    await state .update_data (
    generated_title =bundle .title ,
    generated_content =bundle .content ,
    generated_hashtags =bundle .hashtags ,
    generated_cta =bundle .cta ,
    generated_format =bundle .format_type ,
    )
    await state .set_state (PostFlow .ready_for_action )
    await message .answer (
    f"{trim_text (preview ,3900 )}\n\nМожно сохранить пост в черновики или сразу опубликовать.",
    reply_markup =main_menu_keyboard (),
    )
@router .message (F .text =="Собрать новости")
async def collect_news (message :Message ,state :FSMContext )->None :
    async with session_scope ()as session :
        pipeline =ContentPipeline (
        source_repo =SourceRepository (session ),
        fetched_repo =FetchedItemRepository (session ),
        generated_repo =GeneratedPostRepository (session ),
        )
        items =await pipeline .collect_and_store_materials ()
    if not items :
        await message .answer ("Новых материалов пока не найдено. Проверьте источники или повторите позже.")
        return
    lines =[
    f"{index }. {item .title or 'Без заголовка'} [{item .classification or 'unclassified'} | {item .relevance_score :.2f}]"
    for index ,item in enumerate (items [:5 ],start =1 )
    ]
    await state .set_state (PostFlow .waiting_for_format )
    await message .answer ("Собрал материалы:\n\n"+"\n".join (lines ),reply_markup =format_keyboard ())
@router .message (F .text .in_ (["Пост о проекте","Пост о туризме","Смешанный пост","Сгенерировать пост"]))
async def generate_post (message :Message ,state :FSMContext )->None :
    requested_format ={
    "Пост о проекте":"project_update",
    "Пост о туризме":"travel_post",
    "Смешанный пост":"mixed_post",
    "Сгенерировать пост":None ,
    }[message .text .strip ()]
    async with session_scope ()as session :
        fetched_repo =FetchedItemRepository (session )
        items =await fetched_repo .latest_relevant (classification =requested_format ,limit =1 )
        if not items :
            items =await fetched_repo .latest_relevant (limit =1 )
        if not items :
            await message .answer ("Материалов ещё нет. Сначала нажмите «Собрать новости».")
            return
        pipeline =ContentPipeline (
        source_repo =SourceRepository (session ),
        fetched_repo =fetched_repo ,
        generated_repo =GeneratedPostRepository (session ),
        )
        bundle =await pipeline .generate_post_from_item (items [0 ],user_id =message .from_user .id )
    preview =join_non_empty ([f"<b>{bundle .title }</b>",bundle .content ,bundle .hashtags ,bundle .cta ])
    await state .update_data (
    generated_title =bundle .title ,
    generated_content =bundle .content ,
    generated_hashtags =bundle .hashtags ,
    generated_cta =bundle .cta ,
    generated_format =bundle .format_type ,
    )
    await state .set_state (PostFlow .ready_for_action )
    await message .answer (trim_text (preview ,3900 ),reply_markup =main_menu_keyboard ())
@router .message (F .text =="Сохранить в черновики")
async def save_draft (message :Message ,state :FSMContext )->None :
    data =await state .get_data ()
    content =data .get ("generated_content")or data .get ("raw_text")
    if not content :
        await message .answer ("Пока нечего сохранять. Сначала создайте или улучшите пост.")
        return
    settings =get_settings ()
    async with session_scope ()as session :
        user_repo =UserRepository (session )
        user =await user_repo .get_or_create (
        telegram_id =message .from_user .id ,
        username =message .from_user .username ,
        full_name =message .from_user .full_name ,
        is_admin =message .from_user .id in settings .telegram_admin_ids ,
        )
        draft =await DraftService (DraftRepository (session )).save_draft (
        user_id =user .id ,
        content =content ,
        title =data .get ("generated_title"),
        format_type =data .get ("generated_format"),
        )
    await message .answer (f"Черновик сохранён. ID: {draft .id }",reply_markup =main_menu_keyboard ())
@router .message (F .text =="Опубликовать в канал")
async def publish_post (message :Message ,state :FSMContext ,bot :Bot )->None :
    data =await state .get_data ()
    if not data .get ("generated_content"):
        await message .answer ("Сейчас нет поста для публикации.")
        return
    publisher =Publisher (bot )
    sent_message =await publisher .publish (
    title =data .get ("generated_title"),
    content =data ["generated_content"],
    hashtags =data .get ("generated_hashtags"),
    cta =data .get ("generated_cta"),
    )
    async with session_scope ()as session :
        generated =await GeneratedPostRepository (session ).create (
        user_id =message .from_user .id ,
        draft_id =None ,
        fetched_item_id =None ,
        format_type =data .get ("generated_format","manual_improve"),
        tone ="published",
        title =data .get ("generated_title"),
        content =data ["generated_content"],
        short_version =None ,
        hashtags =data .get ("generated_hashtags"),
        cta =data .get ("generated_cta"),
        )
        await PublicationRepository (session ).create (
        generated_post_id =generated .id ,
        channel_id =get_settings ().channel_id ,
        status ="published",
        message_id =sent_message .message_id ,
        )
    await message .answer (f"Пост опубликован. Message ID: {sent_message .message_id }",reply_markup =main_menu_keyboard ())
@router .message (F .text =="Добавить картинку")
async def add_image_info (message :Message )->None :
    await message .answer (
    "В текущем MVP загрузка изображения в черновик ещё не заведена в FSM. "
    "Но Publisher уже умеет отправлять пост с изображением, и этот шаг легко расширяется."
    )