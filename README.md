# Murder of Crows

A true-black OLED Omarchy theme with pure `#000000` interface backgrounds, ash text, and cool pewter accents. Eleven original crow wallpapers pair atmospheric wildlife photography with mist, weathered stone, and quiet landscapes.

![Solitude](backgrounds/01-solitude.png)

## Install the complete theme

```sh
git clone https://github.com/RobbieUK1/omarchy-murder-of-crows.git
cd omarchy-murder-of-crows
bash install.sh
```

This single setup installs the theme, activates it, and enables its built-in
multi-monitor wallpaper behavior. Requires the current Omarchy Quickshell shell
and Python 3. The standard `omarchy theme install` command only installs static
theme files; Omarchy does not execute a theme's setup scripts automatically.
Use the setup above for the complete theme experience.

Already have a checkout? Update it, then run `bash install.sh` again.

## Wallpapers

Open the background picker with **Super + Ctrl + Space**, or cycle from a terminal:

```sh
omarchy theme bg next
```

| Wallpaper | Scene |
| --- | --- |
| 01 · Solitude | A lone crow above a misty forest valley |
| 02 · Companions | A pair of crows |
| 03 · The Murder | A loose flock in charcoal mist |
| 04 · The Sentinel | A crow on a weathered stone gatepost |
| 05 · Blackwater | A crow reflected at a still lake |
| 06 · Wings of Ash | A crow gliding over a fog-filled valley |
| 07 · Winter Watch | Two crows on frost-covered branches |
| 08 · The Roost | Crows in a skeletal oak |
| 09 · Rainkeeper | A rain-soaked crow on a slate rooftop |
| 10 · Stone and Feather | A crow on a ruined stone arch |
| 11 · Last Light | Three crows on a moorland fence |

## Palette

- Background: `#000000` (true OLED black)
- Dark and darker backgrounds: `#000000`
- Raised surfaces: `#202329` (for visual separation)
- Foreground: `#d6d8de`
- Accent: `#b5bdc9`
- Selection: `#323740`

Omarchy generates supported application configurations from `colors.toml`. The theme includes the `Yaru-blue` icon preference.

## Artwork

Created with the built-in imagegen tool. The original prompt set used widescreen gothic wildlife fine-art photography: a solitary crow on a bare branch, a pair, and a loose flying flock. All use charcoal blacks, faint cool pewter highlights, and generous negative space.

The eight additional prompts are recorded in [PROMPTS.md](PROMPTS.md). Each image was generated separately for this collection.

## Built-in independent wallpapers per monitor

Use the usual **Super + Ctrl + Space** picker or `omarchy theme bg next`.
Confirming an image reshuffles all connected displays, even when confirming
the same image again. The clicked image is the trigger, not a pinned display
choice. Canceling keeps the arrangement. Connecting or disconnecting a monitor
also reshuffles it.

The pool includes theme stills and images in
`~/.config/omarchy/backgrounds/murder-of-crows/`. Distinct images are used across
monitors when enough exist, and each monitor changes its image whenever possible.
Videos are excluded from the pool. The picker's selected image remains the normal
current-background link for lock screens and other tools.

The theme ships `wallpaper-randomizer.json` and its renderer integration as part
of the same package. Setup builds a user-owned renderer from your installed
Omarchy version, retaining stock IPC, click handling and theme colors. Themes
without this settings file use stock behavior. Randomized stills change directly.
No palette, wallpaper artwork or packaged Omarchy files are modified.

Setup migrates the known Sunny OLED/PU renderer automatically and enables its
working theme through the same shared renderer, retaining the previous plugin
for restoration. Other custom renderer conflicts stop setup with an explanation.
User configuration and any replaced theme/plugin are backed up under
`~/.local/state/omarchy/backups/`. Re-run setup after Omarchy renderer updates.
Unsupported source layouts fail before user configuration changes.

To disable the built-in integration and restore the previous renderer:

```sh
bash install.sh --remove
```

The theme and its wallpapers remain installed.

### Development checks

```sh
node tests/randomize.test.cjs
python3 -B -m unittest discover -s tests -v
bash -n install.sh scripts/install-randomizer.sh
```

Tests cover repeated independent assignment, no avoidable duplicates/repeats,
monitor-list changes, empty/single/short image pools, theme settings, filename
handling, source compatibility, integrated installation, renderer migration and
restoration. `omarchy-shell background randomizerStatus` reports active output
assignments and renderer readiness for live checks.
