# Windows Explorer Goblin

A tiny Windows rename assistant that adds smarter autocomplete to file and folder naming.

The first build uses an AutoHotkey v2 overlay instead of trying to fight Windows Explorer's inline rename box. Press a hotkey, type in the Goblin rename box, get live suggestions from a Python suggestion brain, press Tab to accept, and Enter to rename the selected item.

## MVP features

- Windows Explorer and Desktop support
- Ctrl + Space hotkey
- Overlay rename box
- Live suggestions while typing
- Tab accepts the top suggestion
- Enter renames the selected file or folder
- Esc cancels
- Python suggestion brain with fuzzy matching
- Rename history learning
- Dataset/audio naming template support

## Folder layout

```text
windows-explorer-goblin/
├─ ahk/
│  └─ ExplorerGoblin.ahk
├─ src/
│  └─ rename_brain.py
├─ config/
│  └─ goblin_config.json
├─ docs/
│  └─ ROADMAP.md
├─ launch.bat
├─ requirements.txt
└─ README.md
```

## Requirements

- Windows 10 or Windows 11
- AutoHotkey v2
- Python 3.10+

No external Python packages are required for the MVP.

## Quick start

1. Install AutoHotkey v2.
2. Install Python 3.10+ and make sure the `py` launcher works.
3. Double-click `launch.bat`.
4. In Explorer, select a file or folder.
5. Press `Ctrl + Space`.
6. Type a new name.
7. Press `Tab` to accept the top suggestion.
8. Press `Enter` to rename.

## Why overlay instead of native inline rename?

Explorer's inline rename edit control does not reliably expose live text/cursor state to automation tools. The overlay keeps the workflow fast while making the suggestion logic reliable.

## Design goal

Make Windows Explorer feel like it has IDE-style autocomplete for file and folder names, with special support for dataset naming, audio sample catalogs, texture maps, and project assets.
