"""Check the installer artifact, including UCP's language-specific entry points."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import zipfile
import xml.etree.ElementTree as ET
from tools.package import build

# UCP3-GUI/resources/lang/languages.yaml (the launcher uses 'ch', not 'zh').
LANGUAGES = ('en', 'de', 'fr', 'ru', 'hu', 'tr', 'ch', 'es', 'fa')


class PackageTests(unittest.TestCase):
    def test_store_file_list_matches_preview_without_development_dependencies(self):
        source = Path(__file__).resolve().parents[1]
        members = set()
        for entry in ET.parse(source / 'files.xml').findall('./files/file'):
            files = list(source.glob(entry.attrib['src']))
            self.assertTrue(files, entry.attrib['src'])
            for file in files:
                self.assertTrue(file.is_file())
                members.add((Path(entry.get('target', '')) / file.name).as_posix())
        with tempfile.TemporaryDirectory() as temporary:
            with zipfile.ZipFile(build(Path(temporary))) as archive:
                self.assertEqual(members, set(archive.namelist()))
        self.assertIn('docs/compatibility.md', members)
        self.assertFalse(any(name.startswith(('tools/', 'tests/')) or name.endswith('.py')
                             for name in members))

    def test_release_contains_launcher_descriptions_and_instructions(self):
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            archive = build(destination)
            expected_hash = (destination / 'SHA256SUMS').read_text().split()[0]
            self.assertEqual(hashlib.sha256(archive.read_bytes()).hexdigest(), expected_hash)
            with zipfile.ZipFile(archive) as content:
                self.assertIsNone(content.testzip())
                root = ''
                for name in ('README.md', 'docs/testing.md', 'init.lua', 'definition.yml'):
                    self.assertGreater(len(content.read(root + name)), 20)
                for language in LANGUAGES:
                    with self.subTest(language=language):
                        description = content.read(root + f'locale/description-{language}.md').decode('utf-8')
                        self.assertTrue(description.startswith('# '))
                        self.assertIn('1.41', description)
                        self.assertIn('3.0.7', description)
                        self.assertNotIn('\ufffd', description)
                        # No configurable options: valid empty YAML mappings suffice.
                        self.assertEqual(json.loads(content.read(root + f'locale/{language}.yml')), {})
                self.assertIn('definition.yml', content.namelist())
                self.assertNotIn(archive.stem + '/definition.yml', content.namelist())
                self.assertFalse(any('/tests/' in name or name.endswith(('.exe', '.sav'))
                                     for name in content.namelist()))


if __name__ == '__main__':
    unittest.main()
