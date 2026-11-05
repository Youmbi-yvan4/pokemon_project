import time

from services.api_client import APIClient
from services.exceptions import ResourceNotFoundError
from services.pokemon_service import get_pokemon


TYPE_BASE_URL = "https://pokeapi.co/api/v2/type"

api_client = APIClient(
    timeout=10,
    max_retries=3,
    backoff_factor=1,
)


def get_type_data(type_identifier):
    type_identifier = str(
        type_identifier
    ).strip().lower()

    if not type_identifier:
        return None

    url = f"{TYPE_BASE_URL}/{type_identifier}"

    try:
        return api_client.get_json(url)
    except ResourceNotFoundError:
        return None


def extract_pokemon_names(type_data):
    names = []

    for item in type_data.get("pokemon", []):
        pokemon_name = item["pokemon"]["name"]
        names.append(pokemon_name)

    return names


def get_pokemon_names_by_type(type_identifier):
    type_data = get_type_data(type_identifier)

    if type_data is None:
        return None

    return extract_pokemon_names(type_data)


def calculate_average_hp(pokemon_names):
    total_hp = 0
    successful_count = 0
    failed_names = []

    for name in pokemon_names:
        pokemon = get_pokemon(name)

        if pokemon is None:
            failed_names.append(name)
            continue

        total_hp += pokemon.hp
        successful_count += 1

    if successful_count == 0:
        average_hp = 0.0
    else:
        average_hp = total_hp / successful_count

    return {
        "average_hp": average_hp,
        "successful_count": successful_count,
        "failed_count": len(failed_names),
        "failed_names": failed_names,
    }


def calculate_type_statistics(type_identifier):
    start_time = time.perf_counter()

    normalized_type = str(
        type_identifier
    ).strip().lower()

    if not normalized_type:
        return None

    pokemon_names = get_pokemon_names_by_type(
        normalized_type
    )

    if pokemon_names is None:
        return None

    hp_statistics = calculate_average_hp(
        pokemon_names
    )

    duration = time.perf_counter() - start_time

    return {
        "type": normalized_type,
        "total_count": len(pokemon_names),
        "average_hp": hp_statistics["average_hp"],
        "successful_count": hp_statistics[
            "successful_count"
        ],
        "failed_count": hp_statistics[
            "failed_count"
        ],
        "failed_names": hp_statistics[
            "failed_names"
        ],
        "duration_seconds": duration,
    }