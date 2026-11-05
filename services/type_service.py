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
    """
    Retrieve the data for a Pokémon type.

    Examples:
        get_type_data("fire")
        get_type_data("dragon")
        get_type_data(10)

    Returns None if the type does not exist.
    """

    normalized_type = str(
        type_identifier
    ).strip().lower()

    if not normalized_type:
        return None

    url = f"{TYPE_BASE_URL}/{normalized_type}"

    try:
        return api_client.get_json(url)

    except ResourceNotFoundError:
        return None


def extract_pokemon_names(type_data):
    """
    Extract the names of the Pokémon associated
    with a type.
    """

    pokemon_names = []

    for item in type_data.get("pokemon", []):
        pokemon_data = item.get(
            "pokemon",
            {},
        )

        pokemon_name = pokemon_data.get(
            "name"
        )

        if pokemon_name:
            pokemon_names.append(
                pokemon_name
            )

    return pokemon_names


def get_pokemon_names_by_type(type_identifier):
    """
    Return the names of all Pokémon associated
    with the requested type.

    Returns None when the type does not exist.
    """

    type_data = get_type_data(
        type_identifier
    )

    if type_data is None:
        return None

    return extract_pokemon_names(
        type_data
    )


def calculate_average_hp(pokemon_names):
    """
    Retrieve each Pokémon sequentially and
    calculate their average HP.

    Only successfully retrieved Pokémon are used
    to calculate the average.
    """

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

        pokemon = get_pokemon(name)

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
        "successful_count": successful_count,
        "failed_count": len(
            failed_names
        ),
        "failed_names": failed_names,
    }


def calculate_type_statistics(
    type_identifier,
    limit=None,
):
    """
    Calculate statistics for Pokémon belonging
    to a given type.

    Parameters
    ----------
    type_identifier:
        Type name or ID, for example "fire",
        "dragon" or 10.

    limit:
        Maximum number of Pokémon to analyse.

        None:
            Analyse every Pokémon returned
            for the requested type.

        Positive integer:
            Analyse only the first N Pokémon.

    Examples
    --------
    Analyse every Fire Pokémon:

        calculate_type_statistics("fire")

    Analyse only the first 10:

        calculate_type_statistics(
            "fire",
            limit=10,
        )
    """

    start_time = time.perf_counter()

    normalized_type = str(
        type_identifier
    ).strip().lower()

    if not normalized_type:
        return None

    pokemon_names = (
        get_pokemon_names_by_type(
            normalized_type
        )
    )

    if pokemon_names is None:
        return None

    available_count = len(
        pokemon_names
    )

    if limit is not None:
        if not isinstance(limit, int):
            raise ValueError(
                "La limite doit être un entier."
            )

        if limit <= 0:
            raise ValueError(
                "La limite doit être supérieure "
                "à zéro."
            )

        selected_names = (
            pokemon_names[:limit]
        )

    else:
        selected_names = pokemon_names

    analysed_count = len(
        selected_names
    )

    hp_statistics = (
        calculate_average_hp(
            selected_names
        )
    )

    duration = (
        time.perf_counter()
        - start_time
    )

    return {
        "type": normalized_type,
        "available_count": available_count,
        "analysed_count": analysed_count,
        "average_hp": hp_statistics[
            "average_hp"
        ],
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