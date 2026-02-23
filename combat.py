"""
Simple combat loop for SteveJacksonAdventure
"""
import dice


class Combat:
    def __init__(self, character, monster):
        self.character = character
        if isinstance(monster, list):
            self.monsters = monster
        else:
            self.monsters = [monster]
        self.round = 0

    def _alive_monsters(self):
        return [monster for monster in self.monsters if monster.is_alive()]

    def get_alive_monsters(self):
        return list(self._alive_monsters())

    def get_combat_summary(self):
        lines = [
            f"Round: {self.round}",
            f"Hero Energia: {self.character.current_energia}/{self.character.max_energia}",
            "Monsters:",
        ]
        for idx, monster in enumerate(self.monsters, 1):
            status = "alive" if monster.is_alive() else "defeated"
            lines.append(f"  {idx}. {monster.name} - Energia {monster.energia} ({status})")
        return "\n".join(lines)

    def _ask_luck_choice(self, prompt):
        while True:
            choice = input(prompt).strip().lower()
            if choice in ('y', 'n'):
                return choice == 'y'
            print("Please type 'y' or 'n'.")

    def _apply_player_damage(self, log, target, use_luck=False, interactive=False):
        if use_luck or (interactive and self._ask_luck_choice("You hit! Test sorte (luck) to try for extra damage? (y/n): ")):
            lucky = self.character.test_sorte()
            if lucky:
                damage = 3
                log.append("Lucky! You deal 3 damage.")
            else:
                damage = 1
                log.append("Unlucky! You deal only 1 damage.")
        else:
            damage = 2

        target.take_damage(damage)
        log.append(f"You hit {target.name} for {damage} damage! ({target.energia} HP left)")
        if not target.is_alive():
            log.append(f"{target.name} is defeated!")

    def _apply_monster_damage(self, log, attacker, use_luck=False, interactive=False):
        if use_luck or (interactive and self._ask_luck_choice(f"{attacker.name} hits! Test sorte (luck) to reduce damage? (y/n): ")):
            lucky = self.character.test_sorte()
            if lucky:
                damage = 1
                log.append("Lucky! You take only 1 point of damage.")
            else:
                damage = 3
                log.append("Unlucky! You take 3 points of damage.")
        else:
            damage = 2

        self.character.take_damage(damage)
        log.append(f"{attacker.name} hits you for {damage} damage! ({self.character.current_energia} HP left)")

    def _apply_support_damage(self, log, attacker, use_luck=False, interactive=False):
        if use_luck or (interactive and self._ask_luck_choice(f"{attacker.name} support-hit! Test sorte (luck) to reduce damage? (y/n): ")):
            lucky = self.character.test_sorte()
            if lucky:
                damage = 0
                log.append("Lucky! You avoid the support hit.")
            else:
                damage = 2
                log.append("Unlucky! The support hit hurts more (2 damage).")
        else:
            damage = 1

        if damage > 0:
            self.character.take_damage(damage)
            log.append(f"{attacker.name} lands a support hit for {damage} damage! ({self.character.current_energia} HP left)")
        else:
            log.append(f"{attacker.name} support hit is avoided.")

    def execute_round(self, action=None, interactive=False):
        action = action or {'type': 'attack'}
        log = []

        if not self.character.is_alive():
            return {'status': 'defeat', 'log': ["You have been defeated..."]}

        alive = self._alive_monsters()
        if not alive:
            return {'status': 'victory', 'log': ["All monsters are defeated!"], 'rewards': {}}

        action_type = action.get('type', 'attack')

        if action_type == 'flee':
            flee_roll = dice.d6(1)
            if flee_roll >= 5:
                return {'status': 'fled', 'log': ["You escape from combat!"], 'message': "You fled the battle."}
            log.append("You fail to flee!")

        if action_type == 'item':
            log.append("Using items in combat is not implemented in this simplified system.")

        self.round += 1
        log.append(f"--- Round {self.round} ---")

        alive = self._alive_monsters()
        if not alive:
            return {'status': 'victory', 'log': log + ["All monsters are defeated!"], 'rewards': {}}

        target = alive[0]
        target_index = action.get('target_index')
        if isinstance(target_index, int) and 0 <= target_index < len(alive):
            target = alive[target_index]

        log.append(f"Primary duel target: {target.name}")

        player_attack = self.character.attack_roll()
        monster_attack = target.attack_roll()
        if player_attack >= monster_attack:
            self._apply_player_damage(
                log,
                target,
                use_luck=action.get('use_luck_attack', False),
                interactive=interactive,
            )
        else:
            self._apply_monster_damage(
                log,
                target,
                use_luck=action.get('use_luck_defense', False),
                interactive=interactive,
            )

        if self.character.is_alive():
            support_attackers = [monster for monster in self._alive_monsters() if monster is not target]
            if support_attackers:
                log.append("Other enemies press in:")
            for attacker in support_attackers:
                hero_defense = self.character.attack_roll()
                attacker_roll = attacker.attack_roll()
                if attacker_roll > hero_defense:
                    self._apply_support_damage(
                        log,
                        attacker,
                        use_luck=action.get('use_luck_support_defense', False),
                        interactive=interactive,
                    )
                else:
                    log.append(f"{attacker.name} misses with a support attack.")
                if not self.character.is_alive():
                    break

        if not self.character.is_alive():
            return {'status': 'defeat', 'log': log + ["You have been defeated..."]}

        if not self._alive_monsters():
            return {'status': 'victory', 'log': log + ["All monsters are defeated!"], 'rewards': {}}

        return {'status': 'ongoing', 'log': log}

    def run(self):
        while True:
            alive = self._alive_monsters()
            if not self.character.is_alive():
                print("\nYou have been defeated...")
                return 'defeat'
            if not alive:
                print("\nAll monsters are defeated!")
                return 'victory'

            print("\nTargets:")
            for idx, monster in enumerate(alive, 1):
                print(f"  [{idx}] {monster.name} ({monster.energia} energia)")

            selected = input("Choose target number (Enter for first): ").strip()
            target_index = 0
            if selected.isdigit():
                parsed = int(selected) - 1
                if 0 <= parsed < len(alive):
                    target_index = parsed

            result = self.execute_round({'type': 'attack', 'target_index': target_index}, interactive=True)
            for line in result.get('log', []):
                print(line)

            if result['status'] == 'victory':
                return 'victory'
            if result['status'] == 'defeat':
                return 'defeat'
            if result['status'] == 'fled':
                return 'fled'
