import requests


BASE_URL = "https://pokeapi.co/api/v2/pokemon"


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

    url = f"{BASE_URL}/{identifier}"

    response = requests.get(url, timeout=10)

    if response.status_code != 200:
        return None

    data = response.json()

    stats = extract_stats(data)

    return {
        "id": data["id"],
        "name": data["name"],
        "hp": stats["hp"],
        "attack": stats["attack"],
        "defense": stats["defense"],
        "special_attack": stats["special-attack"],
        "special_defense": stats["special-defense"],
        "speed": stats["speed"],
        "types": extract_types(data)
    }