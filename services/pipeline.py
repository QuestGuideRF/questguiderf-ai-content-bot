from __future__ import annotations
from database .models import FetchedItem
from database .repositories import FetchedItemRepository ,GeneratedPostRepository ,SourceRepository
from services .post_generator import GeneratedPostBundle ,PostGenerator
from services .source_aggregator import Material ,SourceAggregator
class ContentPipeline :
    def __init__ (self ,source_repo :SourceRepository ,fetched_repo :FetchedItemRepository ,generated_repo :GeneratedPostRepository )->None :
        self .aggregator =SourceAggregator ()
        self .generator =PostGenerator ()
        self .source_repo =source_repo
        self .fetched_repo =fetched_repo
        self .generated_repo =generated_repo
    async def collect_and_store_materials (self )->list [FetchedItem ]:
        materials =await self .aggregator .collect ()
        stored :list [FetchedItem ]=[]
        for material in materials :
            if await self .fetched_repo .exists (material .id ,material .source_type ):
                continue
            summary =await self .generator .summarize (material .text )
            classification_data =await self .generator .classify (summary )
            source =await self .source_repo .get_or_create (material .source_type ,material .source_name ,material .url )
            item =FetchedItem (
            external_id =material .id ,
            source_id =source .id ,
            source_type =material .source_type ,
            source_name =material .source_name ,
            title =material .title ,
            url =material .url ,
            text =material .text ,
            summary =summary ,
            tags =",".join (material .tags ),
            published_at =material .published_at ,
            relevance_score =float (classification_data .get ("relevance_score",0.0 )),
            classification =classification_data .get ("classification","travel_post"),
            raw_payload =self .aggregator .serialize_payload (material .raw_payload ),
            )
            await self .fetched_repo .create (item )
            stored .append (item )
        return stored
    async def generate_post_from_item (self ,fetched_item :FetchedItem ,user_id :int |None =None )->GeneratedPostBundle :
        material =Material (
        id =fetched_item .external_id ,
        source_type =fetched_item .source_type ,
        source_name =fetched_item .source_name ,
        title =fetched_item .title ,
        url =fetched_item .url ,
        text =fetched_item .text ,
        summary =fetched_item .summary ,
        relevance_score =fetched_item .relevance_score ,
        )
        bundle =await self .generator .generate_from_material (material ,fetched_item .classification or "travel_post")
        await self .generated_repo .create (
        user_id =user_id ,
        draft_id =None ,
        fetched_item_id =fetched_item .id ,
        format_type =bundle .format_type ,
        tone =bundle .tone ,
        title =bundle .title ,
        content =bundle .content ,
        short_version =bundle .short_version ,
        hashtags =bundle .hashtags ,
        cta =bundle .cta ,
        )
        return bundle