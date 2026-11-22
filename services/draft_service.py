from __future__ import annotations
from collections .abc import Sequence
from database .repositories import DraftRepository
class DraftService :
    def __init__ (self ,repository :DraftRepository )->None :
        self .repository =repository
    async def save_draft (self ,user_id :int ,content :str ,title :str |None =None ,format_type :str |None =None ):
        return await self .repository .create (user_id =user_id ,content =content ,title =title ,format_type =format_type )
    async def list_drafts (self ,user_id :int ,limit :int =10 )->Sequence :
        return await self .repository .list_for_user (user_id =user_id ,limit =limit )
    async def get_draft (self ,draft_id :int ):
        return await self .repository .get (draft_id )
    async def delete_draft (self ,draft_id :int )->bool :
        draft =await self .repository .get (draft_id )
        if not draft :
            return False
        await self .repository .delete (draft )
        return True