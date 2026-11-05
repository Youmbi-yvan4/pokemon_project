from services.battle_service import simulate_battle


result = simulate_battle(
    "pikachu",
    "charizard",
)


if result is None:
    print("Un des Pokémon est introuvable.")

else:
    pokemon1 = result["pokemon_1"]
    pokemon2 = result["pokemon_2"]

    print(
        f"{pokemon1.name.upper()} VS "
        f"{pokemon2.name.upper()}"
    )

    print()

    for round_result in result["rounds"]:
        print(
            f"Tour {round_result['round']}"
        )

        print(
            f"{pokemon1.name} inflige "
            f"{round_result['pokemon1_damage']} "
            "dégâts"
        )

        print(
            f"{pokemon2.name} inflige "
            f"{round_result['pokemon2_damage']} "
            "dégâts"
        )

        print()

    print(
        f"Dégâts totaux {pokemon1.name} :",
        result["total_damage_1"],
    )

    print(
        f"Dégâts totaux {pokemon2.name} :",
        result["total_damage_2"],
    )

    print()
    print("Gagnant :", result["winner"])