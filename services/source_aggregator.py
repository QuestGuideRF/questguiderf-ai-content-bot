from __future__ import annotations
import hashlib
import json
import logging
from abc import ABC ,abstractmethod
from dataclasses import dataclass ,field
from datetime import datetime
from typing import Any
import aiofiles
import httpx
from bs4 import BeautifulSoup
from core .config import get_settings
from integrations .github_client import GitHubClient
logger =logging .getLogger (__name__ )
@dataclass
class Material :
    id :str
    source_type :str
    source_name :str
    title :str |None
    url :str |None
    text :str
    summary :str |None =None
    tags :list [str ]=field (default_factory =list )
    published_at :datetime |None =None
    relevance_score :float =0.0
    raw_payload :dict [str ,Any ]|None =None
class BaseSource (ABC ):
    source_type :str
    source_name :str
    @abstractmethod
    async def fetch_new_materials (self )->list [Material ]:
        raise NotImplementedError
    def normalize (self ,payload :dict [str ,Any ])->Material :
        text =payload .get ("text")or payload .get ("body")or payload .get ("content")or ""
        title =payload .get ("title")or payload .get ("name")
        url =payload .get ("url")or payload .get ("html_url")
        raw_id =payload .get ("id")or payload .get ("sha")or title or text [:50 ]
        material_id =hashlib .sha1 (f"{self .source_type }:{raw_id }".encode ("utf-8")).hexdigest ()
        return Material (
        id =material_id ,
        source_type =self .source_type ,
        source_name =self .source_name ,
        title =title ,
        url =url ,
        text =text .strip (),
        raw_payload =payload ,
        )
class WebsiteSource (BaseSource ):
    source_type ="website"
    def __init__ (self ,url :str )->None :
        self .url =url
        self .source_name =url
    async def fetch_new_materials (self )->list [Material ]:
        async with httpx .AsyncClient (timeout =20.0 )as client :
            response =await client .get (self .url )
            response .raise_for_status ()
        soup =BeautifulSoup (response .text ,"html.parser")
        title =soup .title .text .strip ()if soup .title else self .url
        paragraphs =[p .get_text (" ",strip =True )for p in soup .select ("p")[:12 ]]
        text ="\n".join (part for part in paragraphs if part )
        if not text :
            return []
        return [self .normalize ({"id":self .url ,"title":title ,"url":self .url ,"text":text })]
class GitHubSource (BaseSource ):
    source_type ="github"
    source_name ="GitHub"
    def __init__ (self )->None :
        self .client =GitHubClient ()
    async def fetch_new_materials (self )->list [Material ]:
        commits =await self .client .get_recent_commits ()
        return [
        self .normalize (
        {
        "id":commit .get ("sha"),
        "title":commit .get ("commit",{}).get ("message","").splitlines ()[0 ],
        "url":commit .get ("html_url"),
        "text":commit .get ("commit",{}).get ("message",""),
        }
        )
        for commit in commits
        ]
class TelegramSource (BaseSource ):
    source_type ="telegram"
    def __init__ (self ,public_feed_url :str )->None :
        self .url =public_feed_url
        self .source_name =public_feed_url
    async def fetch_new_materials (self )->list [Material ]:
        async with httpx .AsyncClient (timeout =20.0 )as client :
            response =await client .get (self .url )
            response .raise_for_status ()
        soup =BeautifulSoup (response .text ,"html.parser")
        messages =soup .select (".tgme_widget_message_text")[:5 ]
        result :list [Material ]=[]
        for index ,node in enumerate (messages ):
            text =node .get_text ("\n",strip =True )
            if not text :
                continue
            result .append (
            self .normalize (
            {
            "id":f"{self .url }:{index }",
            "title":text .splitlines ()[0 ][:80 ],
            "url":self .url ,
            "text":text ,
            }
            )
            )
        return result
class NotesSource (BaseSource ):
    source_type ="notes"
    source_name ="Местные заметки"
    def __init__ (self ,path :str )->None :
        self .path =path
    async def fetch_new_materials (self )->list [Material ]:
        try :
            async with aiofiles .open (self .path ,"r",encoding ="utf-8")as file :
                text =await file .read ()
        except FileNotFoundError :
            logger .info ("Файл заметок %s пока не найден.",self .path )
            return []
        chunks =[chunk .strip ()for chunk in text .split ("\n---\n")if chunk .strip ()]
        return [
        self .normalize ({"id":f"note-{index }","title":chunk .splitlines ()[0 ][:80 ],"text":chunk })
        for index ,chunk in enumerate (chunks )
        ]
class SourceAggregator :
    def __init__ (self )->None :
        settings =get_settings ()
        self .sources :list [BaseSource ]=[
        GitHubSource (),
        NotesSource (settings .notes_storage_path ),
        *(WebsiteSource (url )for url in settings .website_sources ),
        *(TelegramSource (url )for url in settings .telegram_source_urls ),
        ]
        self .max_source_items =settings .max_source_items
    async def collect (self )->list [Material ]:
        materials :list [Material ]=[]
        for source in self .sources :
            try :
                materials .extend ((await source .fetch_new_materials ())[:self .max_source_items ])
            except Exception as exc :
                logger .exception ("Ошибка источника %s: %s",source .source_name ,exc )
        return materials
    @staticmethod
    def serialize_payload (payload :dict [str ,Any ]|None )->str |None :
        if payload is None :
            return None
        return json .dumps (payload ,ensure_ascii =False )