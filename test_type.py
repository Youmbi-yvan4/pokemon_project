from services.type_service import (
    calculate_type_statistics,
)


result = calculate_type_statistics("fire")

if result is None:
    print("Type introuvable ou incorrect.")

else:
    print("Type :", result["type"])
    print(
        "Nombre total :",
        result["total_count"],
    )
    print(
        "Pokémon récupérés :",
        result["successful_count"],
    )
    print(
        "Échecs :",
        result["failed_count"],
    )
    print(
        "Moyenne HP :",
        round(result["average_hp"], 2),
    )
    print(
        "Durée :",
        round(result["duration_seconds"], 2),
        "seconde(s)",
    )

    if result["failed_names"]:
        print(
            "Pokémon non récupérés :",
            result["failed_names"],
        )