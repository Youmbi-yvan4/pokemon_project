from services.pokemon_service import get_pokemon


def calculate_damage(attacker, defender):
    damage = (
        attacker.attack
        - defender.defense // 2
    )

    return max(1, damage)


def simulate_round(pokemon1, pokemon2):
    damage1 = calculate_damage(
        pokemon1,
        pokemon2,
    )

    damage2 = calculate_damage(
        pokemon2,
        pokemon1,
    )

    return {
        "pokemon1_damage": damage1,
        "pokemon2_damage": damage2,
    }


def determine_winner(
    pokemon1,
    pokemon2,
    total_damage1,
    total_damage2,
):
    if total_damage1 > total_damage2:
        return pokemon1.name

    if total_damage2 > total_damage1:
        return pokemon2.name

    return "Égalité"


def simulate_battle(
    first_identifier,
    second_identifier,
    rounds=5,
):
    if rounds <= 0:
        raise ValueError(
            "Le nombre de tours doit être supérieur à zéro."
        )

    pokemon1 = get_pokemon(
        first_identifier
    )

    pokemon2 = get_pokemon(
        second_identifier
    )

    if pokemon1 is None or pokemon2 is None:
        return None

    total_damage1 = 0
    total_damage2 = 0

    round_details = []

    for round_number in range(
        1,
        rounds + 1,
    ):
        result = simulate_round(
            pokemon1,
            pokemon2,
        )

        total_damage1 += result[
            "pokemon1_damage"
        ]

        total_damage2 += result[
            "pokemon2_damage"
        ]

        round_details.append({
            "round": round_number,
            "pokemon1_damage": result[
                "pokemon1_damage"
            ],
            "pokemon2_damage": result[
                "pokemon2_damage"
            ],
        })

    winner = determine_winner(
        pokemon1,
        pokemon2,
        total_damage1,
        total_damage2,
    )

    return {
        "pokemon_1": pokemon1,
        "pokemon_2": pokemon2,
        "rounds": round_details,
        "total_damage_1": total_damage1,
        "total_damage_2": total_damage2,
        "winner": winner,
    }