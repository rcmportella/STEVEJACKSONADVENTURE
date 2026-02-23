"""
Simplified Monster for SteveJacksonAdventure
"""
import dice


class Monster:
    def __init__(self, name, habilidade=5, energia=4):
        self.name = name
        self.energia = energia
        self.habilidade = habilidade

    def attack_roll(self):
        # Simple attack: 2d6
            roll = dice.d6(2)+self.habilidade
            return roll

    def take_damage(self, damage):
        self.energia -= damage
        return self.energia > 0

    def is_alive(self):
        return self.energia > 0

    def __str__(self):
        return f"{self.name} - Energia: {self.energia} | Habilidade: {self.habilidade}"


class Goblin(Monster):
    def __init__(self):
        super().__init__(name="Goblin", habilidade=5, energia=4)


def create_monster(monster_type):
    name = str(monster_type or "monster").strip()
    key = name.lower().replace(" ", "_")

    presets = {
        "goblin": {"name": "Goblin", "habilidade": 5, "energia": 4},
        "orc": {"name": "Orc", "habilidade": 6, "energia": 6},
        "troll": {"name": "Troll", "habilidade": 8, "energia": 10},
        "ogro": {"name": "Ogro", "habilidade": 7, "energia": 8},
        "abelhas_assassinas": {"name": "Abelhas Assassinas", "habilidade": 6, "energia": 6},
    }

    data = presets.get(key)
    if data:
        return Monster(
            name=data["name"],
            habilidade=data["habilidade"],
            energia=data["energia"],
        )

    pretty_name = name.replace("_", " ").title()
    return Monster(name=pretty_name, habilidade=5, energia=4)
