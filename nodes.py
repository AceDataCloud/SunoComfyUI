"""ComfyUI graph nodes for submitting and retrieving Suno tasks."""

from __future__ import annotations

from io import BytesIO

from .client import (AUDIO_MODELS, LYRICS_MODELS, SunoError, download_audio,
                     generate_lyrics, retrieve, retrieve_lyrics_once, submit)



class _FreshTaskLookup:
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        # Task state changes remotely even when this graph's inputs do not.
        return float('nan')

class AceSunoGenerate:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "prompt": ("STRING", {"multiline": True, "default": "A gentle instrumental piano melody for a sunrise."}),
            "model": (list(AUDIO_MODELS), {"default": "chirp-v6"}),
            "instrumental": ("BOOLEAN", {"default": True}),
        }}

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("task_id", "trace_id")
    FUNCTION = "run"
    CATEGORY = "Ace Data Cloud/Suno"
    DESCRIPTION = "Submit one paid Suno music task. Copy the task ID and use Retrieve; never resubmit to poll."
    OUTPUT_NODE = True

    def run(self, prompt: str, model: str, instrumental: bool):
        task_id, trace_id = submit(prompt, model, instrumental)
        return {"ui": {"text": [f"Suno task ID: {task_id}", f"Trace ID: {trace_id}"]},
                "result": (task_id, trace_id)}


class AceSunoRetrieve(_FreshTaskLookup):
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "task_id": ("STRING", {"default": ""}),
            "wait_seconds": ("INT", {"default": 240, "min": 0, "max": 240, "step": 5}),
        }}

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("status", "task_id", "audio_url", "trace_id")
    FUNCTION = "run"
    CATEGORY = "Ace Data Cloud/Suno"
    DESCRIPTION = "Read the same Suno task. This query does not submit a new generation."
    OUTPUT_NODE = True

    def run(self, task_id: str, wait_seconds: int):
        status, audio_url, trace_id = retrieve(task_id, wait_seconds)
        return {"ui": {"text": [f"Suno status: {status}", f"Task ID: {task_id}",
                                "Audio is ready" if audio_url else "Query this task ID again later"]},
                "result": (status, task_id, audio_url, trace_id)}


class AceSunoGenerateLyrics:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "prompt": ("STRING", {"multiline": True, "default": "A hopeful song about finding a new home."}),
            "model": (list(LYRICS_MODELS), {"default": "default"}),
        }}

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("status", "task_id", "lyrics_json", "trace_id")
    FUNCTION = "run"
    CATEGORY = "Ace Data Cloud/Suno"
    DESCRIPTION = "Submit one Suno lyrics request. If a task ID is returned, use Retrieve Lyrics."
    OUTPUT_NODE = True

    def run(self, prompt: str, model: str):
        status, task_id, lyrics_json, trace_id = generate_lyrics(prompt, model)
        return {"ui": {"text": [f"Suno lyrics status: {status}", f"Task ID: {task_id or 'completed synchronously'}"]},
                "result": (status, task_id, lyrics_json, trace_id)}


class AceSunoRetrieveLyrics(_FreshTaskLookup):
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"task_id": ("STRING", {"default": ""})}}

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("status", "task_id", "lyrics_json", "trace_id")
    FUNCTION = "run"
    CATEGORY = "Ace Data Cloud/Suno"
    DESCRIPTION = "Read an existing lyrics task without submitting another paid request."
    OUTPUT_NODE = True

    def run(self, task_id: str):
        status, task_id, lyrics_json, trace_id = retrieve_lyrics_once(task_id)
        return {"ui": {"text": [f"Suno lyrics status: {status}", f"Task ID: {task_id}"]},
                "result": (status, task_id, lyrics_json, trace_id)}


class AceSunoAudio:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"audio_url": ("STRING", {"default": ""})}}

    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)
    FUNCTION = "run"
    CATEGORY = "Ace Data Cloud/Suno"
    DESCRIPTION = "Load a completed Suno audio link into ComfyUI's AUDIO type for Preview Audio or Save Audio."

    def run(self, audio_url: str):
        if not audio_url:
            raise SunoError("Task is still pending. Query the same task ID again; do not generate again.")
        import av
        import torch

        raw = download_audio(audio_url)
        with av.open(BytesIO(raw)) as container:
            if not container.streams.audio:
                raise SunoError("The media link contains no audio stream.")
            stream = container.streams.audio[0]
            sample_rate = stream.codec_context.sample_rate
            channels = stream.channels
            frames = []
            for frame in container.decode(streams=stream.index):
                samples = torch.from_numpy(frame.to_ndarray())
                if samples.shape[0] != channels:
                    samples = samples.view(-1, channels).t()
                if samples.dtype == torch.int16:
                    samples = samples.float() / (2 ** 15)
                elif samples.dtype == torch.int32:
                    samples = samples.float() / (2 ** 31)
                elif not samples.is_floating_point():
                    raise SunoError("Unsupported audio sample format.")
                frames.append(samples)
            if not frames:
                raise SunoError("The media link contains no audio frames.")
            waveform = torch.cat(frames, dim=1).unsqueeze(0)
            return ({"waveform": waveform, "sample_rate": sample_rate},)
