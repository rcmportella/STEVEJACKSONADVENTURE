"""
Minimal main for SteveJacksonAdventure
Only prompts for a character name (no classes) and runs a short combat.
"""
import os

# When run directly as a script: python steve_jackson_adventure/main.py
# Import the local modules instead
from character import Character
from monster import Goblin
from combat import Combat
from adventure_loader import AdventureLoader
from sample_adventure import create_sample_adventure
from sound_manager import sound_manager
import game

def play_adventure(game_engine):
    """Main game loop"""
    ui = game.GameUI()
    
    # Start background music
    sound_manager.play_music('adventure_theme.wav')
    
    # Start the game
    result = game_engine.start_game()
    
    while not game_engine.game_over:
        # Display current node
        ui.display_node(game_engine.current_node)
        
        # Display any messages from processing the node
        if result.get('event_messages'):
            ui.display_messages(result['event_messages'])
        if result.get('stat_effect_messages'):
            ui.display_messages(result['stat_effect_messages'])
        if result.get('treasure_messages'):
            sound_manager.play_sound('treasure')
            ui.display_messages(result['treasure_messages'])
        
        # Check if there's combat
        if result.get('has_combat'):
            sound_manager.play_sound('combat_start')
            print("\n" + "!"*60)
            print("COMBAT BEGINS!".center(60))
            print("!"*60)
            
            combat = game_engine.start_combat()
            combat_result = {'status': 'ongoing'}
            
            while combat_result['status'] == 'ongoing':
                ui.display_combat_status(combat)
                
                print("\nCombat Options:")
                print("  1. Attack")
                print("  3. Use Item")
                print("  4. Attempt to Flee")
                
                action = input("\nWhat do you do? ")
                
                if action == '1':
                    # Attack
                    round_action = {'type': 'attack', 'weapon_damage': '1d8'}
                    alive_targets = combat.get_alive_monsters()
                    if len(alive_targets) > 1:
                        print("\nChoose your duel target:")
                        for idx, monster in enumerate(alive_targets, 1):
                            print(f"  {idx}. {monster.name} ({monster.energia} energia)")

                        target_choice = input("Target number (Enter for first): ").strip()
                        if target_choice.isdigit():
                            parsed = int(target_choice) - 1
                            if 0 <= parsed < len(alive_targets):
                                round_action['target_index'] = parsed

                        support_luck = input("Use Sorte against support hits this round? (y/n): ").strip().lower()
                        if support_luck == 'y':
                            round_action['use_luck_support_defense'] = True

                    combat_result = combat.execute_round(round_action)
                    ui.display_messages(combat_result.get('log', []))
                    
                elif action == '3':
                    # Use item
                    if not game_engine.character.inventory:
                        print("Your inventory is empty!")
                        continue
                    print("\nInventory:")
                    for i, item in enumerate(game_engine.character.inventory):
                        print(f"  {i+1}. {item.name}")
                    item_choice = input("\nChoose item (0 to cancel): ")
                    if item_choice != '0':
                        item_idx = int(item_choice) - 1
                        if 0 <= item_idx < len(game_engine.character.inventory):
                            item = game_engine.character.inventory[item_idx]
                            combat_result = combat.execute_round({'type': 'item', 'item_name': item.name})
                            ui.display_messages(combat_result.get('log', []))
                    
                elif action == '4':
                    # Flee
                    combat_result = combat.execute_round({'type': 'flee'})
                    ui.display_messages(combat_result.get('log', []))
            
            # Handle combat result
            result = game_engine.handle_combat_result(combat_result)
            
            if result.get('victory'):
                sound_manager.play_sound('victory')
            
            if result.get('messages'):
                ui.display_messages(result['messages'])
            
            if result['status'] == 'game_over':
                sound_manager.play_sound('defeat')
                game_engine.game_over = True
                print("\n" + result['message'])
                break
            
            print("\nPress Enter to continue...")
            input()
        
        # Display choices if game is still active
        if not game_engine.game_over:
            ui.display_choices(game_engine.current_node)
            
            # Additional commands
            print("\nOther commands: [S]tatus, [I]tem, [H]elp, [Q]uit")
            
            choice = input("\nYour choice: ").strip().lower()
            
            if choice == 's':
                ui.display_character(game_engine.character)
                print("\nPress Enter to continue...")
                input()
                continue
            elif choice == 'i':
                # Use item from inventory
                sound_manager.play_sound('menu_select')
                if not game_engine.character.inventory:
                    print("\nYour inventory is empty.")
                else:
                    print("\n=== INVENTORY ===")
                    for idx, item in enumerate(game_engine.character.inventory, 1):
                        print(f"{idx}. {item.name} - {item.description}")
                    
                    item_choice = input("\nEnter item number to use (or press Enter to cancel): ").strip()
                    if item_choice:
                        try:
                            item_idx = int(item_choice) - 1
                            if 0 <= item_idx < len(game_engine.character.inventory):
                                item = game_engine.character.inventory[item_idx]
                                effect = game_engine.character.use_item(item.name)
                                if effect:
                                    # Play healing sound for potions
                                    if 'potion' in item.name.lower():
                                        sound_manager.play_sound('healing')
                                    print(f"\n{effect}")
                                else:
                                    print("\nCouldn't use that item.")
                            else:
                                print("\nInvalid item number.")
                        except ValueError:
                            print("\nInvalid input.")
                print("\nPress Enter to continue...")
                input()
                continue
            elif choice == 'h':
                print("\n=== HELP ===")
                print("Enter the number of your choice to make a decision.")
                print("Combat: Choose actions during combat to defeat enemies.")
                print("Commands: S=Status, I=Item, H=Help, Q=Quit")
                print("\nPress Enter to continue...")
                input()
                continue
            elif choice == 'q':
                confirm = input("Are you sure you want to quit? (y/n): ")
                if confirm.lower() == 'y':
                    print("Thanks for playing!")
                    return
                continue
            
            # Process normal choice
            try:
                choice_idx = int(choice) - 1
                result = game_engine.handle_choice(choice_idx)
                
                if result['status'] == 'error' or result['status'] == 'blocked':
                    print(f"\n{result['message']}")
                    print("Press Enter to continue...")
                    input()
                elif result['status'] == 'victory':
                    sound_manager.play_sound('victory')
                    print("\n" + "="*60)
                    print("VICTORY!".center(60))
                    print("="*60)
                    print(f"\n{game_engine.current_node.description}")
                    game_engine.game_over = True
                elif result['status'] == 'defeat':
                    sound_manager.play_sound('defeat')
                    print("\n" + "="*60)
                    print("DEFEAT!".center(60))
                    print("="*60)
                    print(f"\n{game_engine.current_node.description}")
                    game_engine.game_over = True
                    
            except (ValueError, IndexError):
                print("\nInvalid choice! Please enter a valid number.")
                print("Press Enter to continue...")
                input()
    
    print("\n" + "="*60)
    print("GAME OVER")
    print("="*60)
    
    # Stop music when game ends
    sound_manager.stop_music()
    print(f"\nFinal Status:")
    ui.display_character(game_engine.character)

def main():
    """Main function"""
    print("\n" + "="*60)
    print("TEXT ADVENTURE - STEVE JACKSON GAMEBOOK")
    print("="*60)
    print("\nWelcome to the Text Adventure Game!")
    print("This is a gamebook-style adventure using Steve Jackson rules.")
    print("\nPrepare yourself for combat, exploration, and decision-making!")
    
    # Choose adventure
    print("\n" + "="*60)
    print("CHOOSE YOUR ADVENTURE")
    print("="*60)
    # Custom JSON file
    print("\nAvailable adventures:")
    adventures_dir = 'adventures'
    if os.path.exists(adventures_dir):
        json_files = [f for f in os.listdir(adventures_dir) if f.endswith('.json')]
        if json_files:
            for i, filename in enumerate(json_files, 1):
                print(f"  {i}. {filename}")
            file_choice = input("\nEnter file number or path: ")
            try:
                file_idx = int(file_choice) - 1
                if 0 <= file_idx < len(json_files):
                    json_path = os.path.join(adventures_dir, json_files[file_idx])
                else:
                    json_path = file_choice
            except ValueError:
                json_path = file_choice
            
            try:
                adventure = AdventureLoader.load_from_file(json_path)
                print(f"\nLoaded: {adventure.title}")
            except Exception as e:
                print(f"\nError loading adventure: {e}")
                print("Using default adventure instead.")
                adventure = create_sample_adventure()
        else:
            print("No JSON adventures found. Using default.")
            adventure = create_sample_adventure()
    else:
        print("Adventures directory not found. Using default.")
        adventure = create_sample_adventure()
    
    name = input("Enter your character's name: ").strip() or "Hero"
    player = Character(name)

    # Let the player reroll as many times as they want
    while True:
        print(f"\nCharacter status:\n{player}")
        choice = input("Reroll characteristics? [r]eroll / [Enter] accept: ").strip().lower()
        if choice == 'r':
            player.roll_characteristics()
            continue
        break

    print(f"\nWelcome, {player.name}! You start with {player.current_energia} Energia.")

    # Create game engine
    game_engine = game.GameEngine(adventure, player)
    
    # Start playing
    print("\nPress Enter to begin your adventure...")
    input()
    
    play_adventure(game_engine)
    
    print("\nThank you for playing!")

if __name__ == '__main__':
    main()
