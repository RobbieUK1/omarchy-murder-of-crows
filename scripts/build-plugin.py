#!/usr/bin/env python3
"""Patch a user-owned copy of the installed background plugin, failing closed."""
import argparse
import json
from pathlib import Path
import shutil


def build(source, output, scripts):
    text = (source / 'Background.qml').read_text()
    replacements = {
        'import QtQuick\n': 'import QtQuick\nimport "Randomize.js" as CrowRandom\n',
        '    target: "background"':
            '    target: "background"\n\n    function randomizerStatus(): string {\n      return JSON.stringify({assignments: root.monitorBackgrounds, screens: backgrounds.instances.map(function(panel) { return {name: panel.screen.name, path: panel.renderedPath, ready: panel.backgroundReady} })})\n    }',
        '      property bool maskReady: false':
            '      readonly property string renderedPath: root.monitorBackgrounds[panel.screen.name] || root.displayedBackground\n      property bool maskReady: false',
        '    function set(path: string): void {':
            '    function set(path: string): void {\n      root.requestShuffle()',
        '    function setInstant(path: string): void {':
            '    function setInstant(path: string): void {\n      root.requestShuffle()',
        '    function transition(fromPath: string, path: string): void {':
            '    function transition(fromPath: string, path: string): void {\n      root.requestShuffle()',
        '  function transitionBackgroundWithTheme(fromPath, path, finalPath, colorsB64, shellB64) {':
            '  function transitionBackgroundWithTheme(fromPath, path, finalPath, colorsB64, shellB64) {\n    requestShuffle()',
        '    var paths = [displayedBackground, incomingBackground, oldBackground, preparedBackground]':
            '    var paths = [displayedBackground, incomingBackground, oldBackground, preparedBackground].concat(Object.keys(monitorBackgrounds).map(function(name) { return monitorBackgrounds[name] }))',
        '  Component.onCompleted: refreshBackground()':
            '  Component.onCompleted: { refreshBackground(); requestShuffle() }',
        '        path: root.displayedBackground':
            '        path: root.monitorBackgrounds[panel.screen.name] || root.displayedBackground',
        '        decodeSize: panel.decodeSize(root.displayedBackground)':
            '        decodeSize: panel.decodeSize(base.path)',
        '        visible: root.oldBackground !== "" && root.revealProgress < 1':
            '        visible: !root.randomizing && root.oldBackground !== "" && root.revealProgress < 1',
        '        visible: root.incomingBackground !== "" && incomingFrame.status === Image.Ready && (root.revealProgress >= 1 || panel.maskReady)':
            '        visible: !root.randomizing && root.incomingBackground !== "" && incomingFrame.status === Image.Ready && (root.revealProgress >= 1 || panel.maskReady)',
    }
    for old, new in replacements.items():
        if text.count(old) != 1:
            raise ValueError('Unsupported Omarchy background plugin: expected one occurrence of ' + repr(old))
        text = text.replace(old, new)
    # Insert inside the root Item, retaining all stock IPC, theme and video logic.
    anchor = '  id: root\n'
    if text.count(anchor) != 1:
        raise ValueError('Unsupported root Item')
    text = text.replace(anchor, anchor + '\n' + (scripts / 'randomizer.qml.part').read_text())
    manifest = json.loads((source / 'manifest.json').read_text())
    if manifest.get('id') != 'omarchy.background':
        raise ValueError('Expected the stock omarchy.background plugin')
    manifest.update(id='crows.background', name='Murder of Crows Background')
    manifest['omarchy'] = {'clonedFrom': 'omarchy.background'}
    if output.exists():
        raise ValueError('Output already exists: ' + str(output))
    shutil.copytree(source, output)
    (output / 'Background.qml').write_text(text)
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    for name in ('Randomize.js', 'list-backgrounds.py'):
        shutil.copy2(scripts / name, output / name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    build(args.source, args.output, Path(__file__).resolve().parent)
