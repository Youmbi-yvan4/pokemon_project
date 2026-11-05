import time

from services.cache_service import (
    api_cache,
)
from services.pokemon_service import (
    get_pokemon,
)


def display_statistics():
    statistics = (
        api_cache.get_statistics()
    )

    print(
        "Cache hits :",
        statistics["hits"],
    )

    print(
        "Cache misses :",
        statistics["misses"],
    )

    print(
        "Écritures :",
        statistics["sets"],
    )

    print(
        "Entrées en cache :",
        statistics["size"],
    )

    print(
        "TTL :",
        statistics["ttl_seconds"],
        "seconde(s)",
    )

    print(
        "Taux de hit :",
        f"{statistics['hit_rate']:.2f} %",
    )


def main():
    print(
        "=================================="
    )
    print(
        "TEST DU CACHE POKÉMON"
    )
    print(
        "=================================="
    )

    print()
    print(
        "Nettoyage du cache..."
    )

    api_cache.clear()

    print()

    # --------------------------------------------------------
    # PREMIER APPEL
    # --------------------------------------------------------

    print(
        "PREMIER APPEL"
    )
    print(
        "-------------"
    )

    start_time = (
        time.perf_counter()
    )

    pokemon1 = get_pokemon(
        "pikachu"
    )

    first_duration = (
        time.perf_counter()
        - start_time
    )

    if pokemon1 is None:
        print(
            "Impossible de récupérer Pikachu."
        )
        return

    print(
        "Pokémon :",
        pokemon1.name,
    )

    print(
        "Durée :",
        f"{first_duration:.6f}",
        "seconde(s)",
    )

    print()

    display_statistics()

    print()

    # --------------------------------------------------------
    # DEUXIÈME APPEL
    # --------------------------------------------------------

    print(
        "DEUXIÈME APPEL"
    )
    print(
        "--------------"
    )

    start_time = (
        time.perf_counter()
    )

    pokemon2 = get_pokemon(
        "pikachu"
    )

    second_duration = (
        time.perf_counter()
        - start_time
    )

    if pokemon2 is None:
        print(
            "Impossible de récupérer Pikachu."
        )
        return

    print(
        "Pokémon :",
        pokemon2.name,
    )

    print(
        "Durée :",
        f"{second_duration:.6f}",
        "seconde(s)",
    )

    print()

    display_statistics()

    print()

    # --------------------------------------------------------
    # COMPARAISON
    # --------------------------------------------------------

    print(
        "COMPARAISON"
    )
    print(
        "-----------"
    )

    print(
        "Premier appel :",
        f"{first_duration:.6f}",
        "s",
    )

    print(
        "Deuxième appel :",
        f"{second_duration:.6f}",
        "s",
    )

    if second_duration > 0:
        speedup = (
            first_duration
            / second_duration
        )

        print(
            "Facteur d'accélération observé :",
            f"{speedup:.2f}",
        )

    print()

    print(
        "Le premier appel doit provoquer "
        "un cache MISS."
    )

    print(
        "Le second appel identique doit "
        "provoquer un cache HIT."
    )


if __name__ == "__main__":
    main()