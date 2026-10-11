"""Ace Data Cloud Suno nodes for ComfyUI."""

from .nodes import (AceSunoAudio, AceSunoGenerate, AceSunoGenerateLyrics,
                    AceSunoRetrieve, AceSunoRetrieveLyrics)
from .parity_nodes import (NODE_CLASS_MAPPINGS as DIFY_NODE_CLASS_MAPPINGS,
                           NODE_DISPLAY_NAME_MAPPINGS as DIFY_NODE_DISPLAY_NAME_MAPPINGS)

NODE_CLASS_MAPPINGS = {
    "AceSunoGenerate": AceSunoGenerate,
    "AceSunoRetrieve": AceSunoRetrieve,
    "AceSunoAudio": AceSunoAudio,
    "AceSunoGenerateLyrics": AceSunoGenerateLyrics,
    "AceSunoRetrieveLyrics": AceSunoRetrieveLyrics,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AceSunoGenerate": "Suno Submit Music (Ace Data Cloud)",
    "AceSunoRetrieve": "Suno Retrieve Task (Ace Data Cloud)",
    "AceSunoAudio": "Suno Load Audio (Ace Data Cloud)",
    "AceSunoGenerateLyrics": "Suno Generate Lyrics (Ace Data Cloud)",
    "AceSunoRetrieveLyrics": "Suno Retrieve Lyrics (Ace Data Cloud)",
}

NODE_CLASS_MAPPINGS.update(DIFY_NODE_CLASS_MAPPINGS)
NODE_DISPLAY_NAME_MAPPINGS.update(DIFY_NODE_DISPLAY_NAME_MAPPINGS)

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
