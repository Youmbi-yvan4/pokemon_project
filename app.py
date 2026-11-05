import streamlit as st

from services.battle_service import simulate_battle
from services.comparison_service import compare_pokemon
from services.exceptions import APIError
from services.pokemon_service import get_pokemon
from services.type_service import calculate_type_statistics


# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Pokémon Analyzer",
    page_icon="⚡",
    layout="wide",
)

st.title("⚡ Pokémon Analyzer")

st.write(
    "Explorez les statistiques des Pokémon, comparez-les, "
    "analysez leurs types et simulez des combats."
)

st.divider()


# ============================================================
# ONGLETS
# ============================================================

tab_search, tab_compare, tab_type, tab_battle = st.tabs(
    [
        "🔎 Recherche",
        "⚖️ Comparaison",
        "📊 Analyse par type",
        "⚔️ Combat",
    ]
)


# ============================================================
# 1. RECHERCHE D'UN POKÉMON
# ============================================================

with tab_search:

    st.header("🔎 Rechercher un Pokémon")

    st.write(
        "Entrez le nom ou l'identifiant d'un Pokémon "
        "pour afficher ses statistiques."
    )

    identifier = st.text_input(
        "Nom ou ID du Pokémon",
        placeholder="Exemple : pikachu ou 25",
        key="search_pokemon",
    )

    search_button = st.button(
        "Rechercher",
        key="search_button",
    )

    if search_button:

        if not identifier.strip():

            st.warning(
                "Veuillez saisir un nom ou un identifiant."
            )

        else:

            try:

                with st.spinner(
                    "Récupération du Pokémon...",
                    show_time=True,
                ):
                    pokemon = get_pokemon(identifier)

                if pokemon is None:

                    st.error("Pokémon introuvable.")

                else:

                    st.success("Pokémon trouvé.")

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
                            for type_name in pokemon.types
                        ),
                    )

                    st.divider()

                    # Première ligne
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric(
                            "❤️ HP",
                            pokemon.hp,
                        )

                    with col2:
                        st.metric(
                            "⚔️ Attaque",
                            pokemon.attack,
                        )

                    with col3:
                        st.metric(
                            "🛡️ Défense",
                            pokemon.defense,
                        )

                    # Deuxième ligne
                    col4, col5, col6 = st.columns(3)

                    with col4:
                        st.metric(
                            "✨ Attaque spéciale",
                            pokemon.special_attack,
                        )

                    with col5:
                        st.metric(
                            "🔰 Défense spéciale",
                            pokemon.special_defense,
                        )

                    with col6:
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
                    f"Une erreur inattendue est survenue : {error}"
                )


# ============================================================
# 2. COMPARAISON DE DEUX POKÉMON
# ============================================================

with tab_compare:

    st.header("⚖️ Comparer deux Pokémon")

    st.write(
        "Comparez les points de vie et l'attaque "
        "de deux Pokémon."
    )

    col1, col2 = st.columns(2)

    with col1:

        first_pokemon = st.text_input(
            "Premier Pokémon",
            placeholder="Exemple : pikachu",
            key="compare_first",
        )

    with col2:

        second_pokemon = st.text_input(
            "Deuxième Pokémon",
            placeholder="Exemple : charizard",
            key="compare_second",
        )

    compare_button = st.button(
        "Comparer",
        key="compare_button",
    )

    if compare_button:

        if (
            not first_pokemon.strip()
            or not second_pokemon.strip()
        ):

            st.warning(
                "Veuillez saisir les deux Pokémon."
            )

        else:

            try:

                with st.spinner(
                    "Comparaison en cours...",
                    show_time=True,
                ):

                    result = compare_pokemon(
                        first_pokemon,
                        second_pokemon,
                    )

                if result is None:

                    st.error(
                        "Un des Pokémon est introuvable."
                    )

                else:

                    pokemon1 = result["pokemon_1"]
                    pokemon2 = result["pokemon_2"]

                    st.success(
                        "Comparaison terminée."
                    )

                    st.divider()

                    col1, col2 = st.columns(2)

                    # Premier Pokémon
                    with col1:

                        st.subheader(
                            pokemon1.name.capitalize()
                        )

                        st.write(
                            "**Type(s) :**",
                            ", ".join(
                                type_name.capitalize()
                                for type_name in pokemon1.types
                            ),
                        )

                        st.metric(
                            "❤️ HP",
                            pokemon1.hp,
                        )

                        st.metric(
                            "⚔️ Attaque",
                            pokemon1.attack,
                        )

                        st.metric(
                            "Score HP + attaque",
                            pokemon1.strength_score(),
                        )

                    # Deuxième Pokémon
                    with col2:

                        st.subheader(
                            pokemon2.name.capitalize()
                        )

                        st.write(
                            "**Type(s) :**",
                            ", ".join(
                                type_name.capitalize()
                                for type_name in pokemon2.types
                            ),
                        )

                        st.metric(
                            "❤️ HP",
                            pokemon2.hp,
                        )

                        st.metric(
                            "⚔️ Attaque",
                            pokemon2.attack,
                        )

                        st.metric(
                            "Score HP + attaque",
                            pokemon2.strength_score(),
                        )

                    st.divider()

                    st.subheader(
                        "Résultat de la comparaison"
                    )

                    result_col1, result_col2 = st.columns(2)

                    with result_col1:

                        st.write(
                            "**Meilleurs HP :**",
                            result["best_hp"],
                        )

                        st.write(
                            "**Différence de HP :**",
                            result["hp_difference"],
                        )

                    with result_col2:

                        st.write(
                            "**Meilleure attaque :**",
                            result["best_attack"],
                        )

                        st.write(
                            "**Différence d'attaque :**",
                            result["attack_difference"],
                        )

                    st.info(
                        "Plus fort selon notre règle "
                        "`HP + attaque` : "
                        f"**{result['strongest']}**"
                    )

                    st.caption(
                        "Le score HP + attaque est une règle "
                        "définie pour ce projet et non une "
                        "formule officielle des jeux Pokémon."
                    )

            except APIError as error:

                st.error(
                    f"Erreur API : {error}"
                )

            except Exception as error:

                st.error(
                    f"Une erreur inattendue est survenue : {error}"
                )


# ============================================================
# 3. ANALYSE PAR TYPE
# ============================================================

with tab_type:

    st.header("📊 Analyse des Pokémon par type")

    st.write(
        "Sélectionnez un type pour connaître le nombre "
        "de Pokémon disponibles et calculer leur moyenne de HP."
    )

    type_name = st.text_input(
        "Type Pokémon",
        placeholder="Exemple : fire, water, dragon...",
        key="type_name",
    )

    limit = st.number_input(
        "Nombre de Pokémon à analyser",
        min_value=1,
        value=10,
        step=1,
        key="type_limit",
    )

    st.caption(
        "Nous limitons volontairement le nombre pendant "
        "cette phase car les appels API sont encore séquentiels."
    )

    analyse_button = st.button(
        "Analyser",
        key="analyse_button",
    )

    if analyse_button:

        if not type_name.strip():

            st.warning(
                "Veuillez saisir un type."
            )

        else:

            try:

                with st.spinner(
                    "Analyse du type en cours...",
                    show_time=True,
                ):

                    result = calculate_type_statistics(
                        type_name,
                        limit=int(limit),
                    )

                if result is None:

                    st.error(
                        "Type Pokémon introuvable."
                    )

                else:

                    st.success(
                        "Analyse terminée."
                    )

                    st.subheader(
                        f"Type : {result['type'].capitalize()}"
                    )

                    st.divider()

                    col1, col2, col3 = st.columns(3)

                    with col1:

                        st.metric(
                            "Pokémon disponibles",
                            result["available_count"],
                        )

                    with col2:

                        st.metric(
                            "Pokémon analysés",
                            result["analysed_count"],
                        )

                    with col3:

                        st.metric(
                            "HP moyen",
                            round(
                                result["average_hp"],
                                2,
                            ),
                        )

                    st.divider()

                    col4, col5, col6 = st.columns(3)

                    with col4:

                        st.metric(
                            "Récupérations réussies",
                            result["successful_count"],
                        )

                    with col5:

                        st.metric(
                            "Échecs",
                            result["failed_count"],
                        )

                    with col6:

                        st.metric(
                            "Temps d'exécution",
                            f"{result['duration_seconds']:.2f} s",
                        )

                    if result["failed_names"]:

                        with st.expander(
                            "Afficher les Pokémon non récupérés"
                        ):

                            for name in result["failed_names"]:
                                st.write(
                                    f"- {name}"
                                )

            except ValueError as error:

                st.warning(str(error))

            except APIError as error:

                st.error(
                    f"Erreur API : {error}"
                )

            except Exception as error:

                st.error(
                    f"Une erreur inattendue est survenue : {error}"
                )


# ============================================================
# 4. COMBAT
# ============================================================

with tab_battle:

    st.header("⚔️ Combat Pokémon")

    st.write(
        "Simulez un combat de cinq tours entre deux Pokémon."
    )

    st.caption(
        "Chaque Pokémon inflige des dégâts calculés avec "
        "son attaque et la défense de son adversaire."
    )

    col1, col2 = st.columns(2)

    with col1:

        fighter1 = st.text_input(
            "Pokémon 1",
            placeholder="Exemple : pikachu",
            key="battle_first",
        )

    with col2:

        fighter2 = st.text_input(
            "Pokémon 2",
            placeholder="Exemple : charizard",
            key="battle_second",
        )

    battle_button = st.button(
        "⚔️ Lancer le combat",
        key="battle_button",
    )

    if battle_button:

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
                    "Préparation du combat...",
                    show_time=True,
                ):

                    result = simulate_battle(
                        fighter1,
                        fighter2,
                        rounds=5,
                    )

                if result is None:

                    st.error(
                        "Un des Pokémon est introuvable."
                    )

                else:

                    pokemon1 = result["pokemon_1"]
                    pokemon2 = result["pokemon_2"]

                    st.subheader(
                        f"{pokemon1.name.capitalize()} "
                        "VS "
                        f"{pokemon2.name.capitalize()}"
                    )

                    st.divider()

                    # Affichage des caractéristiques
                    col1, col2 = st.columns(2)

                    with col1:

                        st.write(
                            f"### {pokemon1.name.capitalize()}"
                        )

                        st.write(
                            f"❤️ HP : {pokemon1.hp}"
                        )

                        st.write(
                            f"⚔️ Attaque : {pokemon1.attack}"
                        )

                        st.write(
                            f"🛡️ Défense : {pokemon1.defense}"
                        )

                    with col2:

                        st.write(
                            f"### {pokemon2.name.capitalize()}"
                        )

                        st.write(
                            f"❤️ HP : {pokemon2.hp}"
                        )

                        st.write(
                            f"⚔️ Attaque : {pokemon2.attack}"
                        )

                        st.write(
                            f"🛡️ Défense : {pokemon2.defense}"
                        )

                    st.divider()

                    st.subheader(
                        "Déroulement du combat"
                    )

                    for round_result in result["rounds"]:

                        round_number = round_result[
                            "round"
                        ]

                        damage1 = round_result[
                            "pokemon1_damage"
                        ]

                        damage2 = round_result[
                            "pokemon2_damage"
                        ]

                        with st.expander(
                            f"Tour {round_number}",
                            expanded=True,
                        ):

                            st.write(
                                f"⚡ "
                                f"{pokemon1.name.capitalize()} "
                                f"inflige **{damage1} dégâts** "
                                f"à "
                                f"{pokemon2.name.capitalize()}."
                            )

                            st.write(
                                f"⚡ "
                                f"{pokemon2.name.capitalize()} "
                                f"inflige **{damage2} dégâts** "
                                f"à "
                                f"{pokemon1.name.capitalize()}."
                            )

                    st.divider()

                    st.subheader(
                        "Résultat final"
                    )

                    col1, col2 = st.columns(2)

                    with col1:

                        st.metric(
                            f"Dégâts totaux - "
                            f"{pokemon1.name.capitalize()}",
                            result["total_damage_1"],
                        )

                    with col2:

                        st.metric(
                            f"Dégâts totaux - "
                            f"{pokemon2.name.capitalize()}",
                            result["total_damage_2"],
                        )

                    st.divider()

                    if result["winner"] == "Égalité":

                        st.warning(
                            "🤝 Le combat se termine "
                            "sur une égalité."
                        )

                    else:

                        st.success(
                            f"🏆 Gagnant : "
                            f"{result['winner'].capitalize()}"
                        )

                    st.caption(
                        "Règle du projet : dégâts = "
                        "max(1, attaque - défense_adverse // 2). "
                        "Le Pokémon ayant infligé le plus de "
                        "dégâts cumulés après cinq tours gagne."
                    )

            except APIError as error:

                st.error(
                    f"Erreur API : {error}"
                )

            except ValueError as error:

                st.warning(str(error))

            except Exception as error:

                st.error(
                    f"Une erreur inattendue est survenue : {error}"
                )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Pokémon Analyzer - Mini-projet Python / PokéAPI"
)