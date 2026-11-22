from __future__ import annotations
from aiogram .types import KeyboardButton ,ReplyKeyboardMarkup
from content .styles import TONES
def _keyboard (rows :list [list [str ]])->ReplyKeyboardMarkup :
    return ReplyKeyboardMarkup (
    keyboard =[[KeyboardButton (text =text )for text in row ]for row in rows ],
    resize_keyboard =True ,
    )
def main_menu_keyboard ()->ReplyKeyboardMarkup :
    return _keyboard (
    [
    ["Новый пост","Улучшить текст"],
    ["Сгенерировать пост","Собрать новости"],
    ["Пост о проекте","Пост о туризме"],
    ["Смешанный пост","Добавить картинку"],
    ["Опубликовать в канал","Сохранить в черновики"],
    ]
    )
def tone_keyboard ()->ReplyKeyboardMarkup :
    keys =list (TONES .keys ())
    return _keyboard ([keys [:3 ],keys [3 :]])
def format_keyboard ()->ReplyKeyboardMarkup :
    return _keyboard ([["Пост о проекте","Пост о туризме","Смешанный пост"]])