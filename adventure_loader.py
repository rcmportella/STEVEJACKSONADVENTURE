"""
Adventure Loader - package-aware copy for SteveJacksonAdventure
"""
import json
import os

from node import Adventure, GameNode


class AdventureLoader:
    """Load adventures from JSON format"""

    @staticmethod
    def load_from_file(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return AdventureLoader.load_from_dict(data)

    @staticmethod
    def load_from_dict(data):
        adventure = Adventure(
            title=data['title'],
            description=data['description'],
            starting_node_id=data['starting_node_id']
        )

        if 'custom_monsters' in data:
            for monster_name, monster_stats in data['custom_monsters'].items():
                adventure.add_custom_monster(monster_name, monster_stats)

        for node_data in data['nodes']:
            node = AdventureLoader._create_node(node_data)
            adventure.add_node(node)

        return adventure

    @staticmethod
    def _create_node(node_data):
        node = GameNode(
            node_id=node_data['node_id'],
            title=node_data['title'],
            description=node_data['description']
        )

        if 'monsters' in node_data:
            node.add_monster_encounter(node_data['monsters'])

        if 'treasure' in node_data:
            node.add_treasure(node_data['treasure'])

        if 'stat_effects' in node_data:
            for effect_data in node_data['stat_effects']:
                if isinstance(effect_data, dict) and 'stat' in effect_data:
                    node.add_stat_effect(
                        stat=effect_data['stat'],
                        amount=effect_data.get('amount', 0),
                        text=effect_data.get('text')
                    )
                elif isinstance(effect_data, dict):
                    for stat_name, amount in effect_data.items():
                        node.add_stat_effect(stat=stat_name, amount=amount)

        if 'choices' in node_data:
            for choice_data in node_data['choices']:
                node.add_choice(
                    choice_text=choice_data['text'],
                    target_node_id=choice_data['target'],
                    requirements=choice_data.get('requirements')
                )

        if node_data.get('is_victory', False):
            node.set_victory()
        if node_data.get('is_defeat', False):
            node.set_defeat()

        if 'gold_cost' in node_data:
            node.set_gold_cost(node_data['gold_cost'])

        if 'item_cost' in node_data:
            for item_name, quantity in node_data['item_cost'].items():
                node.set_item_cost(item_name, quantity)

        return node


class AdventureExporter:
    """Export adventures to JSON format"""

    @staticmethod
    def export_to_file(adventure, filepath):
        data = AdventureExporter.adventure_to_dict(adventure)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def adventure_to_dict(adventure):
        result = {
            'title': adventure.title,
            'description': adventure.description,
            'starting_node_id': adventure.starting_node_id,
            'nodes': [AdventureExporter._node_to_dict(node) for node in adventure.nodes.values()]
        }

        if adventure.custom_monsters:
            result['custom_monsters'] = adventure.custom_monsters

        return result

    @staticmethod
    def _node_to_dict(node):
        node_dict = {
            'node_id': node.node_id,
            'title': node.title,
            'description': node.description
        }

        if node.monsters:
            node_dict['monsters'] = node.monsters

        if node.treasure:
            node_dict['treasure'] = node.treasure

        if node.stat_effects:
            node_dict['stat_effects'] = [
                {
                    'stat': effect['stat'],
                    'amount': effect['amount'],
                    **({'text': effect['text']} if effect.get('text') else {})
                }
                for effect in node.stat_effects
            ]

        if node.choices:
            node_dict['choices'] = [
                {
                    'text': choice['text'],
                    'target': choice['target'],
                    'requirements': choice['requirements']
                }
                if choice['requirements'] else {
                    'text': choice['text'],
                    'target': choice['target']
                }
                for choice in node.choices
            ]

        if node.is_victory:
            node_dict['is_victory'] = True

        if node.is_defeat:
            node_dict['is_defeat'] = True

        if node.gold_cost > 0:
            node_dict['gold_cost'] = node.gold_cost

        if node.item_cost:
            node_dict['item_cost'] = node.item_cost

        return node_dict


class AdventureEditor:
    """Create and edit adventure JSON files for the Steve Jackson style system."""

    LEGACY_MONSTER_KEYS = {
        'hit_dice',
        'armor_class',
        'attack_bonus',
        'damage',
        'special_abilities',
        'treasure',
    }

    @staticmethod
    def _load_data(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def _save_data(filepath, data):
        AdventureEditor._validate_custom_monsters_schema(data)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @staticmethod
    def _validate_custom_monsters_schema(data):
        custom = data.get('custom_monsters', {})
        if not isinstance(custom, dict):
            raise ValueError("'custom_monsters' must be an object/dict")

        invalid_entries = []
        for monster_name, stats in custom.items():
            if not isinstance(stats, dict):
                invalid_entries.append((monster_name, ['<non-dict monster definition>']))
                continue

            keys = set(stats.keys())
            legacy_overlap = sorted(keys & AdventureEditor.LEGACY_MONSTER_KEYS)
            if legacy_overlap:
                invalid_entries.append((monster_name, legacy_overlap))

        if invalid_entries:
            detail = "; ".join(
                f"{name}: {', '.join(keys)}" for name, keys in invalid_entries
            )
            raise ValueError(
                "Legacy monster schema is not allowed in 'custom_monsters'. "
                "Use Steve Jackson fields (e.g. 'name', 'habilidade', 'energia'). "
                f"Invalid entries -> {detail}"
            )

    @staticmethod
    def _validate_node_data(node_data):
        required_fields = ('node_id', 'title', 'description')
        missing = [field for field in required_fields if field not in node_data]
        if missing:
            raise ValueError(f"Node data missing required fields: {', '.join(missing)}")

        if 'stat_effects' in node_data and not isinstance(node_data['stat_effects'], list):
            raise ValueError("'stat_effects' must be a list")

        if 'choices' in node_data and not isinstance(node_data['choices'], list):
            raise ValueError("'choices' must be a list")

    @staticmethod
    def create_adventure_file(filepath, title, description, starting_node_id, *, overwrite=False):
        """Create a new adventure JSON file with an empty node list."""
        if os.path.exists(filepath) and not overwrite:
            raise FileExistsError(f"File already exists: {filepath}")

        data = {
            'title': title,
            'description': description,
            'starting_node_id': starting_node_id,
            'nodes': []
        }
        AdventureEditor._save_data(filepath, data)
        return filepath

    @staticmethod
    def update_adventure_metadata(filepath, *, title=None, description=None, starting_node_id=None):
        """Update top-level adventure metadata fields."""
        data = AdventureEditor._load_data(filepath)

        if title is not None:
            data['title'] = title
        if description is not None:
            data['description'] = description
        if starting_node_id is not None:
            data['starting_node_id'] = starting_node_id

        AdventureEditor._save_data(filepath, data)
        return data

    @staticmethod
    def upsert_node(filepath, node_data):
        """Insert a new node or replace an existing node by node_id."""
        AdventureEditor._validate_node_data(node_data)
        data = AdventureEditor._load_data(filepath)

        nodes = data.setdefault('nodes', [])
        node_id = str(node_data['node_id'])
        replaced = False

        for index, existing in enumerate(nodes):
            if str(existing.get('node_id')) == node_id:
                nodes[index] = node_data
                replaced = True
                break

        if not replaced:
            nodes.append(node_data)

        AdventureEditor._save_data(filepath, data)
        return 'updated' if replaced else 'created'

    @staticmethod
    def remove_node(filepath, node_id):
        """Remove a node by node_id. Returns True if removed, else False."""
        data = AdventureEditor._load_data(filepath)
        nodes = data.get('nodes', [])
        node_id = str(node_id)

        filtered = [node for node in nodes if str(node.get('node_id')) != node_id]
        removed = len(filtered) != len(nodes)

        if removed:
            data['nodes'] = filtered
            AdventureEditor._save_data(filepath, data)

        return removed

    @staticmethod
    def add_choice(filepath, from_node_id, text, target, requirements=None):
        """Append a choice to an existing node."""
        data = AdventureEditor._load_data(filepath)
        from_node_id = str(from_node_id)

        for node in data.get('nodes', []):
            if str(node.get('node_id')) == from_node_id:
                choices = node.setdefault('choices', [])
                choice_data = {'text': text, 'target': target}
                if requirements:
                    choice_data['requirements'] = requirements
                choices.append(choice_data)
                AdventureEditor._save_data(filepath, data)
                return True

        return False

    @staticmethod
    def add_stat_effect(filepath, node_id, stat, amount, text=None):
        """Append one stat effect to a node."""
        data = AdventureEditor._load_data(filepath)
        node_id = str(node_id)

        for node in data.get('nodes', []):
            if str(node.get('node_id')) == node_id:
                effects = node.setdefault('stat_effects', [])
                effect = {'stat': stat, 'amount': amount}
                if text:
                    effect['text'] = text
                effects.append(effect)
                AdventureEditor._save_data(filepath, data)
                return True

        return False
