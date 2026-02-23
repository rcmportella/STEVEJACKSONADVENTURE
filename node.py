"""
Node/Paragraph system (package-aware copy for SteveJacksonAdventure)
"""
from combat import Combat
from monster import create_monster
import dice


class GameNode:
    """
    Represents a paragraph/location in the gamebook.
    Each node has a description and can contain encounters, choices, etc.
    """
    def __init__(self, node_id, title, description):
        self.node_id = node_id
        self.title = title
        self.description = description
        self.monsters = []
        self.treasure = []
        self.stat_effects = []
        self.choices = []
        self.is_victory = False
        self.is_defeat = False
        self.on_enter_events = []
        self.gold_cost = 0
        self.item_cost = {}

    def add_monster_encounter(self, monster_types):
        if isinstance(monster_types, str):
            self.monsters.append(monster_types)
        else:
            self.monsters.extend(monster_types)

    def add_treasure(self, items):
        if isinstance(items, str):
            self.treasure.append(items)
        else:
            self.treasure.extend(items)

    def add_stat_effect(self, stat, amount, text=None):
        self.stat_effects.append({
            'stat': str(stat).lower(),
            'amount': amount,
            'text': text,
        })

    def add_choice(self, choice_text, target_node_id, requirements=None):
        self.choices.append({'text': choice_text, 'target': target_node_id, 'requirements': requirements or {}})

    def set_victory(self):
        self.is_victory = True

    def set_defeat(self):
        self.is_defeat = True

    def add_on_enter_event(self, event_func):
        self.on_enter_events.append(event_func)

    def set_gold_cost(self, amount):
        self.gold_cost = amount

        def gold_cost_event(character, node):
            if character.remove_gold(amount):
                return f"You pay {amount} gold to enter. (Remaining: {character.gold} gp)"
            else:
                return f"WARNING: You don't have enough gold! ({character.gold}/{amount} gp needed)"

        self.add_on_enter_event(gold_cost_event)

    def set_item_cost(self, item_name, quantity):
        self.item_cost[item_name] = quantity

        def item_cost_event(character, node):
            available = character.count_item(item_name)
            if character.remove_items(item_name, quantity):
                return f"You use {quantity}x {item_name} to enter. (Remaining: {available - quantity})"
            else:
                return f"WARNING: You don't have enough {item_name}! ({available}/{quantity} needed)"

        self.add_on_enter_event(item_cost_event)

    def add_item_cost(self, item_name, quantity):
        self.set_item_cost(item_name, quantity)

    def execute_on_enter(self, character):
        messages = []
        for event in self.on_enter_events:
            msg = event(character, self)
            if msg:
                messages.append(msg)
        return messages

    def check_requirements(self, character, choice_index):
        if choice_index >= len(self.choices):
            return False, "Invalid choice"
        choice = self.choices[choice_index]
        requirements = choice['requirements']

        if 'item' in requirements:
            required_item = requirements['item']
            has_item = any(getattr(item, 'name', '') == required_item for item in getattr(character, 'inventory', []))
            if not has_item:
                return False, f"Requires {required_item}"

        return True, ""

    def _resolve_effect_amount(self, amount):
        if isinstance(amount, (int, float)):
            return int(amount)

        text = str(amount).strip()
        if not text:
            return 0

        sign = 1
        if text[0] in ('+', '-'):
            sign = -1 if text[0] == '-' else 1
            text = text[1:]

        if 'd' in text.lower():
            return sign * self._roll_from_dice_expression(text, default=0)

        return sign * int(text)

    def _apply_stat_delta(self, character, stat, delta):
        stat = stat.lower()
        aliases = {
            'energia': 'current_energia',
            'stamina': 'current_energia',
            'endurance': 'current_energia',
            'habilidade': 'current_habilidade',
            'skill': 'current_habilidade',
            'sorte': 'current_sorte',
            'luck': 'current_sorte',
        }

        current_attr = aliases.get(stat)
        if not current_attr:
            return False

        max_attr = current_attr.replace('current_', 'max_')
        current_value = getattr(character, current_attr, None)
        if current_value is None:
            return False

        if current_attr == 'current_energia':
            if delta < 0:
                character.take_damage(abs(delta))
            elif delta > 0:
                if hasattr(character, 'heal'):
                    character.heal(delta)
                else:
                    max_value = getattr(character, max_attr, current_value)
                    setattr(character, current_attr, min(max_value, current_value + delta))
            return True

        new_value = current_value + delta
        max_value = getattr(character, max_attr, current_value)
        new_value = max(0, min(max_value, new_value))
        setattr(character, current_attr, new_value)
        return True

    def apply_stat_effects(self, character):
        messages = []
        for effect in self.stat_effects:
            stat = str(effect.get('stat', '')).lower()
            raw_amount = effect.get('amount', 0)
            amount = self._resolve_effect_amount(raw_amount)
            custom_text = effect.get('text')

            applied = self._apply_stat_delta(character, stat, amount)
            if not applied:
                messages.append(f"Unknown stat effect ignored: {stat}")
                continue

            sign = '+' if amount >= 0 else ''
            stat_name = stat.capitalize()
            if custom_text:
                messages.append(f"{custom_text}: {stat_name} {sign}{amount}")
            else:
                messages.append(f"{stat_name} {sign}{amount}")

            if stat in ('energia', 'stamina', 'endurance'):
                messages.append(
                    f"Energia: {getattr(character, 'current_energia', '?')}/{getattr(character, 'max_energia', '?')}"
                )
        return messages

    def has_combat(self):
        return len(self.monsters) > 0

    def _roll_from_dice_expression(self, expression, default=4):
        if not expression or not isinstance(expression, str) or 'd' not in expression:
            return default

        expr = expression.lower().replace(' ', '')
        bonus = 0
        if '+' in expr:
            dice_part, bonus_part = expr.split('+', 1)
            bonus = int(bonus_part)
        elif '-' in expr:
            dice_part, malus_part = expr.split('-', 1)
            bonus = -int(malus_part)
        else:
            dice_part = expr

        count_text, sides_text = dice_part.split('d', 1)
        count = int(count_text) if count_text else 1
        sides = int(sides_text)
        return max(1, dice.roll(sides, count, bonus))

    def _create_custom_monster(self, monster_key, stats):
        from monster import Monster

        name = stats.get('name', str(monster_key).replace('_', ' ').title())

        habilidade = stats.get('habilidade')
        if habilidade is None:
            habilidade = stats.get('skill')
        if habilidade is None:
            habilidade = stats.get('attack_bonus')
        if habilidade is None:
            habilidade = 5

        energia = stats.get('energia')
        if energia is None:
            energia = stats.get('stamina')
        if energia is None:
            energia = stats.get('endurance')
        if energia is None:
            energia = self._roll_from_dice_expression(stats.get('hit_dice', ''), default=4)

        return Monster(name=name, habilidade=int(habilidade), energia=int(energia))

    def create_combat(self, character, adventure=None):
        monster_instances = []
        custom_monsters = adventure.custom_monsters if adventure else {}

        for entry in self.monsters:
            if isinstance(entry, dict):
                base_name = entry.get('type') or entry.get('name') or 'monster'
                if base_name in custom_monsters:
                    stats = dict(custom_monsters[base_name])
                    stats.update(entry)
                    monster_instances.append(self._create_custom_monster(base_name, stats))
                else:
                    monster_instances.append(self._create_custom_monster(base_name, entry))
                continue

            m_type = str(entry)
            if m_type in custom_monsters:
                monster_instances.append(self._create_custom_monster(m_type, custom_monsters[m_type]))
            else:
                monster_instances.append(create_monster(m_type))

        return Combat(character, monster_instances)

    def collect_treasure(self, character):
        messages = []
        for item in self.treasure:
            if 'gold' in item.lower():
                amount = int(''.join(filter(str.isdigit, item)))
                character.add_gold(amount)
                messages.append(f"You found {amount} gold pieces! (Total: {character.gold} gp)")
            else:
                messages.append(f"You found: {item}")
        self.treasure = []
        return messages

    def get_display_text(self):
        text = f"\n{'='*60}\n"
        text += f"{self.title}\n"
        text += f"{'='*60}\n\n"
        text += f"{self.description}\n"
        return text

    def get_choices_text(self):
        if not self.choices:
            return "\n[No choices available - this is an ending]"
        text = "\nWhat do you do?\n"
        for i, choice in enumerate(self.choices):
            text += f"  [{i+1}] {choice['text']}\n"
        return text

    def __str__(self):
        return f"Node {self.node_id}: {self.title}"


class Adventure:
    def __init__(self, title, description, starting_node_id):
        self.title = title
        self.description = description
        self.starting_node_id = starting_node_id
        self.nodes = {}
        self.custom_monsters = {}

    def add_node(self, node):
        self.nodes[node.node_id] = node

    def get_node(self, node_id):
        return self.nodes.get(node_id)

    def get_starting_node(self):
        return self.nodes.get(self.starting_node_id)

    def add_custom_monster(self, monster_name, stats):
        self.custom_monsters[monster_name] = stats

    def get_custom_monster(self, monster_name):
        return self.custom_monsters.get(monster_name)

    def __str__(self):
        return f"{self.title}: {len(self.nodes)} locations"
