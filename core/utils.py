from __future__ import annotations
from datetime import datetime ,timezone
from typing import Iterable
def utc_now ()->datetime :
    return datetime .now (timezone .utc )
def trim_text (value :str ,limit :int =4000 )->str :
    if len (value )<=limit :
        return value
    return value [:limit -3 ].rstrip ()+"..."
def join_non_empty (parts :Iterable [str ],sep :str ="\n\n")->str :
    return sep .join (part .strip ()for part in parts if part and part .strip ())