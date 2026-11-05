import asyncio
import time

import streamlit as st

from load_testing.load_test import (
    DEFAULT_BASE_URL,
    check_mock_api,
    reset_mock_api,
    run_load_test,
)
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
from services.exceptions import APIError
from services.pokemon_service import (
    get_pokemon,
)
from services.type_service import (
    calculate_type_statistics,
)


st.set_page_config(
    page_title="Pokémon Analyzer",
    page_icon="⚡",
    layout="wide",
)

st.title("⚡ Pokémon Analyzer")

st.write(
    "Recherchez, comparez et analysez les Pokémon, "
    "simulez des combats et testez la montée en charge."
)

st.divider()


(
    tab_search,
    tab_compare,
    tab_type,
    tab_battle,
    tab_cache,
    tab_load,
) = st.tabs(
    [
        "🔎 Recherche",
        "⚖️ Comparaison",
        "📊 Analyse par type",
        "⚔️ Combat",
        "🗄️ Cache",
        "🚀 Test de charge",
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
        placeholder="pikachu ou 25",
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
                            "HP",
                            pokemon.hp,
                        )

                        st.metric(
                            "Attaque spéciale",
                            pokemon.special_attack,
                        )

                    with col2:
                        st.metric(
                            "Attaque",
                            pokemon.attack,
                        )

                        st.metric(
                            "Défense spéciale",
                            pokemon.special_defense,
                        )

                    with col3:
                        st.metric(
                            "Défense",
                            pokemon.defense,
                        )

                        st.metric(
                            "Vitesse",
                            pokemon.speed,
                        )

            except APIError as error:
                st.error(
                    f"Erreur API : {error}"
                )

            except Exception as error:
                st.error(
                    f"Erreur inattendue : {error}"
                )


# ============================================================
# COMPARAISON
# ============================================================

with tab_compare:
    st.header(
        "⚖️ Comparaison"
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

                    st.caption(
                        "Le score HP + attaque est une règle "
                        "définie pour ce mini-projet."
                    )

            except APIError as error:
                st.error(
                    f"Erreur API : {error}"
                )

            except Exception as error:
                st.error(
                    f"Erreur inattendue : {error}"
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

    type_concurrency = st.slider(
        "Requêtes simultanées",
        min_value=1,
        max_value=20,
        value=5,
        step=1,
        disabled=(
            execution_mode
            == "Séquentiel"
        ),
        key="type_concurrency",
    )

    use_analysis_cache = st.checkbox(
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
                                type_identifier=(
                                    type_name
                                ),
                                limit=(
                                    selected_limit
                                ),
                                use_cache=(
                                    use_analysis_cache
                                ),
                            )
                        )

                    else:
                        result = asyncio.run(
                            calculate_type_statistics_async(
                                type_identifier=(
                                    type_name
                                ),
                                limit=(
                                    selected_limit
                                ),
                                concurrency_limit=int(
                                    type_concurrency
                                ),
                                use_cache=(
                                    use_analysis_cache
                                ),
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
                            "Succès",
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
                        "Cache de cette analyse"
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

                    if result[
                        "failed_names"
                    ]:
                        with st.expander(
                            "Pokémon non récupérés"
                        ):
                            for name in result[
                                "failed_names"
                            ]:
                                st.write(
                                    f"- {name}"
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
                    f"Erreur inattendue : {error}"
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
                            f"Tour "
                            f"{round_result['round']}"
                        ):
                            st.write(
                                f"{pokemon1.name.capitalize()} "
                                f"inflige "
                                f"**{round_result['pokemon1_damage']} "
                                f"dégâts**."
                            )

                            st.write(
                                f"{pokemon2.name.capitalize()} "
                                f"inflige "
                                f"**{round_result['pokemon2_damage']} "
                                f"dégâts**."
                            )

                    st.divider()

                    col1, col2 = (
                        st.columns(2)
                    )

                    with col1:
                        st.metric(
                            (
                                "Dégâts totaux "
                                f"{pokemon1.name.capitalize()}"
                            ),
                            result[
                                "total_damage_1"
                            ],
                        )

                    with col2:
                        st.metric(
                            (
                                "Dégâts totaux "
                                f"{pokemon2.name.capitalize()}"
                            ),
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
                    f"Erreur inattendue : {error}"
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
        "une heure."
    )

    cache_statistics = (
        api_cache.get_statistics()
    )

    col1, col2, col3, col4 = (
        st.columns(4)
    )

    with col1:
        st.metric(
            "Hits",
            cache_statistics["hits"],
        )

    with col2:
        st.metric(
            "Misses",
            cache_statistics["misses"],
        )

    with col3:
        st.metric(
            "Entrées",
            cache_statistics["size"],
        )

    with col4:
        st.metric(
            "Hit rate",
            (
                f"{cache_statistics['hit_rate']:.1f} %"
            ),
        )

    st.write(
        "**TTL :**",
        cache_statistics[
            "ttl_seconds"
        ],
        "secondes",
    )

    cache_demo_name = st.text_input(
        "Pokémon de démonstration",
        value="pikachu",
        key="cache_demo",
    )

    if st.button(
        "Tester le cache",
        key="cache_test_button",
    ):
        if not cache_demo_name.strip():
            st.warning(
                "Veuillez saisir un Pokémon."
            )

        else:
            try:
                api_cache.clear()

                start = (
                    time.perf_counter()
                )

                first = get_pokemon(
                    cache_demo_name
                )

                first_duration = (
                    time.perf_counter()
                    - start
                )

                first_stats = (
                    api_cache.get_statistics()
                )

                start = (
                    time.perf_counter()
                )

                second = get_pokemon(
                    cache_demo_name
                )

                second_duration = (
                    time.perf_counter()
                    - start
                )

                second_stats = (
                    api_cache.get_statistics()
                )

                if (
                    first is None
                    or second is None
                ):
                    st.error(
                        "Pokémon introuvable."
                    )

                else:
                    col1, col2 = (
                        st.columns(2)
                    )

                    with col1:
                        st.subheader(
                            "Premier appel"
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
                            "Misses :",
                            first_stats[
                                "misses"
                            ],
                        )

                    with col2:
                        st.subheader(
                            "Deuxième appel"
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
                            "Hits :",
                            second_stats[
                                "hits"
                            ],
                        )

                    if second_duration > 0:
                        speedup = (
                            first_duration
                            / second_duration
                        )

                        st.info(
                            "Accélération observée : "
                            f"{speedup:.2f}x"
                        )

            except APIError as error:
                st.error(
                    f"Erreur API : {error}"
                )

            except Exception as error:
                st.error(
                    f"Erreur inattendue : {error}"
                )

    if st.button(
        "Vider le cache",
        key="clear_cache_button",
    ):
        api_cache.clear()

        st.success(
            "Cache vidé."
        )

        st.rerun()


# ============================================================
# TEST DE CHARGE
# ============================================================

with tab_load:
    st.header(
        "🚀 Simulation de charge"
    )

    st.warning(
        "Le test de charge doit cibler uniquement "
        "l'API locale de simulation."
    )

    load_base_url = st.text_input(
        "Adresse de l'API locale",
        value=DEFAULT_BASE_URL,
        key="load_base_url",
    )

    col1, col2 = st.columns(2)

    with col1:
        total_requests = st.number_input(
            "Nombre total de requêtes",
            min_value=1,
            max_value=1_000_000,
            value=1000,
            step=100,
            key="load_total",
        )

        batch_size = st.number_input(
            "Taille des lots",
            min_value=1,
            max_value=10_000,
            value=100,
            step=10,
            key="load_batch",
        )

    with col2:
        load_concurrency = st.number_input(
            "Concurrence maximale",
            min_value=1,
            max_value=500,
            value=20,
            step=1,
            key="load_concurrency",
        )

        load_retries = st.number_input(
            "Retries maximum",
            min_value=0,
            max_value=10,
            value=2,
            step=1,
            key="load_retries",
        )

    st.caption(
        "Les requêtes sont créées par lots afin "
        "d'éviter de charger toutes les tâches "
        "simultanément en mémoire."
    )

    if st.button(
        "Vérifier le serveur local",
        key="check_load_server",
    ):
        try:
            available = asyncio.run(
                check_mock_api(
                    base_url=load_base_url
                )
            )

            if available:
                st.success(
                    "Serveur local accessible."
                )

            else:
                st.error(
                    "Serveur local inaccessible."
                )

                st.code(
                    "python -m uvicorn "
                    "load_testing.mock_api:app "
                    "--host 127.0.0.1 --port 8000",
                    language="bash",
                )

        except Exception as error:
            st.error(
                f"Erreur : {error}"
            )

    if st.button(
        "Lancer la simulation",
        key="run_load_test",
    ):
        try:
            available = asyncio.run(
                check_mock_api(
                    base_url=load_base_url
                )
            )

            if not available:
                st.error(
                    "Le serveur local "
                    "n'est pas accessible."
                )

            else:
                asyncio.run(
                    reset_mock_api(
                        base_url=load_base_url
                    )
                )

                with st.spinner(
                    "Test de charge en cours...",
                    show_time=True,
                ):
                    metrics = asyncio.run(
                        run_load_test(
                            total_requests=int(
                                total_requests
                            ),
                            batch_size=int(
                                batch_size
                            ),
                            concurrency_limit=int(
                                load_concurrency
                            ),
                            max_retries=int(
                                load_retries
                            ),
                            backoff_factor=0.05,
                            base_url=(
                                load_base_url
                            ),
                            request_timeout=10,
                        )
                    )

                st.success(
                    "Simulation terminée."
                )

                col1, col2, col3, col4 = (
                    st.columns(4)
                )

                with col1:
                    st.metric(
                        "Demandées",
                        metrics.total_requested,
                    )

                with col2:
                    st.metric(
                        "Succès",
                        metrics.successful_requests,
                    )

                with col3:
                    st.metric(
                        "Échecs",
                        metrics.failed_requests,
                    )

                with col4:
                    st.metric(
                        "Retries",
                        metrics.total_retries,
                    )

                col5, col6, col7 = (
                    st.columns(3)
                )

                with col5:
                    st.metric(
                        "Durée totale",
                        (
                            f"{metrics.duration_seconds:.2f} s"
                        ),
                    )

                with col6:
                    st.metric(
                        "Débit",
                        (
                            f"{metrics.requests_per_second:.2f} req/s"
                        ),
                    )

                with col7:
                    st.metric(
                        "Temps moyen",
                        (
                            f"{metrics.average_response_time_seconds:.4f} s"
                        ),
                    )

                st.divider()

                st.subheader(
                    "Statuts HTTP rencontrés"
                )

                if metrics.status_counts:
                    for (
                        status_code,
                        count,
                    ) in sorted(
                        metrics.status_counts.items()
                    ):
                        st.write(
                            f"**HTTP {status_code} :** "
                            f"{count}"
                        )

                else:
                    st.write(
                        "Aucun statut enregistré."
                    )

                st.divider()

                st.subheader(
                    "Résultats par route"
                )

                for route, count in (
                    metrics.route_counts.items()
                ):
                    successes = (
                        metrics.route_success_counts.get(
                            route,
                            0,
                        )
                    )

                    failures = (
                        metrics.route_failure_counts.get(
                            route,
                            0,
                        )
                    )

                    st.write(
                        f"**{route}**"
                    )

                    route_col1, route_col2, route_col3 = (
                        st.columns(3)
                    )

                    with route_col1:
                        st.metric(
                            "Requêtes",
                            count,
                        )

                    with route_col2:
                        st.metric(
                            "Succès",
                            successes,
                        )

                    with route_col3:
                        st.metric(
                            "Échecs",
                            failures,
                        )

        except ValueError as error:
            st.warning(
                str(error)
            )

        except Exception as error:
            st.error(
                "Erreur pendant le test de charge : "
                f"{error}"
            )


st.divider()

st.caption(
    "Pokémon Analyzer - Mini-projet Python / PokéAPI"
)