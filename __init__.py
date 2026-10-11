"""Ace Data Cloud Suno nodes for ComfyUI."""

from .nodes import AceSunoAudio, AceSunoGenerate, AceSunoRetrieve

NODE_CLASS_MAPPINGS = {
    "AceSunoGenerate": AceSunoGenerate,
    "AceSunoRetrieve": AceSunoRetrieve,
    "AceSunoAudio": AceSunoAudio,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AceSunoGenerate": "Suno Submit Music (Ace Data Cloud)",
    "AceSunoRetrieve": "Suno Retrieve Task (Ace Data Cloud)",
    "AceSunoAudio": "Suno Load Audio (Ace Data Cloud)",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
