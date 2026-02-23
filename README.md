SteveJacksonAdventure
======================

Interactive text-adventure framework inspired by Steve Jackson gamebooks.

Repository
----------

GitHub: https://github.com/rcmportella/STEVEJACKSONADVENTURE

This project should be published with all core assets, including:

- `adventures/` (JSON adventure files)
- `sounds/` (audio assets used by the game)

Requirements
------------

- Python 3.10+

How to Run
----------

From the project root:

```bash
python main.py
```

Main Features
-------------

- Steve Jackson-style combat with `habilidade`, `energia`, and `sorte`
- Multi-monster encounters
- Node-based stat effects (`stat_effects`) instead of D20 traps
- Adventure loading/saving in JSON format
- Interactive adventure editing tools

Key Files
---------

- `main.py` — game entry point
- `game.py` — main game engine loop
- `character.py` — player model
- `monster.py` — monster model and built-in monster factory
- `combat.py` — combat logic
- `node.py` — adventure and node structures
- `adventure_loader.py` — load/export plus `AdventureEditor` API
- `editor.py` — interactive CLI to create/edit adventures
- `adventure_builder.py` — interactive builder for larger editing sessions

Adventure Data Format (Summary)
-------------------------------

Each node may include:

- `monsters`: list of monster names
- `treasure`: list of strings
- `stat_effects`: list of effects, e.g.:

```json
"stat_effects": [
  { "stat": "energia", "amount": "-1d6", "text": "Poison darts" },
  { "stat": "sorte", "amount": "+1", "text": "Lucky charm" }
]
```

Adventure editing API
---------------------

`AdventureEditor` in `adventure_loader.py` can create and modify adventure JSON files programmatically.

Quick example:

```python
from adventure_loader import AdventureEditor

path = "adventures/new_adventure.json"

AdventureEditor.create_adventure_file(
    path,
    title="My Adventure",
    description="A short test adventure",
    starting_node_id="start",
    overwrite=True,
)

AdventureEditor.upsert_node(path, {
    "node_id": "start",
    "title": "Start",
    "description": "You stand at a crossroads.",
    "choices": [{"text": "Go north", "target": "north"}]
})
```

Release Checklist
-----------------

Use this quick flow when publishing updates:

```bash
# 1) Make sure you are on main
git checkout main

# 2) Sync with remote
git pull origin main

# 3) Check what changed
git status

# 4) Stage everything (or stage specific files)
git add -A

# 5) Commit
git commit -m "Describe your changes"

# 6) Push
git push origin main
```

Recommended before pushing:

- Run the game once (`python main.py`)
- Ensure new/updated JSON adventures in `adventures/` load correctly
- Ensure required sound files are present in `sounds/`
