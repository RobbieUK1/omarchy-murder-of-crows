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
            marker = current / 'theme/wallpaper-randomizer.json'
            marker.write_text('{"version": 1, "enabled": true}')
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
            marker.unlink()
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


class SetupTests(unittest.TestCase):
    def test_setup_migrates_previous_renderer_and_restore(self):
        from unittest.mock import patch
        installer = load('installer', 'install-theme.py')
        with tempfile.TemporaryDirectory() as folder:
            home = Path(folder) / 'home'
            root = Path(folder) / 'checkout'
            (root / 'backgrounds').mkdir(parents=True)
            (root / 'backgrounds/test.png').touch()
            (root / 'wallpaper-randomizer.json').write_text('{"version":1,"enabled":true}')
            config = home / '.config/omarchy'
            sunny = config / 'plugins/sunnyoled.background'
            sunny.mkdir(parents=True)
            (sunny / 'manifest.json').write_text('{"omarchy":{"clonedFrom":"omarchy.background"}}')
            (config / 'themes/sunny-oled').mkdir(parents=True)
            (config / 'shell.json').write_text('{"plugins":[{"id":"sunnyoled.background"}]}')
            calls = []
            def fake_run(*args):
                calls.append(args)
                return '[{"id":"crows.background"}]' if args[-1] == '--json' else 'ok'
            with patch.object(installer.Path, 'home', return_value=home), patch.object(installer, 'ROOT', root), patch.object(installer, 'run', side_effect=fake_run):
                installer.main()
                self.assertTrue((config / 'themes/murder-of-crows/wallpaper-randomizer.json').exists())
                self.assertTrue((config / 'themes/sunny-oled/wallpaper-randomizer.json').exists())
                self.assertIn(('omarchy', 'plugin', 'disable', 'sunnyoled.background'), calls)
                self.assertIn(('omarchy', 'plugin', 'enable', 'crows.background'), calls)
                self.assertIn(('omarchy', 'theme', 'set', 'murder-of-crows'), calls)
                installer.main(remove=True)
                self.assertIn(('omarchy', 'plugin', 'enable', 'sunnyoled.background'), calls)


if __name__ == '__main__':
    unittest.main()
