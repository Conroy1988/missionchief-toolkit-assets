"""Ensure extension audio registration remains fail-closed."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from check_audio_alias_contract import validate_repository


class PackagedAudioTests(unittest.TestCase):
    def check_case(self, mutation=None):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'source.js').write_text(
                "'https://raw.githubusercontent.com/Conroy1988/missionchief-toolkit-assets/main/legacy.mp3'"
            )
            (root / 'legacy.mp3').write_bytes(b'legacy audio')
            (root / 'packaged.mp3').write_bytes(b'submitted audio')
            contract = {
                'schemaVersion': 1, 'canonicalSource': 'source.js',
                'canonicalAudioPaths': ['legacy.mp3'], 'aliases': [],
                'packagedAudioPaths': {'packaged.mp3': hashlib.sha256(b'submitted audio').hexdigest()},
            }
            if mutation:
                mutation(root, contract)
            path = root / 'contract.json'
            path.write_text(json.dumps(contract))
            return {f['code'] for f in validate_repository(root, path)['failures']}

    def test_registered_payload_passes(self):
        self.assertEqual(self.check_case(), set())

    def test_changed_payload_fails(self):
        self.assertIn('packaged-audio-hash-mismatch', self.check_case(
            lambda root, _: (root / 'packaged.mp3').write_bytes(b'changed')))

    def test_missing_payload_fails(self):
        self.assertIn('missing-packaged-audio', self.check_case(
            lambda root, _: (root / 'packaged.mp3').unlink()))

    def test_unregistered_payload_fails(self):
        self.assertIn('undeclared-audio-path', self.check_case(
            lambda root, _: (root / 'unexpected.mp3').write_bytes(b'new')))

    def test_invalid_digest_fails(self):
        self.assertIn('contract-schema-error', self.check_case(
            lambda _, contract: contract['packagedAudioPaths'].update({'packaged.mp3': '*'})))


if __name__ == '__main__':
    unittest.main()
