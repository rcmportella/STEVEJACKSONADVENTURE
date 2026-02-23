"""
Interactive adventure editor for SteveJacksonAdventure.

This CLI wraps AdventureEditor methods so you can create and edit
adventure JSON files without manually editing raw JSON.
"""
import json
import os

from adventure_loader import AdventureEditor, AdventureLoader


ADVENTURES_DIR = "adventures"


def prompt(text, default=None):
    if default is None:
        return input(text).strip()
    value = input(f"{text} [{default}]: ").strip()
    return value if value else str(default)


def prompt_int(text, default=None, allow_blank=False):
    while True:
        value = prompt(text, default)
        if allow_blank and value == "":
            return None
        try:
            return int(value)
        except ValueError:
            print("Please enter a valid integer.")


def prompt_yes_no(text, default=False):
    suffix = "Y/n" if default else "y/N"
    value = input(f"{text} ({suffix}): ").strip().lower()
    if not value:
        return default
    return value in ("y", "yes", "s", "sim")


def list_adventures():
    if not os.path.isdir(ADVENTURES_DIR):
        return []
    return sorted([f for f in os.listdir(ADVENTURES_DIR) if f.endswith(".json")])


def choose_adventure_file(allow_new=False):
    files = list_adventures()
    print("\nAvailable adventures:")
    if files:
        for idx, filename in enumerate(files, 1):
            print(f"  {idx}. {filename}")
    else:
        print("  (none found)")

    if allow_new:
        print("\nType a number, filename, or a new filename.")
    else:
        print("\nType a number or filename.")

    value = input("Adventure file: ").strip()
    if not value:
        return None

    if value.isdigit() and files:
        index = int(value) - 1
        if 0 <= index < len(files):
            return os.path.join(ADVENTURES_DIR, files[index])

    if not value.lower().endswith(".json"):
        value = f"{value}.json"

    if os.path.sep in value:
        return value
    return os.path.join(ADVENTURES_DIR, value)


def load_raw_data(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def save_raw_data(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def find_node(data, node_id):
    for node in data.get("nodes", []):
        if str(node.get("node_id")) == str(node_id):
            return node
    return None


def parse_csv_list(value):
    if not value:
        return []
    return [part.strip() for part in value.split(",") if part.strip()]


def collect_stat_effects(existing=None):
    effects = list(existing or [])
    if effects:
        print(f"Current stat effects: {json.dumps(effects, ensure_ascii=False)}")
        if prompt_yes_no("Clear current stat effects?", default=False):
            effects = []

    while prompt_yes_no("Add a stat effect?", default=False):
        stat = prompt("  Stat (energia/habilidade/sorte)", "energia").lower()
        amount = prompt("  Amount (e.g. -2, +1, -1d6)", "-1")
        text = prompt("  Text (optional)")
        effect = {"stat": stat, "amount": amount}
        if text:
            effect["text"] = text
        effects.append(effect)

    return effects


def collect_choices(existing=None):
    choices = list(existing or [])
    if choices:
        print(f"Current choices: {json.dumps(choices, ensure_ascii=False)}")
        if prompt_yes_no("Clear current choices?", default=False):
            choices = []

    while prompt_yes_no("Add a choice?", default=False):
        text = prompt("  Choice text")
        target = prompt("  Target node_id")
        req_item = prompt("  Required item (blank if none)")
        choice = {"text": text, "target": target}
        if req_item:
            choice["requirements"] = {"item": req_item}
        choices.append(choice)

    return choices


def create_adventure_flow():
    filepath = choose_adventure_file(allow_new=True)
    if not filepath:
        print("Canceled.")
        return

    title = prompt("Title")
    description = prompt("Description")
    start = prompt("Starting node id", "start")

    overwrite = os.path.exists(filepath)
    if overwrite:
        overwrite = prompt_yes_no("File exists. Overwrite?", default=False)
        if not overwrite:
            print("Canceled.")
            return

    os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
    AdventureEditor.create_adventure_file(
        filepath,
        title=title,
        description=description,
        starting_node_id=start,
        overwrite=overwrite,
    )
    print(f"Created: {filepath}")


def edit_metadata_flow():
    filepath = choose_adventure_file()
    if not filepath or not os.path.exists(filepath):
        print("Adventure file not found.")
        return

    data = load_raw_data(filepath)
    title = prompt("Title", data.get("title", ""))
    description = prompt("Description", data.get("description", ""))
    start = prompt("Starting node id", data.get("starting_node_id", "start"))

    AdventureEditor.update_adventure_metadata(
        filepath,
        title=title,
        description=description,
        starting_node_id=start,
    )
    print("Metadata updated.")


def upsert_node_flow():
    filepath = choose_adventure_file()
    if not filepath or not os.path.exists(filepath):
        print("Adventure file not found.")
        return

    data = load_raw_data(filepath)
    node_id = prompt("Node id")
    existing = find_node(data, node_id)

    base = dict(existing) if existing else {"node_id": node_id}
    if existing:
        print("Editing existing node.")
    else:
        print("Creating new node.")

    base["node_id"] = node_id
    base["title"] = prompt("Title", base.get("title", ""))
    base["description"] = prompt("Description", base.get("description", ""))

    base["is_victory"] = prompt_yes_no("Victory node?", default=bool(base.get("is_victory", False)))
    base["is_defeat"] = prompt_yes_no("Defeat node?", default=bool(base.get("is_defeat", False)))

    monsters_input = prompt(
        "Monsters (comma-separated, blank keeps current)",
        ", ".join(base.get("monsters", [])) if base.get("monsters") else "",
    )
    base["monsters"] = parse_csv_list(monsters_input)
    if not base["monsters"]:
        base.pop("monsters", None)

    treasure_input = prompt(
        "Treasure (comma-separated, blank keeps current)",
        ", ".join(base.get("treasure", [])) if base.get("treasure") else "",
    )
    base["treasure"] = parse_csv_list(treasure_input)
    if not base["treasure"]:
        base.pop("treasure", None)

    base["stat_effects"] = collect_stat_effects(base.get("stat_effects"))
    if not base["stat_effects"]:
        base.pop("stat_effects", None)

    base["choices"] = collect_choices(base.get("choices"))
    if not base["choices"]:
        base.pop("choices", None)

    gold_cost_default = base.get("gold_cost") if base.get("gold_cost") is not None else 0
    set_gold = prompt_yes_no("Set gold cost?", default=bool(base.get("gold_cost", 0)))
    if set_gold:
        base["gold_cost"] = prompt_int("Gold cost", default=gold_cost_default)
    else:
        base.pop("gold_cost", None)

    item_cost = dict(base.get("item_cost", {}))
    if item_cost:
        print(f"Current item_cost: {json.dumps(item_cost, ensure_ascii=False)}")
    if prompt_yes_no("Edit item costs?", default=False):
        item_cost = {}
        while prompt_yes_no("Add item cost?", default=False):
            item_name = prompt("  Item name")
            quantity = prompt_int("  Quantity", default=1)
            item_cost[item_name] = quantity
    if item_cost:
        base["item_cost"] = item_cost
    else:
        base.pop("item_cost", None)

    result = AdventureEditor.upsert_node(filepath, base)
    print(f"Node {result}: {node_id}")


def remove_node_flow():
    filepath = choose_adventure_file()
    if not filepath or not os.path.exists(filepath):
        print("Adventure file not found.")
        return

    node_id = prompt("Node id to remove")
    if not prompt_yes_no(f"Confirm remove node '{node_id}'?", default=False):
        print("Canceled.")
        return

    removed = AdventureEditor.remove_node(filepath, node_id)
    print("Node removed." if removed else "Node not found.")


def add_choice_flow():
    filepath = choose_adventure_file()
    if not filepath or not os.path.exists(filepath):
        print("Adventure file not found.")
        return

    from_node = prompt("From node id")
    text = prompt("Choice text")
    target = prompt("Target node id")
    req_item = prompt("Required item (blank if none)")

    requirements = {"item": req_item} if req_item else None
    ok = AdventureEditor.add_choice(filepath, from_node, text, target, requirements)
    print("Choice added." if ok else "From node not found.")


def add_stat_effect_flow():
    filepath = choose_adventure_file()
    if not filepath or not os.path.exists(filepath):
        print("Adventure file not found.")
        return

    node_id = prompt("Node id")
    stat = prompt("Stat (energia/habilidade/sorte)", "energia").lower()
    amount = prompt("Amount (e.g. -2, +1, -1d6)", "-1")
    text = prompt("Text (optional)")

    ok = AdventureEditor.add_stat_effect(filepath, node_id, stat, amount, text or None)
    print("Stat effect added." if ok else "Node not found.")


def list_nodes_flow():
    filepath = choose_adventure_file()
    if not filepath or not os.path.exists(filepath):
        print("Adventure file not found.")
        return

    print(f"\nLoading: {filepath}")
    adventure = AdventureLoader.load_from_file(filepath)
    node_count = len(adventure.nodes)
    print(f"\n{adventure.title} ({node_count} nodes)")

    if node_count == 0:
        print("(No nodes in this adventure yet)")

    for node in adventure.nodes.values():
        tags = []
        if node.is_victory:
            tags.append("victory")
        if node.is_defeat:
            tags.append("defeat")
        tag_text = f" [{' | '.join(tags)}]" if tags else ""
        print(f"- {node.node_id}: {node.title}{tag_text}")

    input("\nPress Enter to return to menu...")


def show_node_flow():
    filepath = choose_adventure_file()
    if not filepath or not os.path.exists(filepath):
        print("Adventure file not found.")
        return

    data = load_raw_data(filepath)
    node_id = prompt("Node id")
    node = find_node(data, node_id)
    if not node:
        print("Node not found.")
        return
    print(json.dumps(node, indent=2, ensure_ascii=False))


def print_menu():
    print("\n" + "=" * 60)
    print("ADVENTURE EDITOR")
    print("=" * 60)
    print("1. Create new adventure file")
    print("2. Edit adventure metadata")
    print("3. Add/Update node")
    print("4. Remove node")
    print("5. Add choice to node")
    print("6. Add stat effect to node")
    print("7. List nodes")
    print("8. Show node JSON")
    print("9. Exit")


def main():
    os.makedirs(ADVENTURES_DIR, exist_ok=True)

    actions = {
        "1": create_adventure_flow,
        "2": edit_metadata_flow,
        "3": upsert_node_flow,
        "4": remove_node_flow,
        "5": add_choice_flow,
        "6": add_stat_effect_flow,
        "7": list_nodes_flow,
        "8": show_node_flow,
    }

    while True:
        print_menu()
        option = input("\nChoose an option: ").strip()

        if option == "9":
            print("Bye!")
            return

        action = actions.get(option)
        if not action:
            print("Invalid option.")
            continue

        try:
            action()
        except FileNotFoundError:
            print("File not found.")
        except json.JSONDecodeError as exc:
            print(f"Invalid JSON file: {exc}")
        except Exception as exc:
            print(f"Error: {exc}")


if __name__ == "__main__":
    main()
