"""Small, fixed-host Suno client. Paid submission is never retried automatically."""

from __future__ import annotations

import json
import os
import time
from typing import Any
from urllib.parse import urlparse

import requests

BASE_URL = "https://api.acedata.cloud"
AUDIO_HOSTS = {"cdn.acedata.cloud", "cdn.acedata2.cloud"}
COMPLETE = {"complete", "completed", "succeed", "succeeded", "success", "finished"}
FAILED = {"failed", "error", "cancelled", "canceled", "rejected"}
MAX_AUDIO_BYTES = 64 * 1024 * 1024
AUDIO_MODELS = (
    "chirp-v6", "chirp-v6-wild", "chirp-v6-mini", "chirp-v5-5", "chirp-v5",
    "chirp-v4-5-plus", "chirp-v4-5", "chirp-v4", "chirp-v3-5", "chirp-v3-0",
)
LYRICS_MODELS = ("default", "remi-v1")


class SunoError(RuntimeError):
    """Public error that never includes a raw response, URL, or API key."""


def _credential() -> str:
    token = os.environ.get("ACEDATACLOUD_API_KEY") or os.environ.get("ACEDATACLOUD_API_TOKEN")
    if not token or not token.strip():
        raise SunoError("Set ACEDATACLOUD_API_KEY in the ComfyUI process environment and restart ComfyUI.")
    token = token.strip()
    if token.lower().startswith("bearer "):
        token = token[7:].strip()
    if not token:
        raise SunoError("Ace Data Cloud API key is empty.")
    return token


def _post(path: str, payload: dict[str, Any], *, read_only: bool = False) -> dict[str, Any]:
    token = _credential()
    for attempt in range(3 if read_only else 1):
        try:
            response = requests.post(
                BASE_URL + path,
                json=payload,
                headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
                timeout=(10, 60 if read_only else 45),
                allow_redirects=False,
            )
            break
        except requests.RequestException as exc:
            if read_only and attempt < 2:
                time.sleep(0.5 * (attempt + 1))
                continue
            if read_only:
                raise SunoError(
                    f"Suno query connection failed ({type(exc).__name__}). Retry the same task ID."
                ) from None
            raise SunoError(
                f"Suno submission connection failed ({type(exc).__name__}). "
                "Check request history before submitting another paid generation."
            ) from None
    if not 200 <= response.status_code < 300:
        raise SunoError(
            f"Ace Data Cloud returned HTTP {response.status_code}. "
            "Check key access, balance, and request history before retrying."
        )
    try:
        body = response.json()
    except ValueError:
        raise SunoError("Ace Data Cloud returned invalid JSON.") from None
    if not isinstance(body, dict):
        raise SunoError("Ace Data Cloud returned an unexpected response.")
    return body


def submit(prompt: str, model: str, instrumental: bool) -> tuple[str, str]:
    if not isinstance(prompt, str) or not prompt.strip() or len(prompt) > 500:
        raise ValueError("Prompt must contain 1 to 500 characters.")
    if model not in AUDIO_MODELS:
        raise ValueError("Unsupported Suno model.")
    body = _post(
        "/suno/audios",
        {"action": "generate", "prompt": prompt.strip(), "model": model,
         "instrumental": bool(instrumental), "async": True},
    )
    if body.get("success") is False or body.get("error"):
        raise SunoError("Suno rejected the request. Inspect request history before resubmitting.")
    task_id = body.get("task_id") or (
        body.get("task", {}).get("id") if isinstance(body.get("task"), dict) else None
    )
    if not isinstance(task_id, str) or not task_id:
        raise SunoError("No task ID was returned. Inspect request history before resubmitting.")
    return task_id, str(body.get("trace_id") or "")


def _public_lyrics(value: Any) -> Any:
    """Keep customer-facing lyric fields while excluding internal task data."""
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except ValueError:
            return value
    if isinstance(value, list):
        return [_public_lyrics(item) for item in value]
    if isinstance(value, dict):
        allowed = {"title", "lyric", "lyrics", "text", "status", "state", "data", "response", "content", "result"}
        return {key: _public_lyrics(item) for key, item in value.items() if key in allowed}
    return value if isinstance(value, (int, float, bool)) else None


def _has_lyric_text(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return any(_has_lyric_text(item) for item in value)
    if isinstance(value, dict):
        return any(_has_lyric_text(value[key]) for key in ("lyric", "lyrics", "text") if key in value) or any(
            _has_lyric_text(value[key]) for key in ("data", "response", "content", "result") if key in value
        )
    return False


def generate_lyrics(prompt: str, model: str) -> tuple[str, str, str, str]:
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("A lyrics prompt is required.")
    if model not in LYRICS_MODELS:
        raise ValueError("Unsupported Suno lyrics model.")
    body = _post("/suno/lyrics", {"prompt": prompt.strip(), "model": model})
    if body.get("success") is False or body.get("error"):
        raise SunoError("Suno rejected the lyrics request. Inspect request history before resubmitting.")
    task_id = body.get("task_id") or (body.get("task", {}).get("id") if isinstance(body.get("task"), dict) else "")
    trace_id = str(body.get("trace_id") or "")
    if task_id:
        return "pending", str(task_id), "", trace_id
    lyrics = _public_lyrics(body.get("data") or body.get("response") or body.get("result"))
    if not _has_lyric_text(lyrics):
        raise SunoError("No task ID or lyrics were returned. Inspect request history before resubmitting.")
    return "succeeded", "", json.dumps(lyrics, ensure_ascii=False), trace_id


def retrieve_lyrics_once(task_id: str) -> tuple[str, str, str, str]:
    if not isinstance(task_id, str) or not task_id.strip():
        raise ValueError("The Suno lyrics task ID is required.")
    task_id = task_id.strip()
    body = _post("/suno/tasks", {"action": "retrieve", "id": task_id}, read_only=True)
    if body.get("success") is False or body.get("error"):
        raise SunoError("Suno lyrics task lookup failed. Check the task ID and service access.")
    result = body.get("response", body)
    if isinstance(result, str):
        try:
            result = json.loads(result)
        except ValueError:
            result = {}
    if _state(result) == "failed":
        raise SunoError("Suno lyrics task failed. Inspect the task and trace ID in Ace Data Cloud.")
    trace_id = str(body.get("trace_id") or "")
    if "finished_at" in body and body["finished_at"] is None:
        return "pending", task_id, "", trace_id
    lyrics = _public_lyrics(result)
    if body.get("finished_at") or _state(result) == "succeeded":
        if not _has_lyric_text(lyrics):
            raise SunoError("Suno lyrics task finished without lyrics.")
        return "succeeded", task_id, json.dumps(lyrics, ensure_ascii=False), trace_id
    return "pending", task_id, "", trace_id


def _audio_urls(value: Any) -> list[str]:
    urls: list[str] = []

    def walk(item: Any) -> None:
        if isinstance(item, dict):
            audio = item.get("audio_url")
            if isinstance(audio, str) and audio.startswith("https://"):
                urls.append(audio)
            for child in item.values():
                if isinstance(child, (dict, list)):
                    walk(child)
        elif isinstance(item, list):
            for child in item:
                walk(child)

    walk(value)
    return list(dict.fromkeys(urls))


def _state(value: Any) -> str:
    states: list[str] = []

    def walk(item: Any) -> None:
        if isinstance(item, dict):
            if item.get("success") is False or item.get("error"):
                states.append("failed")
            for name, child in item.items():
                if name in {"status", "state"} and isinstance(child, str):
                    states.append(child.lower())
                elif name in {"data", "content", "task"} and isinstance(child, (dict, list)):
                    walk(child)
        elif isinstance(item, list):
            for child in item:
                walk(child)

    walk(value)
    if any(item in FAILED for item in states):
        return "failed"
    if states and all(item in COMPLETE for item in states):
        return "succeeded"
    return "pending"


def retrieve_once(task_id: str) -> tuple[str, str, str]:
    if not isinstance(task_id, str) or not task_id.strip():
        raise ValueError("The Suno task ID is required.")
    body = _post("/suno/tasks", {"action": "retrieve", "id": task_id.strip()}, read_only=True)
    if body.get("success") is False or body.get("error"):
        raise SunoError("Suno task lookup failed. Check the task ID and service access.")
    if "response" in body:
        result = body["response"]
        if isinstance(result, str):
            try:
                result = json.loads(result)
            except ValueError:
                result = {}
    else:
        result = body
    if result is None:
        result = {}
    state = _state(result)
    urls = _audio_urls(result)
    if state == "failed":
        raise SunoError("Suno task failed. Inspect the task and trace ID in Ace Data Cloud.")
    unfinished = "finished_at" in body and body["finished_at"] is None
    finished = bool(body.get("finished_at"))
    if unfinished:
        return "pending", "", str(body.get("trace_id") or "")
    if state == "succeeded" or finished or urls:
        if not urls:
            raise SunoError("Suno task finished without an audio URL. Inspect its task result.")
        return "succeeded", urls[0], str(body.get("trace_id") or "")
    return "pending", "", str(body.get("trace_id") or "")


def retrieve(task_id: str, wait_seconds: int) -> tuple[str, str, str]:
    if not isinstance(wait_seconds, int) or not 0 <= wait_seconds <= 240:
        raise ValueError("Wait seconds must be from 0 to 240.")
    deadline = time.monotonic() + wait_seconds
    while True:
        result = retrieve_once(task_id)
        if result[0] != "pending" or time.monotonic() >= deadline:
            return result
        time.sleep(min(5, max(0, deadline - time.monotonic())))


def download_audio(url: str) -> bytes:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in AUDIO_HOSTS or parsed.username or parsed.password:
        raise SunoError("Audio URL must be an Ace Data Cloud HTTPS media link.")
    for attempt in range(3):
        try:
            with requests.get(url, stream=True, timeout=(10, 60), allow_redirects=False) as response:
                if response.status_code != 200:
                    raise SunoError(f"Audio download returned HTTP {response.status_code}.")
                claimed = int(response.headers.get("Content-Length", "0"))
                if claimed > MAX_AUDIO_BYTES:
                    raise SunoError("Audio file exceeds the 64 MiB limit.")
                chunks: list[bytes] = []
                size = 0
                for chunk in response.iter_content(1024 * 1024):
                    size += len(chunk)
                    if size > MAX_AUDIO_BYTES:
                        raise SunoError("Audio file exceeds the 64 MiB limit.")
                    chunks.append(chunk)
            if not size:
                raise SunoError("Audio download was empty.")
            return b"".join(chunks)
        except requests.RequestException as exc:
            if attempt < 2:
                time.sleep(0.5 * (attempt + 1))
                continue
            raise SunoError(f"Audio download failed ({type(exc).__name__}).") from None
    raise AssertionError("Unreachable")
