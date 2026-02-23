"""
Sample adventure copy for SteveJacksonAdventure (package-aware)
"""
try:
    from .node import Adventure, GameNode
except Exception:
    from node import Adventure, GameNode


def create_sample_adventure():
    adventure = Adventure(
        title="The Dark Tower",
        description="A mysterious tower has appeared on the outskirts of town. Strange creatures have been seen emerging from it at night. You have been hired to investigate and stop whatever evil lurks within.",
        starting_node_id="start"
    )

    start = GameNode(
        node_id="start",
        title="The Tower Entrance",
        description=("You stand before a tall, ominous tower built of black stone. \n"
                     "The entrance is a massive wooden door, slightly ajar. Strange sounds echo from within.\n"
                     "A worn path leads around the side of the tower, and you notice a small window high up on the wall.")
    )
    start.add_choice("Enter through the main door", "main_hall")
    start.add_choice("Investigate the side path", "side_path")
    start.add_choice("Try to climb to the window", "window_climb", requirements={'dexterity': 14})
    adventure.add_node(start)

    # Main hall node
    main_hall = GameNode(
        node_id="main_hall",
        title="The Main Hall",
        description=("You push open the heavy door and step into a vast hall. Torches flicker on the walls,"
                     "casting dancing shadows. At the far end, a grand staircase leads upward. You hear the shuffling"
                     "of feet and see two goblins turning to face you with crude weapons drawn!")
    )
    main_hall.add_monster_encounter(['goblin', 'goblin'])
    main_hall.add_choice("Ascend the stairs", "upper_chamber")
    main_hall.add_choice("Search the hall for secrets", "secret_room")
    adventure.add_node(main_hall)

    # Simple adventure variant
    return adventure


def create_simple_adventure():
    adventure = Adventure(
        title="The Goblin Cave",
        description="A group of goblins has been raiding nearby farms. Track them to their cave and stop them!",
        starting_node_id="cave_entrance"
    )

    entrance = GameNode(
        node_id="cave_entrance",
        title="Cave Entrance",
        description="You arrive at the mouth of a dark cave. You can hear goblin voices echoing from within."
    )
    entrance.add_choice("Enter the cave", "goblin_room")
    entrance.add_choice("Leave and return to town", "retreat")
    adventure.add_node(entrance)

    goblin_room = GameNode(
        node_id="goblin_room",
        title="Goblin Den",
        description="Three goblins are sitting around a fire, roasting something unpleasant. They spot you and attack!"
    )
    goblin_room.add_monster_encounter(['goblin', 'goblin', 'goblin'])
    goblin_room.add_treasure(["40 gold pieces", "Potion of Healing"])
    goblin_room.add_choice("Continue deeper into the cave", "boss_room")
    goblin_room.add_choice("Leave the cave victorious", "victory")
    adventure.add_node(goblin_room)

    boss_room = GameNode(
        node_id="boss_room",
        title="Goblin Chief's Chamber",
        description="A large goblin chief sits on a throne made of stolen goods. He roars and charges at you!"
    )
    boss_room.add_monster_encounter('orc')
    boss_room.add_treasure(["100 gold pieces", "Magic sword +1"])
    boss_room.add_choice("Return to town victorious", "victory")
    adventure.add_node(boss_room)

    victory = GameNode(
        node_id="victory",
        title="Victory!",
        description="You have defeated the goblins! The farms are safe once again. Well done, hero!"
    )
    victory.set_victory()
    adventure.add_node(victory)

    retreat = GameNode(
        node_id="retreat",
        title="Retreat",
        description="You decide not to risk it and return to town. The goblin raids continue..."
    )
    retreat.set_defeat()
    adventure.add_node(retreat)

    return adventure
