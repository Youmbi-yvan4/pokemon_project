from services.comparison_service import compare_pokemon


result = compare_pokemon(
    "pikachu",
    "charizard",
)


if result is None:
    print("Un des Pokémon est introuvable.")

else:
    pokemon1 = result["pokemon_1"]
    pokemon2 = result["pokemon_2"]

    print(
        f"{pokemon1.name}: "
        f"HP={pokemon1.hp}, "
        f"attaque={pokemon1.attack}"
    )

    print(
        f"{pokemon2.name}: "
        f"HP={pokemon2.hp}, "
        f"attaque={pokemon2.attack}"
    )

    print()

    print(
        "Meilleurs HP :",
        result["best_hp"],
    )

    print(
        "Meilleure attaque :",
        result["best_attack"],
    )

    print(
        "Différence HP :",
        result["hp_difference"],
    )

    print(
        "Différence attaque :",
        result["attack_difference"],
    )

    print(
        "Plus fort globalement :",
        result["strongest"],
    )