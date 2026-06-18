# Windows Explorer Goblin

A tiny Windows rename assistant that adds smarter autocomplete to file and folder naming.

This build uses an AutoHotkey v2 overlay instead of trying to fight Windows Explorer's inline rename box. Press a hotkey, type in the Goblin rename box, get live suggestions from a Python suggestion brain, press Tab to accept, and Enter to rename the selected item.

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
- Built-in fallback suggestions for examples, experiments, exports, docs, assets, datasets, and textures
- Optional local SLM suggestions through Ollama

## Quick start

1. Install AutoHotkey v2.
2. Install Python 3.10+ and make sure the `py` launcher works.
3. Double-click `launch.bat`.
4. In Explorer, select a file or folder.
5. Press `Ctrl + Space`.
6. Type a new name.
7. Press `Tab` to accept the top suggestion.
8. Press `Enter` to rename.

## Optional SLM setup

The deterministic suggestion brain works without extra packages. For local model suggestions, install Ollama and pull a small model:

```bat
ollama pull qwen2.5:0.5b
```

The model is configured in `config/goblin_config.json`:

```json
"slm": {
  "enabled": true,
  "provider": "ollama",
  "model": "qwen2.5:0.5b",
  "timeout_seconds": 2.5
}
```

If Ollama is missing or the model is not installed, Goblin falls back to deterministic suggestions.

## Why overlay instead of native inline rename?

Explorer's inline rename edit control does not reliably expose live text/cursor state to automation tools. The overlay keeps the workflow fast while making the suggestion logic reliable.

## Design goal

Make Windows Explorer feel like it has IDE-style autocomplete for file and folder names, with special support for dataset naming, audio sample catalogs, texture maps, and project assets.
