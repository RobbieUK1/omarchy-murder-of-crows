import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


builder = load('builder', 'build-plugin.py')
scanner = load('scanner', 'list-backgrounds.py')


class PluginTests(unittest.TestCase):
    def test_theme_scope_files_and_symlinks(self):
        with tempfile.TemporaryDirectory() as folder:
            home = Path(folder)
            current = home / '.local/state/omarchy/current'
            images = current / 'theme/backgrounds'
            images.mkdir(parents=True)
            name = current / 'theme.name'
            name.write_text('murder-of-crows\n')
            image = images / 'a space # sunny.PNG'
            image.touch()
            (images / 'alias.png').symlink_to(image)
            (images / 'movie.mp4').touch()
            (images / 'directory.jpg').mkdir()
            extra = home / '.config/omarchy/backgrounds/murder-of-crows'
            extra.mkdir(parents=True)
            (extra / 'extra.webp').touch()
            self.assertEqual(len(scanner.backgrounds(home)), 2)
            self.assertIn(str(image), scanner.backgrounds(home))
            name.write_text('tokyo-night')
            self.assertEqual(scanner.backgrounds(home), [])
            name.unlink()
            self.assertEqual(scanner.backgrounds(home), [])

    def test_unsupported_source_does_not_write(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'source'
            source.mkdir()
            (source / 'Background.qml').write_text('Item {}')
            output = Path(folder) / 'output'
            with self.assertRaises(ValueError):
                builder.build(source, output, SCRIPTS)
            self.assertFalse(output.exists())

    def test_installed_source_build(self):
        source = Path('/usr/share/omarchy/shell/plugins/background')
        if not source.exists():
            self.skipTest('No local Omarchy shell source')
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / 'plugin'
            builder.build(source, output, SCRIPTS)
            manifest = json.loads((output / 'manifest.json').read_text())
            self.assertEqual(manifest['omarchy']['clonedFrom'], 'omarchy.background')
            self.assertEqual(manifest['id'], 'crows.background')
            self.assertTrue((output / 'Randomize.js').exists())


if __name__ == '__main__':
    unittest.main()
