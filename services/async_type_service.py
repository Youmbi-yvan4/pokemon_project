import time

from services.async_api_client import (
    AsyncAPIClient,
)
from services.async_pokemon_service import (
    async_get_many_pokemon,
)
from services.type_service import (
    get_pokemon_names_by_type,
)


async def calculate_type_statistics_async(
    type_identifier,
    limit=None,
    concurrency_limit=10,
):
    start_time = time.perf_counter()

    normalized_type = str(
        type_identifier
    ).strip().lower()

    if not normalized_type:
        return None

    if concurrency_limit <= 0:
        raise ValueError(
            "La limite de concurrence doit être "
            "supérieure à zéro."
        )

    pokemon_names = get_pokemon_names_by_type(
        normalized_type
    )

    if pokemon_names is None:
        return None

    available_count = len(pokemon_names)

    if limit is not None:
        if limit <= 0:
            raise ValueError(
                "La limite doit être supérieure à zéro."
            )

        selected_names = pokemon_names[:limit]

    else:
        selected_names = pokemon_names

    async_api_client = AsyncAPIClient(
        timeout=10,
        max_retries=3,
        backoff_factor=1,
        concurrency_limit=concurrency_limit,
    )

    retrieval_result = (
        await async_get_many_pokemon(
            identifiers=selected_names,
            api_client=async_api_client,
        )
    )

    pokemon_list = retrieval_result[
        "pokemon"
    ]

    failed_names = retrieval_result[
        "failed_identifiers"
    ]

    errors = retrieval_result["errors"]

    if pokemon_list:
        total_hp = sum(
            pokemon.hp
            for pokemon in pokemon_list
        )

        average_hp = (
            total_hp / len(pokemon_list)
        )

    else:
        average_hp = 0.0

    duration = (
        time.perf_counter() - start_time
    )

    return {
        "type": normalized_type,
        "mode": "Asynchrone",
        "available_count": available_count,
        "analysed_count": len(selected_names),
        "successful_count": len(pokemon_list),
        "failed_count": len(failed_names),
        "failed_names": failed_names,
        "errors": errors,
        "average_hp": average_hp,
        "duration_seconds": duration,
        "concurrency_limit": concurrency_limit,
    }