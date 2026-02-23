"""
Simplified Character for SteveJacksonAdventure
This version removes classes and complex stats — you only pick a name.
"""
import dice


class Character:
    def __init__(self, name):
        self.name = name
        self.max_energia = 18
        self.current_energia = self.max_energia
        self.max_habilidade=9
        self.current_habilidade=self.max_habilidade
        self.max_sorte=9
        self.current_sorte=self.max_sorte
        self.provisions=10
        self.gold=0
        self.inventory = []
        

    def attack_roll(self):
        # Simple attack: 2d6
            roll = dice.d6(2)+self.current_habilidade
            return roll

    def take_damage(self, damage):
        self.current_energia -= damage
        return self.current_energia > 0

    def is_alive(self):
        return self.current_energia > 0

    def heal(self, amount):
        self.current_energia = min(self.max_energia, self.current_energia + amount)

    def add_gold(self, amount):
        self.gold += amount

    def remove_gold(self, amount):
        if self.gold >= amount:
            self.gold -= amount
            return True
        return False

    def test_sorte(self):
        roll = dice.d6(2)
        success = roll <= self.current_sorte
        # Decrease sort (sorte) but never go below 1
        self.current_sorte = max(1, self.current_sorte - 1)
        return success

    def roll_characteristics(self):
        """Roll new characteristics for the character.

        Sets `max_` and `current_` values for habilidade, energia and sorte.
        Returns a tuple (habilidade, energia, sorte).
        """
        # Roll 2d6 for each characteristic
        habilidade = dice.d6(2)
        energia = dice.d6(2)
        sorte = dice.d6(2)

        # Set both max and current values
        self.max_habilidade = habilidade
        self.current_habilidade = habilidade

        self.max_energia = energia
        self.current_energia = energia

        self.max_sorte = sorte
        self.current_sorte = sorte

        return habilidade, energia, sorte
    
    def roll_characteristics(self):
        self.current_habilidade = dice.d6(1) + 6  # Habilidade: 7-12
        self.current_energia = dice.d6(2) + 12     # Energia: 14-24
        self.current_sorte = dice.d6(1) + 6       # Sorte: 7-12
        self.max_habilidade = self.current_habilidade
        self.max_energia = self.current_energia
        self.max_sorte = self.current_sorte
        
    
    # Inventory management
    class Item:
        def __init__(self, name, cost=0):
            self.name = name
            self.cost = cost

        def __str__(self):
            return f"{self.name} ({self.cost} gp)"

    def add_item(self, name, cost=0):
        """Add an item to the character's inventory."""
        item = Character.Item(name, cost)
        self.inventory.append(item)
        return item

    def remove_item(self, name, quantity=1):
        """Remove up to `quantity` items matching `name`. Returns number removed."""
        removed = 0
        remaining = []
        for item in self.inventory:
            if removed < quantity and item.name.lower() == name.lower():
                removed += 1
            else:
                remaining.append(item)
        self.inventory = remaining
        return removed

    def list_inventory(self):
        """Return a list of inventory item strings."""
        return [str(item) for item in self.inventory]

    def __str__(self):
        inv_count = len(self.inventory)
        return (f"{self.name} - Habilidade: {self.current_habilidade}/{self.max_habilidade} | "
            f"Energia: {self.current_energia}/{self.max_energia} | "
            f"Sorte: {self.current_sorte}/{self.max_sorte} | "
            f"Provisions: {self.provisions} | Gold: {self.gold} | "
            f"Inventory: {inv_count} items")
