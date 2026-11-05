from models.pokemon import Pokemon
from services.api_client import APIClient
from services.cache_service import (
    api_cache,
    build_pokemon_cache_key,
)
from services.exceptions import (
    ResourceNotFoundError,
)


BASE_URL = "https://pokeapi.co/api/v2/pokemon"


api_client = APIClient(
    timeout=10,
    max_retries=3,
    backoff_factor=1,
)


def extract_stats(data):
    stats = {}

    for item in data.get("stats", []):
        stat_name = item["stat"]["name"]
        stat_value = item["base_stat"]

        stats[stat_name] = stat_value

    return stats


def extract_types(data):
    types = []

    for item in data.get("types", []):
        type_name = item["type"]["name"]

        types.append(
            type_name
        )

    return types


def build_pokemon(data):
    stats = extract_stats(data)

    required_stats = [
        "hp",
        "attack",
        "defense",
        "special-attack",
        "special-defense",
        "speed",
    ]

    missing_stats = [
        stat_name
        for stat_name in required_stats
        if stat_name not in stats
    ]

    if missing_stats:
        raise ValueError(
            "Statistiques absentes dans la réponse API : "
            + ", ".join(missing_stats)
        )

    return Pokemon(
        id=data["id"],
        name=data["name"],
        hp=stats["hp"],
        attack=stats["attack"],
        defense=stats["defense"],
        special_attack=stats["special-attack"],
        special_defense=stats["special-defense"],
        speed=stats["speed"],
        types=extract_types(data),
    )


def get_pokemon(
    identifier,
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
        f"{BASE_URL}/"
        f"{normalized_identifier}"
    )

    try:
        data = api_client.get_json(
            url
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

        # On crée également une entrée par ID.
        # Cela peut permettre à un futur appel
        # utilisant cet ID de profiter du cache.
        id_cache_key = build_pokemon_cache_key(
            pokemon.id
        )

        if id_cache_key != cache_key:
            api_cache.set(
                id_cache_key,
                pokemon,
            )

        name_cache_key = build_pokemon_cache_key(
            pokemon.name
        )

        if name_cache_key != cache_key:
            api_cache.set(
                name_cache_key,
                pokemon,
            )

    return pokemon