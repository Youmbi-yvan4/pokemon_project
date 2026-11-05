from models.pokemon import Pokemon
from services.api_client import APIClient
from services.exceptions import ResourceNotFoundError


BASE_URL = "https://pokeapi.co/api/v2/pokemon"

api_client = APIClient(
    timeout=10,
    max_retries=3,
    backoff_factor=1,
)


def extract_stats(data):
    stats = {}

    for item in data["stats"]:
        stat_name = item["stat"]["name"]
        stat_value = item["base_stat"]

        stats[stat_name] = stat_value

    return stats


def extract_types(data):
    types = []

    for item in data["types"]:
        types.append(item["type"]["name"])

    return types


def get_pokemon(identifier):
    identifier = str(identifier).strip().lower()

    if not identifier:
        return None

    url = f"{BASE_URL}/{identifier}"

    try:
        data = api_client.get_json(url)
    except ResourceNotFoundError:
        return None

    stats = extract_stats(data)

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