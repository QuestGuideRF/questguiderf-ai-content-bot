from __future__ import annotations
from content .prompts import PROMPTS ,SYSTEM_EDITOR
class PromptManager :
    def render (self ,key :str ,**kwargs :str )->tuple [str ,str ]:
        if key not in PROMPTS :
            raise KeyError (f"Unknown prompt key: {key }")
        return SYSTEM_EDITOR ,PROMPTS [key ].format (**kwargs )