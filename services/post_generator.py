from __future__ import annotations
import json
import logging
from dataclasses import dataclass
from content .styles import TONES
from integrations .cloudflare_ai import CloudflareAIClient
from services .prompt_manager import PromptManager
from services .source_aggregator import Material
logger =logging .getLogger (__name__ )
@dataclass
class GeneratedPostBundle :
    title :str
    content :str
    short_version :str
    cta :str
    hashtags :str
    format_type :str
    tone :str
class PostGenerator :
    def __init__ (self )->None :
        self .ai =CloudflareAIClient ()
        self .prompts =PromptManager ()
    async def summarize (self ,text :str )->str :
        system_prompt ,prompt =self .prompts .render ("summarize_news",text =text )
        return await self .ai .generate (prompt ,system_prompt )
    async def classify (self ,text :str )->dict :
        system_prompt ,prompt =self .prompts .render ("classify_material",text =text )
        raw =await self .ai .generate (prompt ,system_prompt )
        try :
            return json .loads (raw )
        except json .JSONDecodeError :
            logger .warning ("Ответ классификации не был JSON: %s",raw )
            return {"classification":"travel_post","relevance_score":0.5 ,"reason":raw }
    async def improve_user_text (self ,text :str ,tone_key :str )->GeneratedPostBundle :
        tone =TONES .get (tone_key ,TONES ["обычный"])
        system_prompt ,prompt =self .prompts .render ("improve_user_text",text =text ,tone =tone )
        content =await self .ai .generate (prompt ,system_prompt )
        return await self ._finalize_bundle (content ,"manual_improve",tone_key )
    async def generate_from_material (self ,material :Material ,format_type :str )->GeneratedPostBundle :
        prompt_key ={
        "project_update":"generate_project_post",
        "mixed_post":"generate_mixed_post",
        "travel_post":"generate_news_post",
        "news":"generate_news_post",
        }.get (format_type ,"generate_news_post")
        system_prompt ,prompt =self .prompts .render (prompt_key ,text =material .summary or material .text )
        content =await self .ai .generate (prompt ,system_prompt )
        return await self ._finalize_bundle (content ,format_type ,"обычный")
    async def _finalize_bundle (self ,content :str ,format_type :str ,tone_key :str )->GeneratedPostBundle :
        title_system ,title_prompt =self .prompts .render ("generate_title",text =content )
        short_system ,short_prompt =self .prompts .render ("generate_short_version",text =content )
        cta_system ,cta_prompt =self .prompts .render ("generate_cta",text =content )
        tag_system ,tag_prompt =self .prompts .render ("generate_hashtags",text =content )
        title =await self .ai .generate (title_prompt ,title_system )
        short_version =await self .ai .generate (short_prompt ,short_system )
        cta =await self .ai .generate (cta_prompt ,cta_system )
        hashtags =await self .ai .generate (tag_prompt ,tag_system )
        return GeneratedPostBundle (
        title =title ,
        content =content ,
        short_version =short_version ,
        cta =cta ,
        hashtags =hashtags ,
        format_type =format_type ,
        tone =tone_key ,
        )