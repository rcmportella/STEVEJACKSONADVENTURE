"""
Game engine copy for SteveJacksonAdventure (package-aware)
"""
from character import Character
from node import Adventure
from combat import Combat



class GameEngine:
    def __init__(self, adventure, character):
        self.adventure = adventure
        self.character = character
        self.current_node = adventure.get_starting_node()
        self.game_over = False
        self.victory = False
        self.visited_nodes = set()
        self.game_log = []

    def start_game(self):
        self._log(f"\n{'='*60}")
        self._log(f"  {self.adventure.title}")
        self._log(f"{'='*60}")
        self._log(f"\n{self.adventure.description}\n")
        try:
            self._log(f"Character: {self.character.name}")
        except Exception:
            pass
        return self.process_node()

    def process_node(self):
        if self.current_node is None:
            return {'status': 'error', 'message': 'Invalid node!', 'game_over': True}
        self.visited_nodes.add(self.current_node.node_id)
        if self.current_node.is_victory:
            self.victory = True
            self.game_over = True
            return {'status': 'victory', 'message': self.current_node.description, 'game_over': True}
        if self.current_node.is_defeat:
            self.game_over = True
            return {'status': 'defeat', 'message': self.current_node.description, 'game_over': True}
        event_messages = self.current_node.execute_on_enter(self.character)
        stat_effect_messages = self.current_node.apply_stat_effects(self.character)
        if not self.character.is_alive():
            self.game_over = True
            return {
                'status': 'defeat',
                'message': 'You have died!',
                'game_over': True,
                'stat_effect_messages': stat_effect_messages,
            }
        treasure_messages = self.current_node.collect_treasure(self.character)
        has_combat = self.current_node.has_combat()
        return {
            'status': 'active',
            'node': self.current_node,
            'has_combat': has_combat,
            'event_messages': event_messages,
            'stat_effect_messages': stat_effect_messages,
            'treasure_messages': treasure_messages,
            'game_over': False,
        }

    def handle_choice(self, choice_index):
        if choice_index < 0 or choice_index >= len(self.current_node.choices):
            return {'status': 'error', 'message': 'Invalid choice!'}
        can_choose, reason = self.current_node.check_requirements(self.character, choice_index)
        if not can_choose:
            return {'status': 'blocked', 'message': f"Cannot choose this option: {reason}"}
        choice = self.current_node.choices[choice_index]
        next_node_id = choice['target']
        self.current_node = self.adventure.get_node(next_node_id)
        if self.current_node is None:
            return {'status': 'error', 'message': f'Node {next_node_id} not found!'}
        return self.process_node()

    def start_combat(self):
        return self.current_node.create_combat(self.character, self.adventure)

    def handle_combat_result(self, combat_result):
        if combat_result['status'] == 'victory':
            rewards = combat_result.get('rewards', {})
            messages = ['\n=== VICTORY! ===']
            if rewards.get('experience', 0) > 0:
                try:
                    self.character.gain_experience(rewards['experience'])
                    messages.append(f"Gained {rewards['experience']} XP!")
                except Exception:
                    pass
            if rewards.get('gold', 0) > 0:
                messages.append(f"Found {rewards['gold']} gold pieces!")
            for item in rewards.get('items', []):
                messages.append(f"Found: {item}")
            self.current_node.monsters = []
            return {'status': 'combat_complete', 'victory': True, 'messages': messages}
        elif combat_result['status'] == 'defeat':
            self.game_over = True
            return {'status': 'game_over', 'victory': False, 'message': 'You have been defeated in combat!'}
        elif combat_result['status'] == 'fled':
            return {'status': 'fled', 'message': combat_result.get('message', '')}
        else:
            return {'status': 'combat_ongoing', 'combat_status': combat_result}

    def _log(self, message):
        self.game_log.append(message)

    def get_character_status(self):
        return str(self.character)

    def save_game(self, filename="savegame.json"):
        import json
        save_data = {'character_name': getattr(self.character, 'name', ''), 'current_node': getattr(self.current_node, 'node_id', None)}
        with open(filename, 'w') as f:
            json.dump(save_data, f, indent=2)
        return f"Game saved to {filename}"

    def load_game(self, filename="savegame.json"):
        import json
        try:
            with open(filename, 'r') as f:
                save_data = json.load(f)
            self.current_node = self.adventure.get_node(save_data.get('current_node'))
            return f"Game loaded from {filename}"
        except FileNotFoundError:
            return "Save file not found!"
        except Exception as e:
            return f"Error loading game: {e}"


class GameUI:
    @staticmethod
    def display_node(node):
        print(node.get_display_text())

    @staticmethod
    def display_choices(node):
        print(node.get_choices_text())

    @staticmethod
    def display_character(character):
        print("\n" + "="*60)
        print("CHARACTER STATUS")
        print("="*60)
        try:
            print(character.get_character_sheet())
        except Exception:
            print(str(character))
        print("="*60 + "\n")

    @staticmethod
    def display_combat_status(combat):
        try:
            print(combat.get_combat_summary())
        except Exception:
            print("Combat status unavailable.")

    @staticmethod
    def display_messages(messages):
        for msg in messages:
            print(msg)

    @staticmethod
    def get_input(prompt="Enter your choice: "):
        return input(prompt)

    @staticmethod
    def display_title(text):
        print("\n" + "="*60)
        print(text.center(60))
        print("="*60 + "\n")

    @staticmethod
    def clear_screen():
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
