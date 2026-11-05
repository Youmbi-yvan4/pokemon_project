import asyncio

from services.async_type_service import (
    calculate_type_statistics_async,
)
from services.type_service import (
    calculate_type_statistics,
)


TYPE_NAME = "fire"
LIMIT = 10
CONCURRENCY_LIMIT = 5


def display_result(title, result):
    print()
    print(title)
    print("-" * len(title))

    if result is None:
        print("Type introuvable.")
        return

    print(
        "Type :",
        result["type"],
    )

    print(
        "Pokémon disponibles :",
        result["available_count"],
    )

    print(
        "Pokémon analysés :",
        result["analysed_count"],
    )

    print(
        "Réussites :",
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
        "Durée :",
        round(
            result["duration_seconds"],
            2,
        ),
        "seconde(s)",
    )


def main():
    print("Lancement de l'analyse séquentielle...")

    sequential_result = (
        calculate_type_statistics(
            type_identifier=TYPE_NAME,
            limit=LIMIT,
        )
    )

    print()
    print("Lancement de l'analyse asynchrone...")

    async_result = asyncio.run(
        calculate_type_statistics_async(
            type_identifier=TYPE_NAME,
            limit=LIMIT,
            concurrency_limit=CONCURRENCY_LIMIT,
        )
    )

    display_result(
        "RÉSULTAT SÉQUENTIEL",
        sequential_result,
    )

    display_result(
        "RÉSULTAT ASYNCHRONE",
        async_result,
    )

    if (
        sequential_result is None
        or async_result is None
    ):
        return

    sequential_average = round(
        sequential_result["average_hp"],
        6,
    )

    async_average = round(
        async_result["average_hp"],
        6,
    )

    same_average = (
        sequential_average == async_average
    )

    print()
    print("COMPARAISON")
    print("-----------")

    print(
        "Même moyenne de HP :",
        same_average,
    )

    sequential_duration = (
        sequential_result["duration_seconds"]
    )

    async_duration = (
        async_result["duration_seconds"]
    )

    print(
        "Durée séquentielle :",
        round(sequential_duration, 2),
        "seconde(s)",
    )

    print(
        "Durée asynchrone :",
        round(async_duration, 2),
        "seconde(s)",
    )

    if async_duration > 0:
        speedup = (
            sequential_duration / async_duration
        )

        print(
            "Facteur d'accélération observé :",
            round(speedup, 2),
        )

    else:
        print(
            "Le facteur d'accélération ne peut "
            "pas être calculé."
        )


if __name__ == "__main__":
    main()