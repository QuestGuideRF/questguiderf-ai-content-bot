from __future__ import annotations
from collections .abc import Sequence
from typing import Optional
from sqlalchemy import select
from sqlalchemy .ext .asyncio import AsyncSession
from database .models import Draft ,FetchedItem ,GeneratedPost ,Note ,PublicationHistory ,Source ,User
class UserRepository :
    def __init__ (self ,session :AsyncSession )->None :
        self .session =session
    async def get_or_create (self ,telegram_id :int ,username :Optional [str ],full_name :Optional [str ],is_admin :bool )->User :
        result =await self .session .execute (select (User ).where (User .telegram_id ==telegram_id ))
        user =result .scalar_one_or_none ()
        if user :
            user .username =username
            user .full_name =full_name
            user .is_admin =is_admin
            await self .session .flush ()
            return user
        user =User (telegram_id =telegram_id ,username =username ,full_name =full_name ,is_admin =is_admin )
        self .session .add (user )
        await self .session .flush ()
        return user
class DraftRepository :
    def __init__ (self ,session :AsyncSession )->None :
        self .session =session
    async def create (self ,user_id :int ,content :str ,title :str |None =None ,format_type :str |None =None )->Draft :
        draft =Draft (user_id =user_id ,content =content ,title =title ,format_type =format_type )
        self .session .add (draft )
        await self .session .flush ()
        return draft
    async def get (self ,draft_id :int )->Draft |None :
        result =await self .session .execute (select (Draft ).where (Draft .id ==draft_id ))
        return result .scalar_one_or_none ()
    async def list_for_user (self ,user_id :int ,limit :int =10 )->Sequence [Draft ]:
        result =await self .session .execute (select (Draft ).where (Draft .user_id ==user_id ).order_by (Draft .updated_at .desc ()).limit (limit ))
        return result .scalars ().all ()
    async def delete (self ,draft :Draft )->None :
        await self .session .delete (draft )
class SourceRepository :
    def __init__ (self ,session :AsyncSession )->None :
        self .session =session
    async def get_or_create (self ,source_type :str ,name :str ,url :str |None =None )->Source :
        result =await self .session .execute (select (Source ).where (Source .source_type ==source_type ,Source .name ==name ))
        source =result .scalar_one_or_none ()
        if source :
            source .url =url
            return source
        source =Source (source_type =source_type ,name =name ,url =url )
        self .session .add (source )
        await self .session .flush ()
        return source
class FetchedItemRepository :
    def __init__ (self ,session :AsyncSession )->None :
        self .session =session
    async def exists (self ,external_id :str ,source_type :str )->bool :
        result =await self .session .execute (
        select (FetchedItem .id ).where (FetchedItem .external_id ==external_id ,FetchedItem .source_type ==source_type )
        )
        return result .scalar_one_or_none ()is not None
    async def create (self ,item :FetchedItem )->FetchedItem :
        self .session .add (item )
        await self .session .flush ()
        return item
    async def latest_relevant (self ,classification :str |None =None ,limit :int =10 )->Sequence [FetchedItem ]:
        stmt =select (FetchedItem ).order_by (FetchedItem .relevance_score .desc (),FetchedItem .created_at .desc ()).limit (limit )
        if classification :
            stmt =stmt .where (FetchedItem .classification ==classification )
        result =await self .session .execute (stmt )
        return result .scalars ().all ()
class GeneratedPostRepository :
    def __init__ (self ,session :AsyncSession )->None :
        self .session =session
    async def create (
    self ,
    *,
    user_id :int |None ,
    draft_id :int |None ,
    fetched_item_id :int |None ,
    format_type :str ,
    tone :str ,
    title :str |None ,
    content :str ,
    short_version :str |None ,
    hashtags :str |None ,
    cta :str |None ,
    )->GeneratedPost :
        post =GeneratedPost (
        user_id =user_id ,
        draft_id =draft_id ,
        fetched_item_id =fetched_item_id ,
        format_type =format_type ,
        tone =tone ,
        title =title ,
        content =content ,
        short_version =short_version ,
        hashtags =hashtags ,
        cta =cta ,
        )
        self .session .add (post )
        await self .session .flush ()
        return post
class PublicationRepository :
    def __init__ (self ,session :AsyncSession )->None :
        self .session =session
    async def create (self ,generated_post_id :int ,channel_id :str ,status :str ,message_id :int |None =None ,error_message :str |None =None )->PublicationHistory :
        history =PublicationHistory (
        generated_post_id =generated_post_id ,
        channel_id =channel_id ,
        status =status ,
        telegram_message_id =message_id ,
        error_message =error_message ,
        )
        self .session .add (history )
        await self .session .flush ()
        return history
class NoteRepository :
    def __init__ (self ,session :AsyncSession )->None :
        self .session =session
    async def create (self ,body :str ,user_id :int |None =None ,title :str |None =None ,tags :str |None =None )->Note :
        note =Note (user_id =user_id ,title =title ,body =body ,tags =tags )
        self .session .add (note )
        await self .session .flush ()
        return note