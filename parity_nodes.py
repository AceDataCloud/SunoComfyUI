"""Schema-backed ComfyUI nodes for the current SunoDify catalog.

Model and action selectors are first-class. Remaining Dify parameters use JSON,
which is validated by the copied published API contract before any request.
"""

from __future__ import annotations

import json
import os

from .dify_contracts import ENDPOINTS

from .dify_client import AceDataSunoClient

SERVICE = 'Suno'
MEDIA_TYPES = ()
TOOL_SPECS = {'suno_create_persona': {'models': [],
                         'actions': [],
                         'operation': 'request',
                         'label': 'Suno Create Persona',
                         'description': 'Create Persona through the Ace Data Cloud Suno API.',
                         'required': ['name', 'audio_id'],
                         'fields': ['name',
                                    'audio_id',
                                    'vox_audio_id',
                                    'vocal_start',
                                    'vocal_end',
                                    'description']},
 'suno_create_voice': {'models': [],
                       'actions': [],
                       'operation': 'request',
                       'label': 'Suno Create Voice',
                       'description': 'Create Voice through the Ace Data Cloud Suno API.',
                       'required': ['audio_url'],
                       'fields': ['audio_url', 'name', 'description']},
 'suno_create_vox_audio': {'models': [],
                           'actions': [],
                           'operation': 'request',
                           'label': 'Suno Create Vox Audio',
                           'description': 'Create Vox Audio through the Ace Data Cloud Suno API.',
                           'required': ['audio_id', 'vocal_start', 'vocal_end'],
                           'fields': ['audio_id', 'vocal_start', 'vocal_end', 'callback_url']},
 'suno_custom_models': {'models': [],
                        'actions': ['create', 'generate', 'retrieve', 'retrieve_batch', 'delete'],
                        'operation': 'request',
                        'label': 'Suno Custom Models',
                        'description': 'Custom Models through the Ace Data Cloud Suno API.',
                        'required': [],
                        'fields': ['name',
                                   'audio_urls',
                                   'callback_url',
                                   'id',
                                   'lyric',
                                   'lyric_prompt',
                                   'style',
                                   'negative_tags',
                                   'title',
                                   'instrumental',
                                   'vocal_gender',
                                   'weirdness',
                                   'style_influence',
                                   'duration',
                                   'limit',
                                   'offset',
                                   'status',
                                   'idempotency_key',
                                   'confirm']},
 'suno_delete_persona': {'models': [],
                         'actions': [],
                         'operation': 'request',
                         'label': 'Suno Delete Persona',
                         'description': 'Delete Persona through the Ace Data Cloud Suno API.',
                         'required': ['persona_id'],
                         'fields': ['persona_id', 'user_id', 'confirm']},
 'suno_enhance_style': {'models': [],
                        'actions': [],
                        'operation': 'request',
                        'label': 'Suno Enhance Style',
                        'description': 'Enhance Style through the Ace Data Cloud Suno API.',
                        'required': ['prompt'],
                        'fields': ['prompt']},
 'suno_generate_audios': {'models': ['chirp-v6',
                                     'chirp-v6-wild',
                                     'chirp-v6-mini',
                                     'chirp-v5-5',
                                     'chirp-v5',
                                     'chirp-v4-5-plus',
                                     'chirp-v4-5',
                                     'chirp-v4',
                                     'chirp-v3-5',
                                     'chirp-v3-0'],
                          'actions': ['generate',
                                      'extend',
                                      'upload_extend',
                                      'upload_cover',
                                      'concat',
                                      'cover',
                                      'artist_consistency',
                                      'artist_consistency_vox',
                                      'stems',
                                      'all_stems',
                                      'add_stem',
                                      'extract_stem',
                                      'sounds',
                                      'adjust_speed',
                                      'replace_section',
                                      'underpainting',
                                      'overpainting',
                                      'remaster',
                                      'mashup',
                                      'samples',
                                      'inspo'],
                          'operation': 'generate',
                          'label': 'Suno Generate Audios',
                          'description': 'Generate songs with Ace Data Cloud Suno Audios API.',
                          'required': [],
                          'fields': ['lyric',
                                     'max_mode',
                                     'variety',
                                     'style',
                                     'variation_category',
                                     'title',
                                     'custom',
                                     'prompt',
                                     'lyric_prompt',
                                     'audio_id',
                                     'stem_type',
                                     'audio_format',
                                     'sound',
                                     'sound_type',
                                     'bpm',
                                     'key',
                                     'speed_multiplier',
                                     'keep_pitch',
                                     'mashup_audio_ids',
                                     'audio_urls',
                                     'weirdness',
                                     'persona_id',
                                     'overpainting_start',
                                     'overpainting_end',
                                     'samples_start',
                                     'samples_end',
                                     'underpainting_start',
                                     'underpainting_end',
                                     'continue_at',
                                     'callback_url',
                                     'instrumental',
                                     'vocal_gender',
                                     'negative_tags',
                                     'style_influence',
                                     'audio_weight',
                                     'duration',
                                     'replace_section_end',
                                     'replace_section_result_mode',
                                     'replace_section_start']},
 'suno_generate_lyrics': {'models': ['default', 'remi-v1'],
                          'actions': [],
                          'operation': 'request',
                          'label': 'Suno Generate Lyrics',
                          'description': 'Generate Lyrics through the Ace Data Cloud Suno API.',
                          'required': ['prompt'],
                          'fields': ['prompt']},
 'suno_get_midi': {'models': [],
                   'actions': [],
                   'operation': 'request',
                   'label': 'Suno Get Midi',
                   'description': 'Get Midi through the Ace Data Cloud Suno API.',
                   'required': ['audio_id'],
                   'fields': ['audio_id', 'callback_url']},
 'suno_get_mp3': {'models': [],
                  'actions': [],
                  'operation': 'request',
                  'label': 'Suno Get Mp3',
                  'description': 'Get Mp3 through the Ace Data Cloud Suno API.',
                  'required': ['audio_id'],
                  'fields': ['audio_id', 'callback_url']},
 'suno_get_mp4': {'models': [],
                  'actions': [],
                  'operation': 'request',
                  'label': 'Suno Get Mp4',
                  'description': 'Get Mp4 through the Ace Data Cloud Suno API.',
                  'required': ['audio_id'],
                  'fields': ['audio_id']},
 'suno_get_timing': {'models': [],
                     'actions': [],
                     'operation': 'request',
                     'label': 'Suno Get Timing',
                     'description': 'Get Timing through the Ace Data Cloud Suno API.',
                     'required': ['audio_id'],
                     'fields': ['audio_id']},
 'suno_get_wav': {'models': [],
                  'actions': [],
                  'operation': 'request',
                  'label': 'Suno Get Wav',
                  'description': 'Get Wav through the Ace Data Cloud Suno API.',
                  'required': ['audio_id'],
                  'fields': ['audio_id', 'callback_url']},
 'suno_list_personas': {'models': [],
                        'actions': [],
                        'operation': 'request',
                        'label': 'Suno List Personas',
                        'description': 'List Personas through the Ace Data Cloud Suno API.',
                        'required': ['user_id'],
                        'fields': ['user_id', 'limit', 'offset']},
 'suno_mashup_lyrics': {'models': [],
                        'actions': [],
                        'operation': 'request',
                        'label': 'Suno Mashup Lyrics',
                        'description': 'Mashup Lyrics through the Ace Data Cloud Suno API.',
                        'required': ['lyrics_a', 'lyrics_b'],
                        'fields': ['lyrics_a', 'lyrics_b']},
 'suno_projects': {'models': ['chirp-v3-5',
                              'chirp-v4',
                              'chirp-v4-5',
                              'chirp-v4-5-plus',
                              'chirp-v5',
                              'chirp-v5-5',
                              'chirp-v6',
                              'chirp-v6-wild',
                              'chirp-v6-mini'],
                   'actions': ['create',
                               'retrieve',
                               'save',
                               'upload',
                               'add_track',
                               'generate_track',
                               'replace_section',
                               'commit_candidate',
                               'remove_track',
                               'render'],
                   'operation': 'request',
                   'label': 'Suno Projects',
                   'description': 'Projects through the Ace Data Cloud Suno API.',
                   'required': [],
                   'fields': ['title',
                              'id',
                              'version_id',
                              'state',
                              'audio_url',
                              'callback_url',
                              'audio_id',
                              'name',
                              'start_beats',
                              'end_beats',
                              'gain',
                              'source_audio_id',
                              'tags',
                              'prompt',
                              'start_seconds',
                              'end_seconds',
                              'render_audio_id',
                              'stem_control_tags',
                              'batch_size',
                              'replacement_lyrics',
                              'fixed',
                              'operation_id',
                              'candidate_id',
                              'track_id',
                              'lyrics',
                              'idempotency_key']},
 'suno_task_retrieve': {'models': [],
                        'actions': [],
                        'operation': 'task',
                        'label': 'Suno Retrieve Task',
                        'description': 'Retrieve one task, optionally waiting up to 240 seconds.',
                        'required': ['task_id'],
                        'fields': []},
 'suno_tasks_retrieve_batch': {'models': [],
                               'actions': [],
                               'operation': 'batch',
                               'label': 'Suno Retrieve Tasks',
                               'description': 'Retrieve existing tasks by ID without repeating '
                                              'generation.',
                               'required': ['ids'],
                               'fields': []},
 'suno_upload_reference_audio': {'models': [],
                                 'actions': [],
                                 'operation': 'request',
                                 'label': 'Suno Upload Reference Audio',
                                 'description': 'Upload Reference Audio through the Ace Data Cloud Suno '
                                                'API.',
                                 'required': ['audio_url'],
                                 'fields': ['audio_url', 'mode', 'name', 'callback_url']}}
SENTINEL = '(from JSON/default)'


def _credential() -> str:
    token = os.environ.get('ACEDATACLOUD_API_KEY') or os.environ.get('ACEDATACLOUD_API_TOKEN')
    if not token or not token.strip():
        raise RuntimeError('Set ACEDATACLOUD_API_KEY in the ComfyUI process environment and restart.')
    return token.strip()


def _is_read_only_lookup(tool, parameters):
    endpoint = ENDPOINTS[tool]
    if endpoint.get('selector'):
        action = parameters.get('action', endpoint.get('selector_default'))
        selected = endpoint['selector'].get(action) if isinstance(action, str) else None
        if not selected:
            return False
        endpoint = ENDPOINTS[selected]
    values = {**endpoint.get('defaults', {}), **parameters, **endpoint.get('fixed', {})}
    return bool(endpoint.get('operation') in {'task', 'batch'}
                or endpoint['method'] == 'GET' or endpoint.get('read_only', False)
                or ('action' in endpoint.get('properties', {})
                    and values.get('action') in endpoint.get('query_actions', [])))


class _ToolNode:
    RETURN_TYPES = ('STRING', 'STRING', 'STRING', 'STRING', 'STRING', 'STRING')
    RETURN_NAMES = ('status', 'task_id', 'media_urls_json', 'first_media_url', 'result_json', 'trace_id')
    FUNCTION = 'run'
    CATEGORY = 'Ace Data Cloud/' + SERVICE
    OUTPUT_NODE = True

    @classmethod
    def INPUT_TYPES(cls):
        spec = cls.SPEC
        required = {'parameters_json': ('STRING', {'multiline': True, 'default': '{}'})}
        if spec['models']:
            required['model'] = ([SENTINEL, *spec['models']], {'default': SENTINEL})
        if spec['actions']:
            required['action'] = ([SENTINEL, *spec['actions']], {'default': SENTINEL})
        for name in spec['fields']:
            if name == 'confirm':
                required[name] = ('BOOLEAN', {'default': False})
            else:
                required[name] = ('STRING', {'multiline': name in {'prompt', 'lyric', 'lyrics',
                    'image_urls', 'audio_urls', 'video_urls', 'negative_prompt'} or name.endswith('_json'),
                    'default': ''})
        if spec['operation'] == 'task':
            required['task_id'] = ('STRING', {'default': ''})
            required['wait_seconds'] = ('INT', {'default': 0, 'min': 0, 'max': 240})
        if spec['operation'] == 'batch':
            required['ids_json'] = ('STRING', {'multiline': True, 'default': ''})
        return {'required': required}

    @classmethod
    def IS_CHANGED(cls, parameters_json='{}', action=SENTINEL, **kwargs):
        # Pure cache policy: never authenticate or make a request here.
        endpoint = ENDPOINTS[cls.TOOL]
        allowed_actions = endpoint.get('properties', {}).get('action', {}).get('enum', [])
        always_query = (endpoint.get('operation') in {'task', 'batch'}
                        or endpoint['method'] == 'GET' or endpoint.get('read_only', False)
                        or (bool(allowed_actions) and set(allowed_actions).issubset(endpoint.get('query_actions', []))))
        # Linked JSON/actions are unavailable while fingerprints are computed.
        # Unknown mixed operations must stay cacheable to avoid paid replays.
        if not always_query and (parameters_json is None
                                 or (action is None and cls.SPEC.get('actions'))):
            return False
        try:
            parameters = json.loads(parameters_json) if parameters_json is not None else {}
        except (TypeError, ValueError):
            return False
        if not isinstance(parameters, dict):
            return False
        if action is not None and action != SENTINEL:
            parameters['action'] = action
        # Paid/destructive/unknown actions retain stable caching. Only declared
        # read-only operations bypass stale outputs on an unchanged graph.
        return float('nan') if _is_read_only_lookup(cls.TOOL, parameters) else False

    def run(self, parameters_json: str, model: str = SENTINEL, action: str = SENTINEL,
            task_id: str = '', wait_seconds: int = 0, ids_json: str = '', **fields):
        try:
            parameters = json.loads(parameters_json)
        except (TypeError, ValueError):
            raise ValueError('parameters_json must contain a JSON object.') from None
        if not isinstance(parameters, dict):
            raise ValueError('parameters_json must contain a JSON object.')
        if model != SENTINEL:
            parameters['model'] = model
        if action != SENTINEL:
            parameters['action'] = action
        for name, value in fields.items():
            if value is not None and value != '':
                parameters[name] = value
        if task_id.strip():
            parameters['task_id'] = task_id.strip()
        if self.SPEC['operation'] == 'task':
            parameters['wait_seconds'] = wait_seconds
        if ids_json.strip():
            try:
                ids = json.loads(ids_json)
            except ValueError:
                raise ValueError('ids_json must be a JSON array of task IDs.') from None
            if not isinstance(ids, list) or not ids:
                raise ValueError('ids_json must be a nonempty JSON array of task IDs.')
            parameters['ids'] = ids
        result = AceDataSunoClient(_credential()).invoke(self.TOOL, parameters)
        urls = result.get('media_urls') or []
        if not isinstance(urls, list):
            urls = []
        status = str(result.get('status') or 'unknown')
        resolved_task_id = str(result.get('task_id') or '')
        trace_id = str(result.get('trace_id') or '')
        return {
            'ui': {'text': [f'{SERVICE} status: {status}',
                            f'Task ID: {resolved_task_id or "completed synchronously"}',
                            f'Media URLs: {len(urls)}']},
            'result': (status, resolved_task_id, json.dumps(urls), urls[0] if urls else '',
                       json.dumps(result, ensure_ascii=False, default=str), trace_id),
        }


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
for tool, spec in TOOL_SPECS.items():
    class_name = 'Ace' + ''.join(part.title() for part in SERVICE.split()) + ''.join(
        part.title() for part in tool.split('_')
    )
    node = type(class_name, (_ToolNode,), {'TOOL': tool, 'SPEC': spec,
                                          'DESCRIPTION': spec['description']})
    NODE_CLASS_MAPPINGS[class_name] = node
    NODE_DISPLAY_NAME_MAPPINGS[class_name] = spec['label'] + ' (Ace Data Cloud)'


if MEDIA_TYPES:
    from .media import as_audio, as_image, as_video, download_media


class _LoadImage:
    RETURN_TYPES = ('IMAGE',)
    RETURN_NAMES = ('image',)
    FUNCTION = 'run'
    CATEGORY = 'Ace Data Cloud/' + SERVICE
    DESCRIPTION = 'Load a completed Ace CDN image into ComfyUI IMAGE.'

    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {'media_url': ('STRING', {'default': ''})}}

    def run(self, media_url: str):
        if not media_url:
            raise ValueError('Task is pending; retrieve the same task ID again.')
        return (as_image(download_media(media_url)),)


class _LoadVideo:
    RETURN_TYPES = ('VIDEO',)
    RETURN_NAMES = ('video',)
    FUNCTION = 'run'
    CATEGORY = 'Ace Data Cloud/' + SERVICE
    DESCRIPTION = 'Load a completed Ace CDN video into native ComfyUI VIDEO.'

    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {'media_url': ('STRING', {'default': ''})}}

    def run(self, media_url: str):
        if not media_url:
            raise ValueError('Task is pending; retrieve the same task ID again.')
        return (as_video(download_media(media_url)),)


class _LoadAudio:
    RETURN_TYPES = ('AUDIO',)
    RETURN_NAMES = ('audio',)
    FUNCTION = 'run'
    CATEGORY = 'Ace Data Cloud/' + SERVICE
    DESCRIPTION = 'Load a completed Ace CDN audio file into ComfyUI AUDIO.'

    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {'media_url': ('STRING', {'default': ''})}}

    def run(self, media_url: str):
        if not media_url:
            raise ValueError('Task is pending; retrieve the same task ID again.')
        return (as_audio(download_media(media_url)),)


for media_type, base in {'IMAGE': _LoadImage, 'VIDEO': _LoadVideo, 'AUDIO': _LoadAudio}.items():
    if media_type in MEDIA_TYPES:
        class_name = 'Ace' + ''.join(part.title() for part in SERVICE.split()) + 'Load' + media_type.title()
        NODE_CLASS_MAPPINGS[class_name] = type(class_name, (base,), {})
        NODE_DISPLAY_NAME_MAPPINGS[class_name] = SERVICE + ' Load ' + media_type.title() + ' (Ace Data Cloud)'

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'TOOL_SPECS']
