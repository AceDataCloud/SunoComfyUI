"""Ace Data Cloud Suno nodes for ComfyUI."""

from .nodes import (AceSunoAudio, AceSunoGenerate, AceSunoGenerateLyrics,
                    AceSunoRetrieve, AceSunoRetrieveLyrics)

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

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
