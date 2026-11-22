from __future__ import annotations
from functools import lru_cache
from typing import List
import json
from pydantic import Field ,computed_field ,field_validator
from pydantic_settings import BaseSettings ,SettingsConfigDict
class Settings (BaseSettings ):
    model_config =SettingsConfigDict (
    env_file =".env",
    env_file_encoding ="utf-8",
    case_sensitive =False ,
    extra ="ignore",
    )
    bot_token :str =Field (alias ="BOT_TOKEN")
    channel_id :str =Field (alias ="CHANNEL_ID")
    cf_account_id :str =Field (alias ="CF_ACCOUNT_ID")
    cf_api_token :str =Field (alias ="CF_API_TOKEN")
    cf_model :str =Field (default ="@cf/meta/llama-3.1-8b-instruct",alias ="CF_MODEL")
    github_repo :str =Field (alias ="GITHUB_REPO")
    database_url :str =Field (default ="sqlite+aiosqlite:///./storage/app.db",alias ="DATABASE_URL")
    log_level :str =Field (default ="INFO",alias ="LOG_LEVEL")
    telegram_admin_ids :List [int ]=Field (default_factory =list ,alias ="TELEGRAM_ADMIN_IDS")
    auto_fetch_enabled :bool =Field (default =True ,alias ="AUTO_FETCH_ENABLED")
    auto_fetch_cron :str =Field (default ="*/30 * * * *",alias ="AUTO_FETCH_CRON")
    max_source_items :int =Field (default =10 ,alias ="MAX_SOURCE_ITEMS")
    notes_storage_path :str =Field (default ="storage/notes/inbox.md",alias ="NOTES_STORAGE_PATH")
    website_sources :List [str ]=Field (default_factory =list ,alias ="WEBSITE_SOURCES")
    telegram_source_urls :List [str ]=Field (default_factory =list ,alias ="TELEGRAM_SOURCE_URLS")
    publish_preview_enabled :bool =Field (default =True ,alias ="PUBLISH_PREVIEW_ENABLED")
    @field_validator ("telegram_admin_ids","website_sources","telegram_source_urls",mode ="before")
    @classmethod
    def parse_csv_or_json_list (cls ,value ):
        if value in (None ,"",[]):
            return []
        if isinstance (value ,list ):
            return value
        if isinstance (value ,str ):
            stripped =value .strip ()
            if not stripped :
                return []
            if stripped .startswith ("["):
                return json .loads (stripped )
            return [item .strip ()for item in stripped .split (",")if item .strip ()]
        return value
    @computed_field
    @property
    def cf_api_base (self )->str :
        return (
        f"https://api.cloudflare.com/client/v4/accounts/"
        f"{self .cf_account_id }/ai/run/{self .cf_model }"
        )
@lru_cache (maxsize =1 )
def get_settings ()->Settings :
    return Settings ()