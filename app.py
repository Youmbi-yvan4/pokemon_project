import asyncio
import time

import streamlit as st

from services.async_type_service import (
    calculate_type_statistics_async,
)
from services.battle_service import (
    simulate_battle,
)
from services.cache_service import (
    api_cache,
)
from services.comparison_service import (
    compare_pokemon,
)
from services.exceptions import (
    APIError,
)
from services.pokemon_service import (
    get_pokemon,
)
from services.type_service import (
    calculate_type_statistics,
)


# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Pokémon Analyzer",
    page_icon="⚡",
    layout="wide",
)

st.title(
    "⚡ Pokémon Analyzer"
)

st.write(
    "Recherchez, comparez et analysez "
    "les Pokémon grâce à PokéAPI."
)

st.divider()


# ============================================================
# ONGLETS
# ============================================================

(
    tab_search,
    tab_compare,
    tab_type,
    tab_battle,
    tab_cache,
) = st.tabs(
    [
        "🔎 Recherche",
        "⚖️ Comparaison",
        "📊 Analyse par type",
        "⚔️ Combat",
        "🗄️ Cache",
    ]
)


# ============================================================
# RECHERCHE
# ============================================================

with tab_search:
    st.header(
        "🔎 Rechercher un Pokémon"
    )

    identifier = st.text_input(
        "Nom ou ID du Pokémon",
        placeholder="Exemple : pikachu ou 25",
        key="search_pokemon",
    )

    if st.button(
        "Rechercher",
        key="search_button",
    ):
        if not identifier.strip():
            st.warning(
                "Veuillez saisir un Pokémon."
            )

        else:
            try:
                with st.spinner(
                    "Récupération...",
                    show_time=True,
                ):
                    pokemon = get_pokemon(
                        identifier
                    )

                if pokemon is None:
                    st.error(
                        "Pokémon introuvable."
                    )

                else:
                    st.success(
                        "Pokémon trouvé."
                    )

                    st.subheader(
                        pokemon.name.capitalize()
                    )

                    st.write(
                        "**ID :**",
                        pokemon.id,
                    )

                    st.write(
                        "**Type(s) :**",
                        ", ".join(
                            type_name.capitalize()
                            for type_name
                            in pokemon.types
                        ),
                    )

                    col1, col2, col3 = (
                        st.columns(3)
                    )

                    with col1:
                        st.metric(
                            "❤️ HP",
                            pokemon.hp,
                        )

                        st.metric(
                            "✨ Attaque spéciale",
                            pokemon.special_attack,
                        )

                    with col2:
                        st.metric(
                            "⚔️ Attaque",
                            pokemon.attack,
                        )

                        st.metric(
                            "🔰 Défense spéciale",
                            pokemon.special_defense,
                        )

                    with col3:
                        st.metric(
                            "🛡️ Défense",
                            pokemon.defense,
                        )

                        st.metric(
                            "💨 Vitesse",
                            pokemon.speed,
                        )

            except APIError as error:
                st.error(
                    f"Erreur API : {error}"
                )

            except Exception as error:
                st.error(
                    "Erreur inattendue : "
                    f"{error}"
                )


# ============================================================
# COMPARAISON
# ============================================================

with tab_compare:
    st.header(
        "⚖️ Comparer deux Pokémon"
    )

    col1, col2 = st.columns(2)

    with col1:
        first_pokemon = st.text_input(
            "Premier Pokémon",
            placeholder="pikachu",
            key="compare_first",
        )

    with col2:
        second_pokemon = st.text_input(
            "Deuxième Pokémon",
            placeholder="charizard",
            key="compare_second",
        )

    if st.button(
        "Comparer",
        key="compare_button",
    ):
        if (
            not first_pokemon.strip()
            or not second_pokemon.strip()
        ):
            st.warning(
                "Veuillez saisir deux Pokémon."
            )

        else:
            try:
                with st.spinner(
                    "Comparaison...",
                    show_time=True,
                ):
                    result = compare_pokemon(
                        first_pokemon,
                        second_pokemon,
                    )

                if result is None:
                    st.error(
                        "Un Pokémon est introuvable."
                    )

                else:
                    pokemon1 = (
                        result["pokemon_1"]
                    )

                    pokemon2 = (
                        result["pokemon_2"]
                    )

                    col1, col2 = (
                        st.columns(2)
                    )

                    with col1:
                        st.subheader(
                            pokemon1.name.capitalize()
                        )

                        st.metric(
                            "HP",
                            pokemon1.hp,
                        )

                        st.metric(
                            "Attaque",
                            pokemon1.attack,
                        )

                        st.metric(
                            "Score HP + attaque",
                            pokemon1.strength_score(),
                        )

                    with col2:
                        st.subheader(
                            pokemon2.name.capitalize()
                        )

                        st.metric(
                            "HP",
                            pokemon2.hp,
                        )

                        st.metric(
                            "Attaque",
                            pokemon2.attack,
                        )

                        st.metric(
                            "Score HP + attaque",
                            pokemon2.strength_score(),
                        )

                    st.divider()

                    st.write(
                        "**Meilleurs HP :**",
                        result["best_hp"],
                    )

                    st.write(
                        "**Meilleure attaque :**",
                        result["best_attack"],
                    )

                    st.write(
                        "**Différence HP :**",
                        result[
                            "hp_difference"
                        ],
                    )

                    st.write(
                        "**Différence attaque :**",
                        result[
                            "attack_difference"
                        ],
                    )

                    st.success(
                        "Plus fort selon HP + attaque : "
                        f"{result['strongest']}"
                    )

            except APIError as error:
                st.error(
                    f"Erreur API : {error}"
                )

            except Exception as error:
                st.error(
                    "Erreur inattendue : "
                    f"{error}"
                )


# ============================================================
# ANALYSE PAR TYPE
# ============================================================

with tab_type:
    st.header(
        "📊 Analyse par type"
    )

    type_name = st.text_input(
        "Type Pokémon",
        placeholder="fire, water, dragon...",
        key="type_name",
    )

    use_limit = st.checkbox(
        "Limiter le nombre de Pokémon",
        value=True,
        key="use_type_limit",
    )

    limit_value = st.number_input(
        "Nombre maximal à analyser",
        min_value=1,
        value=10,
        step=1,
        disabled=not use_limit,
        key="type_limit",
    )

    if use_limit:
        selected_limit = int(
            limit_value
        )
    else:
        selected_limit = None

    execution_mode = st.radio(
        "Mode d'exécution",
        [
            "Séquentiel",
            "Asynchrone",
        ],
        horizontal=True,
        key="type_execution_mode",
    )

    concurrency_limit = st.slider(
        "Requêtes simultanées",
        min_value=1,
        max_value=20,
        value=5,
        disabled=(
            execution_mode
            == "Séquentiel"
        ),
        key="concurrency_limit",
    )

    use_cache = st.checkbox(
        "Utiliser le cache",
        value=True,
        key="analysis_cache",
    )

    if st.button(
        "Analyser",
        key="analyse_button",
    ):
        if not type_name.strip():
            st.warning(
                "Veuillez saisir un type."
            )

        else:
            try:
                with st.spinner(
                    "Analyse en cours...",
                    show_time=True,
                ):
                    if (
                        execution_mode
                        == "Séquentiel"
                    ):
                        result = (
                            calculate_type_statistics(
                                type_identifier=type_name,
                                limit=selected_limit,
                                use_cache=use_cache,
                            )
                        )

                    else:
                        result = asyncio.run(
                            calculate_type_statistics_async(
                                type_identifier=type_name,
                                limit=selected_limit,
                                concurrency_limit=int(
                                    concurrency_limit
                                ),
                                use_cache=use_cache,
                            )
                        )

                if result is None:
                    st.error(
                        "Type introuvable."
                    )

                else:
                    st.success(
                        "Analyse terminée."
                    )

                    st.write(
                        "**Mode :**",
                        result["mode"],
                    )

                    col1, col2, col3 = (
                        st.columns(3)
                    )

                    with col1:
                        st.metric(
                            "Disponibles",
                            result[
                                "available_count"
                            ],
                        )

                    with col2:
                        st.metric(
                            "Analysés",
                            result[
                                "analysed_count"
                            ],
                        )

                    with col3:
                        st.metric(
                            "HP moyen",
                            round(
                                result[
                                    "average_hp"
                                ],
                                2,
                            ),
                        )

                    col4, col5, col6 = (
                        st.columns(3)
                    )

                    with col4:
                        st.metric(
                            "Réussites",
                            result[
                                "successful_count"
                            ],
                        )

                    with col5:
                        st.metric(
                            "Échecs",
                            result[
                                "failed_count"
                            ],
                        )

                    with col6:
                        st.metric(
                            "Durée",
                            (
                                f"{result['duration_seconds']:.2f} s"
                            ),
                        )

                    st.divider()

                    st.subheader(
                        "Cache pendant cette analyse"
                    )

                    cache_col1, cache_col2 = (
                        st.columns(2)
                    )

                    with cache_col1:
                        st.metric(
                            "Cache hits",
                            result[
                                "cache_hits"
                            ],
                        )

                    with cache_col2:
                        st.metric(
                            "Cache misses",
                            result[
                                "cache_misses"
                            ],
                        )

                    st.write(
                        "**Cache activé :**",
                        (
                            "Oui"
                            if result[
                                "cache_enabled"
                            ]
                            else "Non"
                        ),
                    )

            except APIError as error:
                st.error(
                    f"Erreur API : {error}"
                )

            except ValueError as error:
                st.warning(
                    str(error)
                )

            except Exception as error:
                st.error(
                    "Erreur inattendue : "
                    f"{error}"
                )


# ============================================================
# COMBAT
# ============================================================

with tab_battle:
    st.header(
        "⚔️ Combat Pokémon"
    )

    col1, col2 = st.columns(2)

    with col1:
        fighter1 = st.text_input(
            "Pokémon 1",
            placeholder="pikachu",
            key="battle_first",
        )

    with col2:
        fighter2 = st.text_input(
            "Pokémon 2",
            placeholder="charizard",
            key="battle_second",
        )

    if st.button(
        "Lancer le combat",
        key="battle_button",
    ):
        if (
            not fighter1.strip()
            or not fighter2.strip()
        ):
            st.warning(
                "Veuillez saisir deux Pokémon."
            )

        else:
            try:
                with st.spinner(
                    "Combat...",
                    show_time=True,
                ):
                    result = simulate_battle(
                        fighter1,
                        fighter2,
                        rounds=5,
                    )

                if result is None:
                    st.error(
                        "Un Pokémon est introuvable."
                    )

                else:
                    pokemon1 = (
                        result["pokemon_1"]
                    )

                    pokemon2 = (
                        result["pokemon_2"]
                    )

                    st.subheader(
                        f"{pokemon1.name.capitalize()} "
                        "VS "
                        f"{pokemon2.name.capitalize()}"
                    )

                    for round_result in (
                        result["rounds"]
                    ):
                        with st.expander(
                            "Tour "
                            f"{round_result['round']}"
                        ):
                            st.write(
                                f"{pokemon1.name.capitalize()} : "
                                f"{round_result['pokemon1_damage']} "
                                "dégâts"
                            )

                            st.write(
                                f"{pokemon2.name.capitalize()} : "
                                f"{round_result['pokemon2_damage']} "
                                "dégâts"
                            )

                    st.divider()

                    col1, col2 = st.columns(2)

                    with col1:
                        st.metric(
                            pokemon1.name.capitalize(),
                            result[
                                "total_damage_1"
                            ],
                        )

                    with col2:
                        st.metric(
                            pokemon2.name.capitalize(),
                            result[
                                "total_damage_2"
                            ],
                        )

                    if (
                        result["winner"]
                        == "Égalité"
                    ):
                        st.warning(
                            "Combat nul."
                        )

                    else:
                        st.success(
                            "🏆 Gagnant : "
                            f"{result['winner'].capitalize()}"
                        )

            except APIError as error:
                st.error(
                    f"Erreur API : {error}"
                )

            except Exception as error:
                st.error(
                    "Erreur inattendue : "
                    f"{error}"
                )


# ============================================================
# CACHE
# ============================================================

with tab_cache:
    st.header(
        "🗄️ Cache API"
    )

    st.write(
        "Le cache conserve les réponses pendant "
        "1 heure afin d'éviter les appels API répétitifs."
    )

    statistics = (
        api_cache.get_statistics()
    )

    col1, col2, col3, col4 = (
        st.columns(4)
    )

    with col1:
        st.metric(
            "Cache hits",
            statistics["hits"],
        )

    with col2:
        st.metric(
            "Cache misses",
            statistics["misses"],
        )

    with col3:
        st.metric(
            "Entrées",
            statistics["size"],
        )

    with col4:
        st.metric(
            "Hit rate",
            f"{statistics['hit_rate']:.1f} %",
        )

    st.write(
        "**TTL :**",
        statistics[
            "ttl_seconds"
        ],
        "secondes",
    )

    st.write(
        "**Taille maximale :**",
        statistics[
            "max_size"
        ],
        "entrées",
    )

    st.divider()

    st.subheader(
        "Démonstration du cache"
    )

    cache_demo_pokemon = (
        st.text_input(
            "Pokémon à utiliser pour la démonstration",
            value="pikachu",
            key="cache_demo_pokemon",
        )
    )

    if st.button(
        "Tester le cache",
        key="test_cache_button",
    ):
        if not cache_demo_pokemon.strip():
            st.warning(
                "Veuillez saisir un Pokémon."
            )

        else:
            try:
                # Nettoyage avant le test afin
                # de garantir un premier MISS.
                api_cache.clear()

                start = (
                    time.perf_counter()
                )

                pokemon1 = get_pokemon(
                    cache_demo_pokemon
                )

                first_duration = (
                    time.perf_counter()
                    - start
                )

                stats_after_first = (
                    api_cache.get_statistics()
                )

                start = (
                    time.perf_counter()
                )

                pokemon2 = get_pokemon(
                    cache_demo_pokemon
                )

                second_duration = (
                    time.perf_counter()
                    - start
                )

                stats_after_second = (
                    api_cache.get_statistics()
                )

                if (
                    pokemon1 is None
                    or pokemon2 is None
                ):
                    st.error(
                        "Pokémon introuvable."
                    )

                else:
                    st.success(
                        "Test terminé."
                    )

                    col1, col2 = (
                        st.columns(2)
                    )

                    with col1:
                        st.subheader(
                            "Premier appel"
                        )

                        st.write(
                            "**Source : API**"
                        )

                        st.write(
                            "**Cache : MISS**"
                        )

                        st.metric(
                            "Durée",
                            (
                                f"{first_duration:.6f} s"
                            ),
                        )

                        st.write(
                            "Hits après appel :",
                            stats_after_first[
                                "hits"
                            ],
                        )

                        st.write(
                            "Misses après appel :",
                            stats_after_first[
                                "misses"
                            ],
                        )

                    with col2:
                        st.subheader(
                            "Deuxième appel"
                        )

                        st.write(
                            "**Source : cache**"
                        )

                        st.write(
                            "**Cache : HIT**"
                        )

                        st.metric(
                            "Durée",
                            (
                                f"{second_duration:.6f} s"
                            ),
                        )

                        st.write(
                            "Hits après appel :",
                            stats_after_second[
                                "hits"
                            ],
                        )

                        st.write(
                            "Misses après appel :",
                            stats_after_second[
                                "misses"
                            ],
                        )

                    if second_duration > 0:
                        speedup = (
                            first_duration
                            / second_duration
                        )

                        st.info(
                            "Facteur d'accélération "
                            f"observé : {speedup:.2f}x"
                        )

            except APIError as error:
                st.error(
                    f"Erreur API : {error}"
                )

            except Exception as error:
                st.error(
                    "Erreur inattendue : "
                    f"{error}"
                )

    st.divider()

    if st.button(
        "🗑️ Vider le cache",
        key="clear_cache_button",
    ):
        api_cache.clear()

        st.success(
            "Cache vidé."
        )

        st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Pokémon Analyzer - Mini-projet Python / PokéAPI"
)