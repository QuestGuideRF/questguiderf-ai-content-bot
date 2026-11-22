from __future__ import annotations
from typing import Any
import httpx
from core .config import get_settings
class GitHubClient :
    def __init__ (self )->None :
        self .settings =get_settings ()
        self .base_url =f"https://api.github.com/repos/{self .settings .github_repo }"
        self .timeout =httpx .Timeout (20.0 ,connect =10.0 )
    async def get_recent_commits (self ,limit :int =5 )->list [dict [str ,Any ]]:
        async with httpx .AsyncClient (timeout =self .timeout )as client :
            response =await client .get (
            f"{self .base_url }/commits",
            params ={"per_page":limit },
            headers ={"Accept":"приложение/vnd.github+json"},
            )
            response .raise_for_status ()
            return response .json ()
    async def get_repo_description (self )->dict [str ,Any ]:
        async with httpx .AsyncClient (timeout =self .timeout )as client :
            response =await client .get (
            self .base_url ,
            headers ={"Accept":"приложение/vnd.github+json"},
            )
            response .raise_for_status ()
            return response .json ()