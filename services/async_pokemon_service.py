import asyncio

from services.cache_service import (
    api_cache,
    build_pokemon_cache_key,
)
from services.exceptions import (
    ResourceNotFoundError,
)
from services.pokemon_service import (
    build_pokemon,
)


POKEMON_BASE_URL = (
    "https://pokeapi.co/api/v2/pokemon"
)


async def async_get_pokemon(
    identifier,
    client,
    api_client,
    use_cache=True,
):
    normalized_identifier = str(
        identifier
    ).strip().lower()

    if not normalized_identifier:
        return None

    cache_key = build_pokemon_cache_key(
        normalized_identifier
    )

    if use_cache:
        cache_hit, cached_pokemon = (
            api_cache.get(cache_key)
        )

        if cache_hit:
            return cached_pokemon

    url = (
        f"{POKEMON_BASE_URL}/"
        f"{normalized_identifier}"
    )

    try:
        data = await api_client.get_json(
            client,
            url,
        )

    except ResourceNotFoundError:
        return None

    pokemon = build_pokemon(
        data
    )

    if use_cache:
        api_cache.set(
            cache_key,
            pokemon,
        )

        id_cache_key = (
            build_pokemon_cache_key(
                pokemon.id
            )
        )

        if id_cache_key != cache_key:
            api_cache.set(
                id_cache_key,
                pokemon,
            )

        name_cache_key = (
            build_pokemon_cache_key(
                pokemon.name
            )
        )

        if name_cache_key != cache_key:
            api_cache.set(
                name_cache_key,
                pokemon,
            )

    return pokemon


async def async_get_many_pokemon(
    identifiers,
    api_client,
    use_cache=True,
):
    if not identifiers:
        return {
            "pokemon": [],
            "failed_identifiers": [],
            "errors": {},
        }

    async with (
        api_client.create_client()
        as client
    ):
        tasks = [
            async_get_pokemon(
                identifier=identifier,
                client=client,
                api_client=api_client,
                use_cache=use_cache,
            )
            for identifier in identifiers
        ]

        results = await asyncio.gather(
            *tasks,
            return_exceptions=True,
        )

    pokemon_list = []
    failed_identifiers = []
    errors = {}

    for identifier, result in zip(
        identifiers,
        results,
    ):
        identifier_string = str(
            identifier
        )

        if isinstance(
            result,
            Exception,
        ):
            failed_identifiers.append(
                identifier_string
            )

            errors[
                identifier_string
            ] = str(result)

            continue

        if result is None:
            failed_identifiers.append(
                identifier_string
            )

            errors[
                identifier_string
            ] = (
                "Pokémon introuvable."
            )

            continue

        pokemon_list.append(
            result
        )

    return {
        "pokemon": pokemon_list,
        "failed_identifiers": failed_identifiers,
        "errors": errors,
    }