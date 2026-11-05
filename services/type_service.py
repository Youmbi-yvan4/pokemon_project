import time

from services.api_client import APIClient
from services.cache_service import (
    api_cache,
    build_type_cache_key,
)
from services.exceptions import (
    ResourceNotFoundError,
)
from services.pokemon_service import (
    get_pokemon,
)


TYPE_BASE_URL = (
    "https://pokeapi.co/api/v2/type"
)


api_client = APIClient(
    timeout=10,
    max_retries=3,
    backoff_factor=1,
)


def get_type_data(
    type_identifier,
    use_cache=True,
):
    normalized_type = str(
        type_identifier
    ).strip().lower()

    if not normalized_type:
        return None

    cache_key = build_type_cache_key(
        normalized_type
    )

    if use_cache:
        cache_hit, cached_data = (
            api_cache.get(
                cache_key
            )
        )

        if cache_hit:
            return cached_data

    url = (
        f"{TYPE_BASE_URL}/"
        f"{normalized_type}"
    )

    try:
        data = api_client.get_json(
            url
        )

    except ResourceNotFoundError:
        return None

    if use_cache:
        api_cache.set(
            cache_key,
            data,
        )

    return data


def extract_pokemon_names(
    type_data,
):
    pokemon_names = []

    for item in type_data.get(
        "pokemon",
        [],
    ):
        pokemon_data = item.get(
            "pokemon",
            {},
        )

        pokemon_name = (
            pokemon_data.get(
                "name"
            )
        )

        if pokemon_name:
            pokemon_names.append(
                pokemon_name
            )

    return pokemon_names


def get_pokemon_names_by_type(
    type_identifier,
    use_cache=True,
):
    type_data = get_type_data(
        type_identifier,
        use_cache=use_cache,
    )

    if type_data is None:
        return None

    return extract_pokemon_names(
        type_data
    )


def calculate_average_hp(
    pokemon_names,
    use_cache=True,
):
    total_hp = 0
    successful_count = 0
    failed_names = []

    total_pokemon = len(
        pokemon_names
    )

    for index, name in enumerate(
        pokemon_names,
        start=1,
    ):
        print(
            f"[{index}/{total_pokemon}] "
            f"Récupération de {name}"
        )

        pokemon = get_pokemon(
            name,
            use_cache=use_cache,
        )

        if pokemon is None:
            failed_names.append(
                name
            )

            continue

        total_hp += pokemon.hp
        successful_count += 1

    if successful_count == 0:
        average_hp = 0.0

    else:
        average_hp = (
            total_hp
            / successful_count
        )

    return {
        "average_hp": average_hp,
        "successful_count": (
            successful_count
        ),
        "failed_count": len(
            failed_names
        ),
        "failed_names": failed_names,
    }


def calculate_type_statistics(
    type_identifier,
    limit=None,
    use_cache=True,
):
    start_time = time.perf_counter()

    normalized_type = str(
        type_identifier
    ).strip().lower()

    if not normalized_type:
        return None

    cache_before = (
        api_cache.get_statistics()
    )

    pokemon_names = (
        get_pokemon_names_by_type(
            normalized_type,
            use_cache=use_cache,
        )
    )

    if pokemon_names is None:
        return None

    available_count = len(
        pokemon_names
    )

    if limit is not None:
        if not isinstance(
            limit,
            int,
        ):
            raise ValueError(
                "La limite doit être "
                "un entier."
            )

        if limit <= 0:
            raise ValueError(
                "La limite doit être "
                "supérieure à zéro."
            )

        selected_names = (
            pokemon_names[:limit]
        )

    else:
        selected_names = (
            pokemon_names
        )

    analysed_count = len(
        selected_names
    )

    hp_statistics = (
        calculate_average_hp(
            selected_names,
            use_cache=use_cache,
        )
    )

    duration = (
        time.perf_counter()
        - start_time
    )

    cache_after = (
        api_cache.get_statistics()
    )

    cache_hits = (
        cache_after["hits"]
        - cache_before["hits"]
    )

    cache_misses = (
        cache_after["misses"]
        - cache_before["misses"]
    )

    return {
        "type": normalized_type,
        "mode": "Séquentiel",
        "available_count": (
            available_count
        ),
        "analysed_count": (
            analysed_count
        ),
        "average_hp": (
            hp_statistics[
                "average_hp"
            ]
        ),
        "successful_count": (
            hp_statistics[
                "successful_count"
            ]
        ),
        "failed_count": (
            hp_statistics[
                "failed_count"
            ]
        ),
        "failed_names": (
            hp_statistics[
                "failed_names"
            ]
        ),
        "duration_seconds": duration,
        "cache_enabled": use_cache,
        "cache_hits": cache_hits,
        "cache_misses": cache_misses,
    }