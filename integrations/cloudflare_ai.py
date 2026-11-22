from __future__ import annotations
import asyncio
import logging
from typing import Any
import httpx
from core .config import get_settings
logger =logging .getLogger (__name__ )
class CloudflareAIError (Exception ):
    pass
class CloudflareAIClient :
    def __init__ (self )->None :
        self .settings =get_settings ()
        self .timeout =httpx .Timeout (45.0 ,connect =10.0 )
        self .headers ={
        "Authorization":f"Bearer {self .settings .cf_api_token }",
        "Content-Type":"application/json",
        }
    async def generate (self ,prompt :str ,system_prompt :str |None =None ,temperature :float =0.2 )->str :
        payload :dict [str ,Any ]={
        "messages":[],
        "temperature":temperature ,
        "max_tokens":1200 ,
        }
        if system_prompt :
            payload ["messages"].append ({"role":"system","content":system_prompt })
        payload ["messages"].append ({"role":"user","content":prompt })
        for attempt in range (1 ,4 ):
            try :
                async with httpx .AsyncClient (timeout =self .timeout )as client :
                    response =await client .post (
                    self .settings .cf_api_base ,
                    headers =self .headers ,
                    json =payload ,
                    )
                response .raise_for_status ()
                data =response .json ()
                if not data .get ("success",True ):
                    raise CloudflareAIError (str (data .get ("errors")))
                result =data .get ("result",{})
                if isinstance (result ,dict ):
                    if "response"in result :
                        return str (result ["response"]).strip ()
                    if "text"in result :
                        return str (result ["text"]).strip ()
                return str (result ).strip ()
            except (httpx .HTTPError ,CloudflareAIError )as exc :
                logger .warning ("Не удалось выполнить запрос Cloudflare AI при попытке %s: %s",attempt ,exc )
                if attempt ==3 :
                    raise CloudflareAIError ("Запрос Cloudflare AI не выполнен после повторных попыток")from exc
                await asyncio .sleep (attempt )
        raise CloudflareAIError ("Неожиданный сбой искусственного интеллекта Cloudflare")