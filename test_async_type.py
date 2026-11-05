import asyncio

from services.async_type_service import (
    calculate_type_statistics_async,
)


async def main():
    result = await calculate_type_statistics_async(
        type_identifier="fire",
        limit=10,
        concurrency_limit=5,
    )

    if result is None:
        print("Type introuvable.")
        return

    print("Type :", result["type"])
    print("Mode :", result["mode"])

    print(
        "Pokémon disponibles :",
        result["available_count"],
    )

    print(
        "Pokémon analysés :",
        result["analysed_count"],
    )

    print(
        "Récupérations réussies :",
        result["successful_count"],
    )

    print(
        "Échecs :",
        result["failed_count"],
    )

    print(
        "HP moyen :",
        round(result["average_hp"], 2),
    )

    print(
        "Limite de concurrence :",
        result["concurrency_limit"],
    )

    print(
        "Durée :",
        round(
            result["duration_seconds"],
            2,
        ),
        "seconde(s)",
    )

    if result["failed_names"]:
        print()
        print("Pokémon non récupérés :")

        for name in result["failed_names"]:
            print("-", name)

            error_message = result[
                "errors"
            ].get(name)

            if error_message:
                print(
                    "  Erreur :",
                    error_message,
                )


if __name__ == "__main__":
    asyncio.run(main())