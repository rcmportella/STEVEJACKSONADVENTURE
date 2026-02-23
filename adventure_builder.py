"""
Interactive Adventure Builder
A text-based interface for creating JSON adventure files
"""
import json
import os
from adventure_loader import AdventureExporter, AdventureLoader
from node import Adventure, GameNode


class AdventureBuilder:
    """Interactive builder for creating adventures"""
    
    def __init__(self):
        self.adventure = None
        self.current_node = None
        
    def run(self):
        """Main entry point"""
        print("\n" + "="*70)
        print("ADVENTURE BUILDER - Interactive JSON Adventure Creator".center(70))
        print("="*70)
        print("\nCreate text adventures easily with this guided interface!")
        print("No JSON knowledge required - we'll build it together.\n")
        
        while True:
            print("\n" + "-"*70)
            print("MAIN MENU")
            print("-"*70)
            print("1. Create New Adventure")
            print("2. Load Existing Adventure")
            print("3. Edit Current Adventure")
            print("4. View Adventure Structure")
            print("5. Validate Adventure")
            print("6. Save Adventure")
            print("7. Exit")
            
            choice = input("\nChoice: ").strip()
            
            match choice:
                case '1':
                    self.create_new_adventure()
                case '2':
                    self.load_adventure()
                case '3':
                    if self.adventure:
                        self.edit_adventure_menu()
                    else:
                        print("\n⚠️  No adventure loaded. Create or load one first.")
                case '4':
                    if self.adventure:
                        self.view_structure()
                    else:
                        print("\n⚠️  No adventure loaded.")
                case '5':
                    if self.adventure:
                        self.validate_adventure()
                    else:
                        print("\n⚠️  No adventure loaded.")
                case '6':
                    if self.adventure:
                        self.save_adventure()
                    else:
                        print("\n⚠️  No adventure loaded.")
                case '7':
                    if self.adventure:
                        save = input("\nSave before exiting? (y/n): ").strip().lower()
                        if save == 'y':
                            self.save_adventure()
                    print("\nGoodbye! Happy adventuring! 🎮")
                    break
    
    def create_new_adventure(self):
        """Create a new adventure from scratch"""
        print("\n" + "="*70)
        print("CREATE NEW ADVENTURE")
        print("="*70)
        
        title = input("\nAdventure Title: ").strip()
        if not title:
            print("❌ Title cannot be empty.")
            return
        
        print("\nEnter a brief description/introduction for your adventure:")
        print("(This sets the scene for players)")
        description = input("> ").strip()
        if not description:
            print("❌ Description cannot be empty.")
            return
        
        print("\nWhat should be the starting node ID?")
        print("(Suggestion: 'start', 'beginning', or 'intro')")
        starting_node_id = input("Starting node ID: ").strip().lower().replace(' ', '_')
        if not starting_node_id:
            starting_node_id = "start"
        
        # Create adventure
        self.adventure = Adventure(title, description, starting_node_id)
        
        print(f"\n✓ Adventure '{title}' created!")
        print(f"✓ Starting node will be: '{starting_node_id}'")
        
        # Offer to create starting node
        create_start = input("\nCreate the starting node now? (y/n): ").strip().lower()
        if create_start == 'y':
            self.create_node(starting_node_id)
    
    def load_adventure(self):
        """Load an existing adventure"""
        print("\n" + "="*70)
        print("LOAD ADVENTURE")
        print("="*70)
        
        adventures_dir = 'adventures'
        if not os.path.exists(adventures_dir):
            print("\n❌ Adventures directory not found.")
            return
        
        json_files = [f for f in os.listdir(adventures_dir) if f.endswith('.json')]
        if not json_files:
            print("\n❌ No JSON adventures found.")
            return
        
        print("\nAvailable adventures:")
        for i, filename in enumerate(json_files, 1):
            print(f"  {i}. {filename}")
        
        choice = input("\nEnter number or filename: ").strip()
        
        try:
            file_idx = int(choice) - 1
            if 0 <= file_idx < len(json_files):
                filepath = os.path.join(adventures_dir, json_files[file_idx])
            else:
                print("❌ Invalid number.")
                return
        except ValueError:
            filepath = os.path.join(adventures_dir, choice)
        
        try:
            self.adventure = AdventureLoader.load_from_file(filepath)
            print(f"\n✓ Loaded: {self.adventure.title}")
            print(f"✓ Nodes: {len(self.adventure.nodes)}")
        except Exception as e:
            print(f"\n❌ Error loading: {e}")
    
    def edit_adventure_menu(self):
        """Menu for editing the current adventure"""
        while True:
            print("\n" + "-"*70)
            print(f"EDITING: {self.adventure.title}")
            print("-"*70)
            print("1. Add New Node")
            print("2. Edit Existing Node")
            print("3. Delete Node")
            print("4. Edit Adventure Info (title, description, starting node)")
            print("5. List All Nodes (complete)")
            print("6. List All Node IDs (simple)")
            print("7. Back to Main Menu")
            
            choice = input("\nChoice: ").strip()
            
            match choice:
                case '1':
                    self.create_node()
                case '2':
                    self.edit_node()
                case '3':
                    self.delete_node()
                case '4':
                    self.edit_adventure_info()
                case '5':
                    self.list_all_nodes()
                case '6':
                    self.list_all_nodes_simple()
                case '7':
                    break
    
    def create_node(self, node_id=None):
        """Create a new node"""
        print("\n" + "="*70)
        print("CREATE NEW NODE")
        print("="*70)
        
        if not node_id:
            print("\nNode ID (lowercase, no spaces, e.g., 'forest_entrance'):")
            node_id = input("> ").strip().lower().replace(' ', '_')
        
        if not node_id:
            print("❌ Node ID cannot be empty.")
            return
        
        if node_id in self.adventure.nodes:
            print(f"❌ Node '{node_id}' already exists!")
            return
        
        print("\nNode Title (shown to player):")
        title = input("> ").strip()
        if not title:
            print("❌ Title cannot be empty.")
            return
        
        print("\nNode Description (what the player sees/experiences):")
        print("(Press Enter twice to finish, or type END on a new line)")
        description_lines = []
        while True:
            line = input()
            if line == "END" or (line == "" and description_lines and description_lines[-1] == ""):
                if description_lines and description_lines[-1] == "":
                    description_lines.pop()
                break
            description_lines.append(line)
        description = "\n".join(description_lines).strip()
        
        if not description:
            print("❌ Description cannot be empty.")
            return
        
        # Create node
        node = GameNode(node_id, title, description)
        
        # Add optional elements
        print("\n" + "-"*70)
        print("Optional Elements (you can add these now or later)")
        print("-"*70)
        
        # Monsters
        add_monsters = input("\nAdd monsters? (y/n): ").strip().lower()
        if add_monsters == 'y':
            self.add_monsters_to_node(node)
        
        # Treasure
        add_treasure = input("\nAdd treasure? (y/n): ").strip().lower()
        if add_treasure == 'y':
            self.add_treasure_to_node(node)
        
        # Stat effects
        add_stat_effects = input("\nAdd stat effects (energia/habilidade/sorte)? (y/n): ").strip().lower()
        if add_stat_effects == 'y':
            self.add_stat_effects_to_node(node)
        
        # Gold cost
        add_gold_cost = input("\nAdd gold cost to enter this node? (y/n): ").strip().lower()
        if add_gold_cost == 'y':
            self.add_gold_cost_to_node(node)
        
        # Item cost
        add_item_cost = input("\nAdd item cost to enter this node? (y/n): ").strip().lower()
        if add_item_cost == 'y':
            self.add_item_cost_to_node(node)
        
        # Ending type
        print("\nIs this an ending node?")
        print("1. No (has choices)")
        print("2. Victory ending")
        print("3. Defeat ending")
        ending = input("Choice: ").strip()
        
        match ending:
            case '2':
                node.set_victory()
                print("✓ Marked as victory ending")
            case '3':
                node.set_defeat()
                print("✓ Marked as defeat ending")
            case _:
                # Add choices
                self.add_choices_to_node(node)
        
        # Add to adventure
        self.adventure.add_node(node)
        print(f"\n✓ Node '{node_id}' created successfully!")
    
    def add_monsters_to_node(self, node):
        """Add monsters to a node"""
        print("\nAvailable monster types:")
        monsters = ['goblin', 'orc', 'skeleton', 'giant_spider', 'zombie', 'ogre', 'troll', 'dragon']
        for i, monster in enumerate(monsters, 1):
            print(f"  {i}. {monster}")
        print(f"  {len(monsters) + 1}. Custom monster (create your own)")
        
        print("\nEnter monster numbers separated by spaces or commas (e.g., '1 1 2' or '1,1,2'):")
        print(f"Or enter '{len(monsters) + 1}' to create a custom monster:")
        monster_input = input("> ").strip()
        
        if monster_input:
            try:
                tokens = monster_input.replace(',', ' ').split()
                selected_indexes = [int(token) - 1 for token in tokens]
                added_count = 0

                for selected_index in selected_indexes:
                    if 0 <= selected_index < len(monsters):
                        node.add_monster_encounter(monsters[selected_index])
                        added_count += 1
                    elif selected_index == len(monsters):
                        # Custom monster option
                        custom_name = self.create_custom_monster()
                        if custom_name:
                            node.add_monster_encounter(custom_name)
                            added_count += 1
                    else:
                        print(f"⚠️  Ignoring invalid monster option: {selected_index + 1}")

                print(f"Added {added_count} monster(s)")
            except ValueError:
                print("❌ Invalid input. Skipping monsters.")
    
    def create_custom_monster(self):
        """Create a custom monster using Steve Jackson stats."""
        print("\n" + "-"*70)
        print("CREATE CUSTOM MONSTER")
        print("-"*70)
        
        name = input("Monster name: ").strip()
        if not name:
            print("❌ Monster name cannot be empty.")
            return None
        
        # Check if already exists
        if name in self.adventure.custom_monsters:
            print(f"Custom monster '{name}' already defined, reusing.")
            return name
        
        print("\nEnter Steve Jackson monster stats (press Enter for defaults):")

        try:
            habilidade = int(input("Habilidade [6]: ").strip() or "6")
        except ValueError:
            habilidade = 6

        try:
            energia = int(input("Energia [6]: ").strip() or "6")
        except ValueError:
            energia = 6

        habilidade = max(1, habilidade)
        energia = max(1, energia)

        monster_stats = {
            "name": name,
            "habilidade": habilidade,
            "energia": energia,
        }
        
        self.adventure.add_custom_monster(name, monster_stats)
        print(f"\nCustom monster '{name}' created successfully!")
        return name
    
    def add_treasure_to_node(self, node):
        """Add treasure to a node"""
        print("\nAdd treasure items (one per line, empty line to finish):")
        print("Examples: '50 gold pieces', 'Potion of Healing', 'Magic sword +1'")
        
        while True:
            item = input("> ").strip()
            if not item:
                break
            node.add_treasure(item)
            print(f"✓ Added: {item}")
    
    def add_traps_to_node(self, node):
        """Add traps to a node"""
        while True:
            print("\n--- Add Trap ---")
            trap_type = input("Trap description (e.g., 'spike trap', 'poison dart'): ").strip()
            if not trap_type:
                break
            
            try:
                dc = int(input("Difficulty Class (DC) [10-25]: ").strip())
                damage = input("Damage (e.g., '2d6', '1d8+2'): ").strip()
                
                print("\nSave type:")
                print("1. Reflex (dodge)")
                print("2. Fortitude (endurance)")
                print("3. Will (mental)")
                save_choice = input("Choice [1]: ").strip() or "1"
                
                save_types = {'1': 'reflex', '2': 'fortitude', '3': 'will'}
                save_type = save_types.get(save_choice, 'reflex')
                
                node.add_trap(trap_type, dc, damage, save_type)
                print(f"✓ Trap added: {trap_type} (DC {dc}, {damage} {save_type})")
                
                another = input("\nAdd another trap? (y/n): ").strip().lower()
                if another != 'y':
                    break
            except ValueError:
                print("❌ Invalid input. Skipping trap.")
                break

    def add_stat_effects_to_node(self, node):
        """Add Steve Jackson stat effects to a node."""
        valid_stats = {'1': 'energia', '2': 'habilidade', '3': 'sorte'}

        while True:
            print("\n--- Add Stat Effect ---")
            print("Which stat should be modified?")
            print("1. Energia")
            print("2. Habilidade")
            print("3. Sorte")

            stat_choice = input("Choice [1]: ").strip() or '1'
            stat = valid_stats.get(stat_choice)
            if not stat:
                print("❌ Invalid stat option.")
                continue

            print("\nAmount can be a number or dice expression.")
            print("Examples: -2, +1, -1d6, +1d3")
            amount = input("Amount: ").strip()
            if not amount:
                print("❌ Amount cannot be empty.")
                continue

            label = input("Optional text/label (e.g., 'poison gas'): ").strip()

            node.add_stat_effect(stat=stat, amount=amount, text=label or None)
            print(f"Added stat effect: {stat} {amount}")

            another = input("\nAdd another stat effect? (y/n): ").strip().lower()
            if another != 'y':
                break
    
    def add_gold_cost_to_node(self, node):
        """Add gold cost to a node"""
        print("\n--- Set Gold Cost ---")
        print("This is the amount of gold that will be deducted when the player enters this node.")
        print("Useful for: tolls, shop purchases, bribes, entry fees, etc.")
        
        try:
            gold_cost = int(input("Gold cost [0]: ").strip() or "0")
            if gold_cost > 0:
                node.set_gold_cost(gold_cost)
                print(f"✓ Gold cost set to {gold_cost} gp")
            else:
                print("⚠️  Gold cost must be greater than 0")
        except ValueError:
            print("❌ Invalid input. Must be a number.")
    
    def add_item_cost_to_node(self, node):
        """Add item cost to a node"""
        print("\n--- Set Item Cost ---")
        print("This requires the player to have certain items to enter this node.")
        print("The items will be removed when entering (consumed).")
        print("Useful for: keys, offerings, ingredients, quest items, etc.")
        print("You can add multiple different item types.\n")
        
        while True:
            item_name = input("Item name (empty to finish): ").strip()
            if not item_name:
                break
            
            try:
                quantity = int(input(f"Quantity of {item_name} required: ").strip() or "1")
                if quantity > 0:
                    node.set_item_cost(item_name, quantity)
                    print(f"✓ Item cost added: {quantity}x {item_name}")
                else:
                    print("⚠️  Quantity must be greater than 0")
            except ValueError:
                print("❌ Invalid quantity. Must be a number.")
            
            another = input("\nAdd another item cost? (y/n): ").strip().lower()
            if another != 'y':
                break
    
    def add_choices_to_node(self, node):
        """Add choices to a node"""
        print("\n" + "-"*70)
        print("ADD CHOICES")
        print("-"*70)
        print("Choices lead to other nodes. You'll need to create those nodes later.")
        print("(Empty text to finish adding choices)")
        
        while True:
            print("\n--- New Choice ---")
            choice_text = input("Choice text (what player sees): ").strip()
            if not choice_text:
                break
            
            # Show existing nodes
            print("\nExisting nodes:")
            for nid in sorted(self.adventure.nodes.keys()):
                print(f"  - {nid}")
            
            target = input("Target node ID: ").strip().lower().replace(' ', '_')
            if not target:
                print("❌ Target required. Skipping choice.")
                continue
            
            # Requirements
            add_req = input("Add requirements? (y/n): ").strip().lower()
            requirements = None
            
            if add_req == 'y':
                requirements = {}
                print("\nRequirement type:")
                print("1. Ability score (e.g., Strength 15)")
                print("2. Item (e.g., needs 'key')")
                print("3. Level (e.g., level 3+)")
                print("4. No requirements")
                
                req_type = input("Choice: ").strip()
                
                match req_type:
                    case '1':
                        print("\nAbility: str, dex, con, int, wis, cha")
                        ability = input("Ability: ").strip().lower()
                        if ability in ['strength', 'str']:
                            ability = 'strength'
                        elif ability in ['dexterity', 'dex']:
                            ability = 'dexterity'
                        elif ability in ['constitution', 'con']:
                            ability = 'constitution'
                        elif ability in ['intelligence', 'int']:
                            ability = 'intelligence'
                        elif ability in ['wisdom', 'wis']:
                            ability = 'wisdom'
                        elif ability in ['charisma', 'cha']:
                            ability = 'charisma'
                        
                        if ability in ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']:
                            try:
                                score = int(input(f"Required {ability} score: ").strip())
                                requirements[ability] = score
                            except ValueError:
                                print("❌ Invalid score.")
                    case '2':
                        item = input("Required item name: ").strip()
                        if item:
                            requirements['item'] = item
                    case '3':
                        try:
                            level = int(input("Required level: ").strip())
                            requirements['level'] = level
                        except ValueError:
                            print("❌ Invalid level.")
            
            node.add_choice(choice_text, target, requirements)
            print(f"✓ Choice added → {target}")
            
            if target not in self.adventure.nodes:
                print(f"⚠️  Note: Node '{target}' doesn't exist yet. Create it later.")
    
    def edit_node(self):
        """Edit an existing node"""
        if not self.adventure.nodes:
            print("\n❌ No nodes to edit.")
            return
        
        print("\n" + "="*70)
        print("EDIT NODE")
        print("="*70)
        print("\nExisting nodes:")
        for i, (nid, node) in enumerate(sorted(self.adventure.nodes.items()), 1):
            print(f"  {i}. {nid} - {node.title}")
        
        choice = input("\nEnter number or node ID: ").strip()
        
        node = None
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(self.adventure.nodes):
                node_id = sorted(self.adventure.nodes.keys())[idx]
                node = self.adventure.nodes[node_id]
        except ValueError:
            node_id = choice.lower().replace(' ', '_')
            node = self.adventure.nodes.get(node_id)
        
        if not node:
            print("❌ Node not found.")
            return
        
        while True:
            print("\n" + "-"*70)
            print(f"EDITING NODE: {node.node_id}")
            print("-"*70)
            print(f"Title: {node.title}")
            print(f"Description: {node.description[:50]}...")
            print(f"Monsters: {len(node.monsters)}")
            print(f"Treasure: {len(node.treasure)}")
            print(f"Stat effects: {len(node.stat_effects)}")
            print(f"Choices: {len(node.choices)}")
            print(f"Gold cost: {node.gold_cost}")
            print(f"Item costs: {len(node.item_cost)} types")
            print(f"Victory: {node.is_victory}, Defeat: {node.is_defeat}")
            
            print("\nWhat to edit?")
            print("1. Title")
            print("2. Description")
            print("3. Monsters")
            print("4. Treasure")
            print("5. Stat effects")
            print("6. Choices")
            print("7. Gold cost")
            print("8. Item costs")
            print("9. Ending flags")
            print("10. Back")
            
            edit_choice = input("\nChoice: ").strip()
            
            match edit_choice:
                case '1':
                    new_title = input(f"New title [{node.title}]: ").strip()
                    if new_title:
                        node.title = new_title
                        print("✓ Title updated")
                
                case '2':
                    print("\nNew description (press Enter twice or type END):")
                    description_lines = []
                    while True:
                        line = input()
                        if line == "END" or (line == "" and description_lines and description_lines[-1] == ""):
                            if description_lines and description_lines[-1] == "":
                                description_lines.pop()
                            break
                        description_lines.append(line)
                    new_desc = "\n".join(description_lines).strip()
                    if new_desc:
                        node.description = new_desc
                        print("✓ Description updated")
                
                case '3':
                    print("\nCurrent monsters:", node.monsters)
                    print("1. Add monsters")
                    print("2. Clear all monsters")
                    m_choice = input("Choice: ").strip()
                    match m_choice:
                        case '1':
                            self.add_monsters_to_node(node)
                        case '2':
                            node.monsters = []
                            print("✓ Monsters cleared")
                
                case '4':
                    print("\nCurrent treasure:", node.treasure)
                    print("1. Add treasure")
                    print("2. Clear all treasure")
                    t_choice = input("Choice: ").strip()
                    match t_choice:
                        case '1':
                            self.add_treasure_to_node(node)
                        case '2':
                            node.treasure = []
                            print("✓ Treasure cleared")
                
                case '5':
                    print("\nCurrent stat effects:", node.stat_effects)
                    print("1. Add stat effects")
                    print("2. Clear all stat effects")
                    effect_choice = input("Choice: ").strip()
                    match effect_choice:
                        case '1':
                            self.add_stat_effects_to_node(node)
                        case '2':
                            node.stat_effects = []
                            print("✓ Stat effects cleared")
                
                case '6':
                    print("\nCurrent choices:")
                    for i, c in enumerate(node.choices, 1):
                        print(f"  {i}. {c['text']} → {c['target']}")
                    print("\n1. Add choice")
                    print("2. Remove choice")
                    print("3. Clear all choices")
                    c_choice = input("Choice: ").strip()
                    
                    match c_choice:
                        case '1':
                            self.add_choices_to_node(node)
                        case '2':
                            try:
                                idx = int(input("Remove choice #: ").strip()) - 1
                                if 0 <= idx < len(node.choices):
                                    removed = node.choices.pop(idx)
                                    print(f"✓ Removed: {removed['text']}")
                            except (ValueError, IndexError):
                                print("❌ Invalid choice number")
                        case '3':
                            node.choices = []
                            print("✓ Choices cleared")
                
                case '7':
                    print(f"\nCurrent gold cost: {node.gold_cost}")
                    print("1. Set gold cost")
                    print("2. Remove gold cost")
                    gc_choice = input("Choice: ").strip()
                    match gc_choice:
                        case '1':
                            self.add_gold_cost_to_node(node)
                        case '2':
                            node.gold_cost = 0
                            # Remove gold cost event if it exists
                            node.on_enter_events = []
                            print("✓ Gold cost removed")
                
                case '8':
                    print(f"\nCurrent item costs:")
                    if node.item_cost:
                        for item_name, qty in node.item_cost.items():
                            print(f"  - {qty}x {item_name}")
                    else:
                        print("  None")
                    print("\n1. Add item cost")
                    print("2. Remove item cost")
                    print("3. Clear all item costs")
                    ic_choice = input("Choice: ").strip()
                    match ic_choice:
                        case '1':
                            self.add_item_cost_to_node(node)
                        case '2':
                            if node.item_cost:
                                item_name = input("Item name to remove: ").strip()
                                if item_name in node.item_cost:
                                    del node.item_cost[item_name]
                                    print(f"✓ Removed {item_name} cost")
                                else:
                                    print("❌ Item cost not found")
                            else:
                                print("❌ No item costs to remove")
                        case '3':
                            node.item_cost = {}
                            # Remove item cost events
                            node.on_enter_events = [e for e in node.on_enter_events if 'item' not in str(e)]
                            print("✓ All item costs cleared")
                
                case '9':
                    print(f"\nCurrent: Victory={node.is_victory}, Defeat={node.is_defeat}")
                    print("1. Set as victory")
                    print("2. Set as defeat")
                    print("3. Clear flags (normal node)")
                    flag_choice = input("Choice: ").strip()
                    
                    match flag_choice:
                        case '1':
                            node.is_victory = True
                            node.is_defeat = False
                            print("✓ Set as victory")
                        case '2':
                            node.is_victory = False
                            node.is_defeat = True
                            print("✓ Set as defeat")
                        case '3':
                            node.is_victory = False
                            node.is_defeat = False
                            print("✓ Flags cleared")
                
                case '10':
                    break
    
    def delete_node(self):
        """Delete a node"""
        if not self.adventure.nodes:
            print("\n❌ No nodes to delete.")
            return
        
        print("\n" + "="*70)
        print("DELETE NODE")
        print("="*70)
        print("\nExisting nodes:")
        for i, nid in enumerate(sorted(self.adventure.nodes.keys()), 1):
            print(f"  {i}. {nid}")
        
        choice = input("\nEnter number or node ID to delete: ").strip()
        
        node_id = None
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(self.adventure.nodes):
                node_id = sorted(self.adventure.nodes.keys())[idx]
        except ValueError:
            node_id = choice.lower().replace(' ', '_')
        
        if node_id not in self.adventure.nodes:
            print("❌ Node not found.")
            return
        
        confirm = input(f"\n⚠️  Really delete '{node_id}'? (yes/no): ").strip().lower()
        if confirm == 'yes':
            del self.adventure.nodes[node_id]
            print(f"✓ Node '{node_id}' deleted")
            print("⚠️  Warning: Update any choices that reference this node!")
        else:
            print("Cancelled.")
    
    def list_all_nodes(self):
        """Display a list of all nodes in the adventure"""
        print("\n" + "="*70)
        print("ALL NODES")
        print("="*70)
        
        if not self.adventure.nodes:
            print("\n❌ No nodes in this adventure yet.")
            input("\nPress Enter to continue...")
            return
        
        print(f"\nTotal nodes: {len(self.adventure.nodes)}")
        print(f"Starting node: {self.adventure.starting_node_id}")
        print("\n" + "-"*70)
        
        for i, (node_id, node) in enumerate(sorted(self.adventure.nodes.items()), 1):
            marker = "►" if node_id == self.adventure.starting_node_id else " "
            ending = " [VICTORY]" if node.is_victory else " [DEFEAT]" if node.is_defeat else ""
            
            print(f"\n{i}. {marker} {node_id}{ending}")
            print(f"   Title: {node.title}")
            print(f"   Monsters: {len(node.monsters)}, Treasure: {len(node.treasure)}, Stat effects: {len(node.stat_effects)}, Choices: {len(node.choices)}")
            
            if node.gold_cost > 0:
                print(f"   💰 Gold cost: {node.gold_cost}")
            if node.item_cost:
                items = ", ".join([f"{qty}x {name}" for name, qty in node.item_cost.items()])
                print(f"   🔑 Item cost: {items}")
        
        input("\nPress Enter to continue...")
    
    def list_all_nodes_simple(self):
        """Display a simple list of all node IDs"""
        print("\n" + "="*70)
        print("ALL NODE IDS")
        print("="*70)
        
        if not self.adventure.nodes:
            print("\n❌ No nodes in this adventure yet.")
            input("\nPress Enter to continue...")
            return
        
        print(f"\nTotal nodes: {len(self.adventure.nodes)}")
        print(f"Starting node: {self.adventure.starting_node_id}")
        print("\nNode IDs:")
        
        for node_id in sorted(self.adventure.nodes.keys()):
            marker = "►" if node_id == self.adventure.starting_node_id else " "
            print(f"  {marker} {node_id}")
        
        input("\nPress Enter to continue...")
    
    def edit_adventure_info(self):
        """Edit adventure metadata"""
        print("\n" + "="*70)
        print("EDIT ADVENTURE INFO")
        print("="*70)
        
        print(f"\nCurrent title: {self.adventure.title}")
        new_title = input("New title (Enter to keep): ").strip()
        if new_title:
            self.adventure.title = new_title
            print("✓ Title updated")
        
        print(f"\nCurrent description: {self.adventure.description}")
        new_desc = input("New description (Enter to keep): ").strip()
        if new_desc:
            self.adventure.description = new_desc
            print("✓ Description updated")
        
        print(f"\nCurrent starting node: {self.adventure.starting_node_id}")
        print("Available nodes:", ', '.join(sorted(self.adventure.nodes.keys())))
        new_start = input("New starting node (Enter to keep): ").strip()
        if new_start and new_start in self.adventure.nodes:
            self.adventure.starting_node_id = new_start
            print("✓ Starting node updated")
        elif new_start:
            print("❌ Node doesn't exist!")
    
    def view_structure(self):
        """Display adventure structure"""
        print("\n" + "="*70)
        print(f"ADVENTURE STRUCTURE: {self.adventure.title}")
        print("="*70)
        print(f"\nDescription: {self.adventure.description}")
        print(f"Starting Node: {self.adventure.starting_node_id}")
        print(f"Total Nodes: {len(self.adventure.nodes)}")
        
        print("\n" + "-"*70)
        print("NODE MAP")
        print("-"*70)
        
        for node_id in sorted(self.adventure.nodes.keys()):
            node = self.adventure.nodes[node_id]
            marker = "►" if node_id == self.adventure.starting_node_id else " "
            ending = " [VICTORY]" if node.is_victory else " [DEFEAT]" if node.is_defeat else ""
            
            print(f"\n{marker} {node_id}{ending}")
            print(f"  Title: {node.title}")
            
            if node.monsters:
                print(f"  ⚔️  Monsters: {', '.join(node.monsters)}")
            if node.treasure:
                print(f"  💰 Treasure: {len(node.treasure)} item(s)")
            if node.stat_effects:
                print(f"  ⚙️  Stat effects: {len(node.stat_effects)}")
            
            if node.choices:
                print("  Choices:")
                for choice in node.choices:
                    target = choice['target']
                    exists = "✓" if target in self.adventure.nodes else "✗"
                    reqs = f" [REQ]" if choice.get('requirements') else ""
                    print(f"    {exists} → {target}: {choice['text']}{reqs}")
        
        input("\nPress Enter to continue...")
    
    def validate_adventure(self):
        """Validate the current adventure"""
        print("\n" + "="*70)
        print("VALIDATING ADVENTURE")
        print("="*70)
        
        errors = []
        warnings = []
        
        # Check starting node exists
        if self.adventure.starting_node_id not in self.adventure.nodes:
            errors.append(f"Starting node '{self.adventure.starting_node_id}' doesn't exist")
        
        # Check each node
        has_victory = False
        has_defeat = False
        
        for node_id, node in self.adventure.nodes.items():
            if node.is_victory:
                has_victory = True
            if node.is_defeat:
                has_defeat = True
            
            # Check choices point to existing nodes
            for choice in node.choices:
                target = choice['target']
                if target not in self.adventure.nodes:
                    errors.append(f"Node '{node_id}': Choice points to missing node '{target}'")
            
            # Check for nodes without choices (should be endings)
            if not node.choices and not node.is_victory and not node.is_defeat:
                warnings.append(f"Node '{node_id}': No choices and not marked as ending")
        
        # Check for endings
        if not has_victory:
            warnings.append("No victory ending found")
        if not has_defeat:
            warnings.append("No defeat ending found")
        
        # Check reachability
        reachable = {self.adventure.starting_node_id}
        to_check = [self.adventure.starting_node_id]
        
        while to_check:
            current = to_check.pop()
            if current in self.adventure.nodes:
                for choice in self.adventure.nodes[current].choices:
                    target = choice['target']
                    if target not in reachable and target in self.adventure.nodes:
                        reachable.add(target)
                        to_check.append(target)
        
        unreachable = set(self.adventure.nodes.keys()) - reachable
        for node_id in unreachable:
            warnings.append(f"Node '{node_id}' is unreachable")
        
        # Display results
        if errors:
            print("\n❌ ERRORS:")
            for error in errors:
                print(f"  • {error}")
        
        if warnings:
            print("\n⚠️  WARNINGS:")
            for warning in warnings:
                print(f"  • {warning}")
        
        if not errors and not warnings:
            print("\n✓ Validation passed! Adventure looks good.")
        elif not errors:
            print("\n✓ No critical errors, but there are warnings to review.")
        else:
            print("\n✗ Validation failed. Fix errors before saving.")
        
        input("\nPress Enter to continue...")
    
    def save_adventure(self):
        """Save adventure to JSON file"""
        print("\n" + "="*70)
        print("SAVE ADVENTURE")
        print("="*70)
        
        # Suggest filename
        suggested_name = self.adventure.title.lower().replace(' ', '_')
        suggested_name = ''.join(c for c in suggested_name if c.isalnum() or c == '_')
        
        print(f"\nSuggested filename: {suggested_name}.json")
        filename = input("Filename (or Enter for suggested): ").strip()
        
        if not filename:
            filename = suggested_name + '.json'
        elif not filename.endswith('.json'):
            filename += '.json'
        
        # Ensure adventures directory exists
        os.makedirs('adventures', exist_ok=True)
        filepath = os.path.join('adventures', filename)
        
        # Check if file exists
        if os.path.exists(filepath):
            overwrite = input(f"\n⚠️  File exists. Overwrite? (y/n): ").strip().lower()
            if overwrite != 'y':
                print("Cancelled.")
                return
        
        try:
            AdventureExporter.export_to_file(self.adventure, filepath)
            print(f"\n✓ Adventure saved to: {filepath}")
            print(f"✓ {len(self.adventure.nodes)} nodes saved")
        except Exception as e:
            print(f"\n❌ Error saving: {e}")


def main():
    """Entry point"""
    builder = AdventureBuilder()
    builder.run()


if __name__ == "__main__":
    main()
