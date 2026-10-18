"""Comfy cache contract: same task refreshes; paid inputs do not replay."""
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
NAME = 'cache_policy_package'
spec = importlib.util.spec_from_file_location(NAME, ROOT / '__init__.py', submodule_search_locations=[str(ROOT)])
package = importlib.util.module_from_spec(spec)
sys.modules[NAME] = package
spec.loader.exec_module(package)
QUERIES = ['AceSunoRetrieve', 'AceSunoRetrieveLyrics', 'AceSunoSunoTaskRetrieve', 'AceSunoSunoTasksRetrieveBatch']
PAID = ['AceSunoGenerate', 'AceSunoGenerateLyrics', 'AceSunoSunoGenerateAudios']

def fingerprint(cls, **values):
    method = getattr(cls, 'IS_CHANGED', None)
    return method(**values) if method else False

class CachePolicyTests(unittest.TestCase):
    def test_unchanged_task_refreshes_while_paid_submissions_keep_stable_cache(self):
        for name in QUERIES:
            cls = package.NODE_CLASS_MAPPINGS[name]
            with self.subTest(node=name):
                self.assertNotEqual(fingerprint(cls, task_id='same-task', wait_seconds=240), fingerprint(cls, task_id='same-task', wait_seconds=240))
        for name in PAID:
            cls = package.NODE_CLASS_MAPPINGS[name]
            with self.subTest(node=name):
                self.assertEqual(fingerprint(cls), fingerprint(cls))

    def test_cache_fingerprints_never_authenticate_or_call_transport(self):
        with patch('requests.request', side_effect=AssertionError('cache must not request HTTP')) as transport:
            for name in QUERIES + PAID:
                fingerprint(package.NODE_CLASS_MAPPINGS[name])
        transport.assert_not_called()

    def test_mixed_action_keeps_paid_create_stable_but_refreshes_retrieve(self):
        cls = package.NODE_CLASS_MAPPINGS['AceSunoSunoCustomModels']
        self.assertEqual(fingerprint(cls, action='create'), fingerprint(cls, action='create'))
        self.assertNotEqual(fingerprint(cls, action='retrieve'), fingerprint(cls, action='retrieve'))
        self.assertNotEqual(fingerprint(cls, parameters_json='{"action":"retrieve"}'), fingerprint(cls, parameters_json='{"action":"retrieve"}'))

    def test_unknown_mixed_inputs_and_unrecognized_action_never_force_paid_replay(self):
        cls = package.NODE_CLASS_MAPPINGS['AceSunoSunoCustomModels']
        self.assertEqual(fingerprint(cls, parameters_json=None), fingerprint(cls, parameters_json=None))
        self.assertEqual(fingerprint(cls, parameters_json='{"action":"retrieve"}', action=None), fingerprint(cls, parameters_json='{"action":"retrieve"}', action=None))
        voice = package.NODE_CLASS_MAPPINGS['AceSunoSunoCreateVoice']
        self.assertEqual(fingerprint(voice, parameters_json='{"action":"retrieve"}'), fingerprint(voice, parameters_json='{"action":"retrieve"}'))
