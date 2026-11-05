from dataclasses import dataclass


@dataclass
class Pokemon:
    id: int
    name: str
    hp: int
    attack: int
    defense: int
    special_attack: int
    special_defense: int
    speed: int
    types: list[str]

    def strength_score(self):
        return self.hp + self.attack