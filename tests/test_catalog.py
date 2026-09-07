"""Run this file directly in an IDE or discover with unittest."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

PROJECT = Path(__file__).resolve().parents[1]
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

from src.config import CatalogConfig
from src.exceptions import CatalogBuildError, InvalidCollectionError
from src.service import build_catalog


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'assets'
        self.root.mkdir()
        self.config = CatalogConfig(self.root)

    def idea(self, name='Κήπος', prompt='Ένας κήπος.\nSecond line.\n'):
        idea = self.root / name
        (idea / 'images').mkdir(parents=True)
        (idea / 'prompt.txt').write_text(prompt, encoding='utf-8-sig')
        # Scanner is extension-based, so these are deliberately byte fixtures.
        for filename in ['Image02.webp', 'Image01.PNG']:
            (idea / 'images' / filename).write_bytes(b'fixture')
        (idea / 'images' / 'notes.txt').write_text('ignored')
        return idea

    def test_multiple_ideas_preserve_prompt_paths_and_schema(self):
        self.idea()
        self.idea('Futuristic-Park')
        result = build_catalog(self.config)
        records = json.loads(result.output_file.read_text(encoding='utf-8'))
        self.assertEqual((result.artwork_count, result.image_count), (2, 4))
        self.assertEqual([a['title'] for a in records], ['Futuristic-Park', 'Κήπος'])
        for record in records:
            self.assertEqual(set(record), {'title', 'prompt', 'images'})
            self.assertEqual(record['prompt'], 'Ένας κήπος.\nSecond line.\n')
            self.assertTrue(all((self.root / p).is_file() for p in record['images'].values()))
        self.assertEqual(len({key for record in records for key in record['images']}), 4)

    def test_repeated_and_relocated_builds_are_identical(self):
        self.idea()
        build_catalog(self.config)
        first = self.config.output_file.read_bytes()
        build_catalog(self.config)
        self.assertEqual(first, self.config.output_file.read_bytes())
        relocated = self.root.parent / 'relocated'
        shutil.copytree(self.root, relocated)
        build_catalog(CatalogConfig(relocated))
        self.assertEqual(first, (relocated / 'artworks.json').read_bytes())

    def test_bad_inputs_preserve_existing_catalog(self):
        idea = self.idea()
        build_catalog(self.config)
        previous = self.config.output_file.read_bytes()
        for prompt in ['', '   \n', None]:
            with self.subTest(prompt=prompt):
                path = idea / 'prompt.txt'
                if prompt is None:
                    path.unlink()
                else:
                    path.write_text(prompt)
                with self.assertRaises(InvalidCollectionError):
                    build_catalog(self.config)
                self.assertEqual(previous, self.config.output_file.read_bytes())

    def test_empty_collection_and_empty_images_fail(self):
        with self.assertRaises(InvalidCollectionError):
            build_catalog(self.config)
        idea = self.idea()
        for path in (idea / 'images').iterdir():
            path.unlink()
        with self.assertRaises(InvalidCollectionError):
            build_catalog(self.config)
        self.assertFalse(self.config.output_file.exists())

    def test_failed_replace_preserves_catalog_and_cleans_temporary_file(self):
        self.idea()
        build_catalog(self.config)
        previous = self.config.output_file.read_bytes()
        with patch('genaiart.storage.os.replace', side_effect=PermissionError('locked')):
            with self.assertRaises(CatalogBuildError):
                build_catalog(self.config)
        self.assertEqual(previous, self.config.output_file.read_bytes())
        self.assertEqual(list(self.root.glob('.artworks-*.tmp')), [])

    def test_ide_entry_point_from_another_working_directory(self):
        self.idea()
        project = self.root.parent / 'project'
        project.mkdir()
        shutil.copytree(PROJECT / 'genaiart', project / 'genaiart')
        shutil.copytree(self.root, project / 'assets')
        shutil.copyfile(PROJECT / 'main.py', project / 'main.py')
        result = subprocess.run(
            [sys.executable, str(project / 'main.py')],
            cwd=self.root.parent, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((project / 'assets' / 'artworks.json').is_file())


if __name__ == '__main__':
    unittest.main()
