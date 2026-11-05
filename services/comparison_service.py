from services.pokemon_service import get_pokemon


def compare_stat(pokemon1, pokemon2, attribute):
    value1 = getattr(pokemon1, attribute)
    value2 = getattr(pokemon2, attribute)

    if value1 > value2:
        return pokemon1.name

    if value2 > value1:
        return pokemon2.name

    return "Égalité"


def get_strongest(pokemon1, pokemon2):
    score1 = pokemon1.strength_score()
    score2 = pokemon2.strength_score()

    if score1 > score2:
        return pokemon1.name

    if score2 > score1:
        return pokemon2.name

    return "Égalité"


def compare_pokemon(first_identifier, second_identifier):
    pokemon1 = get_pokemon(first_identifier)
    pokemon2 = get_pokemon(second_identifier)

    if pokemon1 is None or pokemon2 is None:
        return None

    best_hp = compare_stat(
        pokemon1,
        pokemon2,
        "hp",
    )

    best_attack = compare_stat(
        pokemon1,
        pokemon2,
        "attack",
    )

    hp_difference = abs(
        pokemon1.hp - pokemon2.hp
    )

    attack_difference = abs(
        pokemon1.attack - pokemon2.attack
    )

    strongest = get_strongest(
        pokemon1,
        pokemon2,
    )

    return {
        "pokemon_1": pokemon1,
        "pokemon_2": pokemon2,
        "best_hp": best_hp,
        "best_attack": best_attack,
        "hp_difference": hp_difference,
        "attack_difference": attack_difference,
        "strongest": strongest,
    }