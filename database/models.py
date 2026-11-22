from __future__ import annotations
from datetime import datetime
from typing import List ,Optional
from sqlalchemy import Boolean ,DateTime ,Float ,ForeignKey ,Integer ,String ,Text
from sqlalchemy .orm import Mapped ,mapped_column ,relationship
from core .utils import utc_now
from database .base import Base
class TimestampMixin :
    created_at :Mapped [datetime ]=mapped_column (DateTime (timezone =True ),default =utc_now )
    updated_at :Mapped [datetime ]=mapped_column (DateTime (timezone =True ),default =utc_now ,onupdate =utc_now )
class User (TimestampMixin ,Base ):
    __tablename__ ="users"
    id :Mapped [int ]=mapped_column (Integer ,primary_key =True )
    telegram_id :Mapped [int ]=mapped_column (Integer ,unique =True ,index =True )
    username :Mapped [Optional [str ]]=mapped_column (String (255 ),nullable =True )
    full_name :Mapped [Optional [str ]]=mapped_column (String (255 ),nullable =True )
    is_admin :Mapped [bool ]=mapped_column (Boolean ,default =False )
    drafts :Mapped [List ["Draft"]]=relationship (back_populates ="user")
    generated_posts :Mapped [List ["GeneratedPost"]]=relationship (back_populates ="user")
    notes :Mapped [List ["Note"]]=relationship (back_populates ="user")
class Source (TimestampMixin ,Base ):
    __tablename__ ="sources"
    id :Mapped [int ]=mapped_column (Integer ,primary_key =True )
    source_type :Mapped [str ]=mapped_column (String (50 ),index =True )
    name :Mapped [str ]=mapped_column (String (255 ))
    url :Mapped [Optional [str ]]=mapped_column (String (500 ),nullable =True )
    is_active :Mapped [bool ]=mapped_column (Boolean ,default =True )
    config_json :Mapped [Optional [str ]]=mapped_column (Text ,nullable =True )
    fetched_items :Mapped [List ["FetchedItem"]]=relationship (back_populates ="source")
class FetchedItem (TimestampMixin ,Base ):
    __tablename__ ="fetched_items"
    id :Mapped [int ]=mapped_column (Integer ,primary_key =True )
    external_id :Mapped [str ]=mapped_column (String (255 ),index =True )
    source_id :Mapped [Optional [int ]]=mapped_column (ForeignKey ("sources.id"),nullable =True )
    source_type :Mapped [str ]=mapped_column (String (50 ),index =True )
    source_name :Mapped [str ]=mapped_column (String (255 ))
    title :Mapped [Optional [str ]]=mapped_column (String (500 ),nullable =True )
    url :Mapped [Optional [str ]]=mapped_column (String (1000 ),nullable =True )
    text :Mapped [str ]=mapped_column (Text )
    summary :Mapped [Optional [str ]]=mapped_column (Text ,nullable =True )
    tags :Mapped [Optional [str ]]=mapped_column (String (500 ),nullable =True )
    published_at :Mapped [Optional [datetime ]]=mapped_column (DateTime (timezone =True ),nullable =True )
    relevance_score :Mapped [float ]=mapped_column (Float ,default =0.0 )
    classification :Mapped [Optional [str ]]=mapped_column (String (100 ),nullable =True )
    raw_payload :Mapped [Optional [str ]]=mapped_column (Text ,nullable =True )
    source :Mapped [Optional ["Source"]]=relationship (back_populates ="fetched_items")
    generated_posts :Mapped [List ["GeneratedPost"]]=relationship (back_populates ="fetched_item")
class Draft (TimestampMixin ,Base ):
    __tablename__ ="drafts"
    id :Mapped [int ]=mapped_column (Integer ,primary_key =True )
    user_id :Mapped [int ]=mapped_column (ForeignKey ("users.id"))
    title :Mapped [Optional [str ]]=mapped_column (String (255 ),nullable =True )
    content :Mapped [str ]=mapped_column (Text )
    format_type :Mapped [Optional [str ]]=mapped_column (String (100 ),nullable =True )
    status :Mapped [str ]=mapped_column (String (50 ),default ="draft")
    image_url :Mapped [Optional [str ]]=mapped_column (String (1000 ),nullable =True )
    user :Mapped ["User"]=relationship (back_populates ="drafts")
    generated_posts :Mapped [List ["GeneratedPost"]]=relationship (back_populates ="draft")
class GeneratedPost (TimestampMixin ,Base ):
    __tablename__ ="generated_posts"
    id :Mapped [int ]=mapped_column (Integer ,primary_key =True )
    user_id :Mapped [Optional [int ]]=mapped_column (ForeignKey ("users.id"),nullable =True )
    draft_id :Mapped [Optional [int ]]=mapped_column (ForeignKey ("drafts.id"),nullable =True )
    fetched_item_id :Mapped [Optional [int ]]=mapped_column (ForeignKey ("fetched_items.id"),nullable =True )
    format_type :Mapped [str ]=mapped_column (String (100 ))
    tone :Mapped [str ]=mapped_column (String (100 ),default ="default")
    title :Mapped [Optional [str ]]=mapped_column (String (255 ),nullable =True )
    content :Mapped [str ]=mapped_column (Text )
    short_version :Mapped [Optional [str ]]=mapped_column (Text ,nullable =True )
    hashtags :Mapped [Optional [str ]]=mapped_column (String (500 ),nullable =True )
    cta :Mapped [Optional [str ]]=mapped_column (String (500 ),nullable =True )
    image_url :Mapped [Optional [str ]]=mapped_column (String (1000 ),nullable =True )
    status :Mapped [str ]=mapped_column (String (50 ),default ="generated")
    user :Mapped [Optional ["User"]]=relationship (back_populates ="generated_posts")
    draft :Mapped [Optional ["Draft"]]=relationship (back_populates ="generated_posts")
    fetched_item :Mapped [Optional ["FetchedItem"]]=relationship (back_populates ="generated_posts")
    publication_history :Mapped [List ["PublicationHistory"]]=relationship (back_populates ="generated_post")
class PublicationHistory (TimestampMixin ,Base ):
    __tablename__ ="publication_history"
    id :Mapped [int ]=mapped_column (Integer ,primary_key =True )
    generated_post_id :Mapped [int ]=mapped_column (ForeignKey ("generated_posts.id"))
    channel_id :Mapped [str ]=mapped_column (String (255 ))
    telegram_message_id :Mapped [Optional [int ]]=mapped_column (Integer ,nullable =True )
    status :Mapped [str ]=mapped_column (String (50 ),default ="pending")
    error_message :Mapped [Optional [str ]]=mapped_column (Text ,nullable =True )
    generated_post :Mapped ["GeneratedPost"]=relationship (back_populates ="publication_history")
class ProjectUpdate (TimestampMixin ,Base ):
    __tablename__ ="project_updates"
    id :Mapped [int ]=mapped_column (Integer ,primary_key =True )
    title :Mapped [str ]=mapped_column (String (255 ))
    description :Mapped [str ]=mapped_column (Text )
    commit_hash :Mapped [Optional [str ]]=mapped_column (String (64 ),nullable =True )
    pr_url :Mapped [Optional [str ]]=mapped_column (String (1000 ),nullable =True )
    metadata_json :Mapped [Optional [str ]]=mapped_column (Text ,nullable =True )
    is_processed :Mapped [bool ]=mapped_column (Boolean ,default =False )
class Note (TimestampMixin ,Base ):
    __tablename__ ="notes"
    id :Mapped [int ]=mapped_column (Integer ,primary_key =True )
    user_id :Mapped [Optional [int ]]=mapped_column (ForeignKey ("users.id"),nullable =True )
    title :Mapped [Optional [str ]]=mapped_column (String (255 ),nullable =True )
    body :Mapped [str ]=mapped_column (Text )
    tags :Mapped [Optional [str ]]=mapped_column (String (500 ),nullable =True )
    is_processed :Mapped [bool ]=mapped_column (Boolean ,default =False )
    user :Mapped [Optional ["User"]]=relationship (back_populates ="notes")