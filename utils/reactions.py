"""reactions constants (stores emojis)"""

from enum import Enum

class PageReaction(Enum):
    """
        Reactions for page Discord message
    """

    PREVIOUS = "⬅️"
    NEXT = "➡️"
    DELETE = "🗑️"

class Reactions(Enum):
    """
        Stores emojis for Discord messages reactions
    """

    _ignore_ = "merge_enum member cls merges"

    cls = vars()
    merges = (
        PageReaction,
    )
    
    for merge_enum in merges:
        merge_enum = list(merge_enum)

        for member in merge_enum:
            cls[member.name] = member.value

    LOADING = "⌛"

    def __str__(self):
        return self.value
