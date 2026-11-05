import time

from services.cache_service import (
    CacheService,
)


def main():
    print(
        "=================================="
    )
    print(
        "TEST D'EXPIRATION DU CACHE"
    )
    print(
        "=================================="
    )

    test_cache = CacheService(
        ttl=3,
        max_size=100,
    )

    cache_key = "test:pikachu"

    test_value = {
        "name": "pikachu",
        "hp": 35,
    }

    print()
    print(
        "Insertion dans le cache..."
    )

    test_cache.set(
        cache_key,
        test_value,
    )

    print()

    print(
        "Lecture immédiate :"
    )

    hit, value = test_cache.get(
        cache_key
    )

    print(
        "Cache HIT :",
        hit,
    )

    print(
        "Valeur :",
        value,
    )

    print()

    print(
        "Attente de 4 secondes..."
    )

    time.sleep(4)

    print()

    print(
        "Lecture après expiration :"
    )

    hit, value = test_cache.get(
        cache_key
    )

    print(
        "Cache HIT :",
        hit,
    )

    print(
        "Valeur :",
        value,
    )

    print()

    print(
        "Statistiques finales :"
    )

    statistics = (
        test_cache.get_statistics()
    )

    print(
        statistics
    )


if __name__ == "__main__":
    main()