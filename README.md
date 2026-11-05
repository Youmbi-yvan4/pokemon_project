# Pokémon Analyzer

Mini-projet Python basé sur PokéAPI permettant de récupérer et analyser des informations sur les Pokémon, comparer leurs statistiques, simuler des combats et expérimenter plusieurs problématiques liées aux appels API :

- gestion des erreurs HTTP ;
- retries avec délai progressif ;
- appels synchrones et asynchrones ;
- concurrence avec `asyncio` ;
- cache avec expiration d'une heure ;
- simulation de charge ;
- interface utilisateur avec Streamlit.

---

# 1. Fonctionnalités

L'application permet de :

### Recherche d'un Pokémon

Rechercher un Pokémon par :

- nom ;
- ID.

Exemples :

```text
pikachu
25
charizard
```

Les informations affichées sont :

- ID ;
- type(s) ;
- HP ;
- attaque ;
- défense ;
- attaque spéciale ;
- défense spéciale ;
- vitesse.

Le JSON complet retourné par PokéAPI n'est pas directement affiché.

---

### Comparaison de deux Pokémon

L'application permet de comparer deux Pokémon selon :

- leurs HP ;
- leur attaque ;
- la différence de HP ;
- la différence d'attaque.

Un score simple est également utilisé :

```text
score = HP + attaque
```

Ce score est une règle définie uniquement pour ce mini-projet.

Il ne représente pas une formule officielle des jeux Pokémon.

---

### Analyse par type

L'utilisateur peut saisir un type :

```text
fire
water
dragon
electric
```

L'application :

1. récupère les Pokémon appartenant au type ;
2. récupère leurs statistiques ;
3. compte le nombre de Pokémon ;
4. calcule leur moyenne de HP ;
5. mesure le temps d'exécution.

Deux modes sont disponibles :

```text
Séquentiel
Asynchrone
```

Une limite peut également être utilisée pour effectuer des tests rapides.

Exemple :

```text
Type : fire
Limite : 10
```

Sans limite, tous les Pokémon retournés pour le type sont analysés.

---

### Combat entre deux Pokémon

L'application permet de simuler un combat de cinq tours.

Chaque Pokémon attaque une fois par tour.

La formule utilisée dans le projet est :

```python
damage = max(
    1,
    attacker.attack - defender.defense // 2
)
```

Les dégâts sont cumulés pendant cinq tours.

Le Pokémon ayant infligé le plus de dégâts totaux remporte le combat.

Cette formule est propre au mini-projet et ne représente pas le système officiel de combat Pokémon.

---

# 2. Gestion robuste des appels API

Les appels API sont centralisés dans :

```text
services/api_client.py
services/async_api_client.py
```

Différentes erreurs HTTP sont traitées.

Exemples :

```text
400 → Bad Request
401 → Unauthorized
403 → Forbidden
404 → Ressource inexistante
429 → Too Many Requests
500 → Internal Server Error
502 → Bad Gateway
503 → Service Unavailable
504 → Gateway Timeout
```

Les erreurs temporaires peuvent provoquer une nouvelle tentative.

Le système applique également un délai progressif entre les tentatives.

Exemple conceptuel :

```text
1 s
2 s
4 s
...
```

Des timeouts sont également utilisés afin d'éviter qu'une requête reste bloquée indéfiniment.

---

# 3. Appels asynchrones

La version asynchrone utilise :

```text
asyncio
httpx.AsyncClient
asyncio.Semaphore
```

Le but est d'effectuer plusieurs appels réseau de manière concurrente.

Le `Semaphore` limite le nombre d'appels exécutés simultanément.

Par exemple :

```python
concurrency_limit = 5
```

signifie qu'un maximum de cinq appels réseau peut être exécuté simultanément dans cette partie du programme.

---

# 4. Cache

Le projet possède un cache applicatif basé sur :

```text
cachetools.TTLCache
```

Le cache principal possède un TTL de :

```text
3600 secondes
```

soit :

```text
1 heure
```

Le principe est :

```text
Premier appel
    ↓
CACHE MISS
    ↓
PokéAPI
    ↓
mise en cache

Deuxième appel identique
    ↓
CACHE HIT
    ↓
réponse depuis le cache
```

Cela réduit les appels répétitifs vers l'API.

L'application Streamlit permet également :

- de consulter les cache hits ;
- de consulter les cache misses ;
- d'afficher le taux de hit ;
- de vider le cache ;
- de comparer la durée d'un premier et d'un second appel.

---

# 5. Test de charge

Le projet contient également une simulation de charge.

Pour éviter d'envoyer une charge importante vers PokéAPI, le test utilise une API locale.

Elle expose notamment :

```text
/data1
/data2
/data3
```

Les routes simulent différents comportements HTTP.

Le test de charge permet de configurer :

```text
nombre total de requêtes
taille des lots
niveau de concurrence
nombre de retries
```

Les requêtes sont traitées par lots afin d'éviter de créer toutes les tâches simultanément en mémoire.

Les métriques calculées incluent notamment :

- nombre de requêtes demandées ;
- nombre de requêtes terminées ;
- succès ;
- échecs ;
- tentatives HTTP ;
- retries ;
- durée totale ;
- temps moyen ;
- débit en requêtes par seconde ;
- statuts HTTP observés ;
- résultats par route.

---

# 6. Structure du projet

```text
pokemon_project/
│
├── app.py
├── compare_performance.py
├── requirements.txt
│
├── load_testing/
│   ├── __init__.py
│   ├── load_test.py
│   ├── mock_api.py
│   └── models.py
│
├── models/
│   ├── __init__.py
│   └── pokemon.py
│
├── services/
│   ├── __init__.py
│   ├── api_client.py
│   ├── async_api_client.py
│   ├── async_pokemon_service.py
│   ├── async_type_service.py
│   ├── battle_service.py
│   ├── cache_service.py
│   ├── comparison_service.py
│   ├── exceptions.py
│   ├── pokemon_service.py
│   └── type_service.py
│
├── test_api.py
├── test_async_type.py
├── test_battle.py
├── test_cache.py
├── test_cache_expiration.py
├── test_comparison.py
├── test_load_test.py
└── test_type.py
```

Les dossiers suivants ne doivent pas être versionnés :

```text
__pycache__/
.venv/
```

---

# 7. Installation après clonage du dépôt

## Étape 1 : cloner le projet

```bash
git clone URL_DU_DEPOT
```

Entrer ensuite dans le projet :

```bash
cd NOM_DU_DEPOT
```

---

## Étape 2 : créer l'environnement virtuel

```bash
python -m venv .venv
```

### Windows CMD

```cmd
.venv\Scripts\activate
```

### Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

### Linux / macOS

```bash
source .venv/bin/activate
```

Une fois activé, le terminal doit généralement afficher :

```text
(.venv)
```

---

## Étape 3 : installer les dépendances

```bash
pip install -r requirements.txt
```

Les principales dépendances du projet sont :

```text
requests
streamlit
httpx
cachetools
fastapi
uvicorn
pytest
```

---

# 8. Lancer l'application principale

Avec l'environnement virtuel activé :

```bash
python -m streamlit run app.py
```

Streamlit démarre alors l'interface Web.

Les principaux onglets permettent de tester :

```text
Recherche
Comparaison
Analyse par type
Combat
Cache
Test de charge
```

---

# 9. Reproduire les tests fonctionnels

## Recherche d'un Pokémon

Dans l'onglet de recherche, tester :

```text
pikachu
```

Puis :

```text
25
```

Les deux recherches doivent retrouver Pikachu.

Tester également :

```text
PIKACHU
```

et :

```text
pokemon-inexistant-123
```

Le dernier cas doit être traité sans faire planter l'application.

---

# 10. Tester la comparaison

Dans l'onglet Comparaison :

```text
Pokémon 1 : pikachu
Pokémon 2 : charizard
```

L'application affiche leurs HP et attaque ainsi que le résultat de la comparaison.

On peut également tester une égalité avec :

```text
pikachu
pikachu
```

---

# 11. Tester l'analyse par type

Utiliser par exemple :

```text
Type : fire
Limite : 10
Mode : Séquentiel
```

Noter le temps obtenu.

Effectuer ensuite exactement le même test avec :

```text
Type : fire
Limite : 10
Mode : Asynchrone
Concurrence : 5
```

Les deux versions doivent analyser le même nombre de Pokémon.

La moyenne de HP doit être cohérente lorsque les mêmes Pokémon ont été récupérés avec succès.

Les durées peuvent varier selon l'environnement et les conditions réseau.

---

# 12. Comparer automatiquement synchrone et asynchrone

Le fichier :

```text
compare_performance.py
```

permet de comparer les deux stratégies.

Lancer :

```bash
python compare_performance.py
```

Le script affiche notamment :

```text
durée séquentielle
durée asynchrone
moyenne HP
facteur d'accélération observé
```

Les performances observées dépendent de l'environnement d'exécution et du réseau.

---

# 13. Tester le combat

Lancer :

```bash
python test_battle.py
```

Ou utiliser directement l'interface Streamlit.

Exemple :

```text
pikachu
charizard
```

Le combat doit effectuer cinq tours puis afficher :

```text
dégâts de chaque tour
dégâts cumulés
gagnant
```

---

# 14. Tester le cache

Lancer :

```bash
python test_cache.py
```

Le script effectue deux appels identiques.

Le comportement attendu est :

```text
Premier appel
CACHE MISS
appel API

Deuxième appel
CACHE HIT
réponse provenant du cache
```

La durée du second appel doit généralement être nettement plus faible puisque la donnée est déjà présente en mémoire.

---

# 15. Tester l'expiration du cache

Le cache réel de l'application expire après :

```text
3600 secondes
```

Il n'est pas pratique d'attendre une heure pour démontrer cette fonctionnalité.

Le fichier :

```text
test_cache_expiration.py
```

utilise donc volontairement un TTL très court uniquement pour le test.

Lancer :

```bash
python test_cache_expiration.py
```

Le principe attendu est :

```text
Insertion
   ↓
lecture avant expiration
   ↓
HIT
   ↓
attente
   ↓
lecture après expiration
   ↓
MISS
```

---

# 16. Tester la récupération asynchrone

Lancer :

```bash
python test_async_type.py
```

Ce script permet de vérifier indépendamment de Streamlit le fonctionnement de l'analyse asynchrone.

---

# 17. Lancer la simulation de charge

Le test de charge nécessite deux terminaux.

## Terminal 1 : démarrer l'API locale

Activer l'environnement :

### Windows

```cmd
.venv\Scripts\activate
```

Puis :

```bash
python -m uvicorn load_testing.mock_api:app --host 127.0.0.1 --port 8000
```

Le serveur local doit être disponible sur :

```text
http://127.0.0.1:8000
```

Ne pas fermer ce terminal pendant le test.

---

## Terminal 2 : lancer le test

Activer également l'environnement virtuel :

```cmd
.venv\Scripts\activate
```

Puis commencer avec une charge réduite :

```bash
python -m load_testing.load_test --total 1000 --batch 100 --concurrency 20
```

Cela signifie :

```text
1 000 requêtes logiques
lots de 100
maximum de 20 requêtes concurrentes
```

Le script affiche ensuite les métriques mesurées.

---

# 18. Tester différents niveaux de charge

Commencer avec une petite charge :

```bash
python -m load_testing.load_test --total 100 --batch 20 --concurrency 10
```

Puis :

```bash
python -m load_testing.load_test --total 1000 --batch 100 --concurrency 20
```

Ensuite, si l'environnement local fonctionne correctement, augmenter progressivement :

```bash
python -m load_testing.load_test --total 10000 --batch 500 --concurrency 50
```

L'objectif du traitement par lots est de ne pas créer toutes les tâches simultanément en mémoire.

---

# 19. Test de charge depuis Streamlit

Laisser l'API locale active :

```bash
python -m uvicorn load_testing.mock_api:app --host 127.0.0.1 --port 8000
```

Dans un deuxième terminal :

```bash
python -m streamlit run app.py
```

Ouvrir :

```text
Test de charge
```

Utiliser par exemple :

```text
Adresse :
http://127.0.0.1:8000

Total :
1000

Batch :
100

Concurrence :
20

Retries :
2
```

Cliquer d'abord sur :

```text
Vérifier le serveur local
```

puis :

```text
Lancer la simulation
```

Les résultats affichés comprennent les succès, échecs, retries, durée, débit et statuts HTTP observés.

---

# 20. Autres scripts disponibles

## Test API simple

```bash
python test_api.py
```

## Analyse d'un type

```bash
python test_type.py
```

## Comparaison

```bash
python test_comparison.py
```

## Combat

```bash
python test_battle.py
```

## Async

```bash
python test_async_type.py
```

## Cache

```bash
python test_cache.py
```

## Expiration du cache

```bash
python test_cache_expiration.py
```

## Test de charge

Le serveur local doit être actif.

```bash
python test_load_test.py
```

---

# 21. Arrêter les applications

Pour arrêter Streamlit ou Uvicorn :

```text
Ctrl + C
```

Pour quitter l'environnement virtuel :

```bash
deactivate
```

---

# 22. Fichier `.gitignore` recommandé

Créer un fichier `.gitignore` à la racine avec :

```gitignore
# Environnement virtuel
.venv/
venv/

# Python
__pycache__/
*.py[cod]
*$py.class

# Pytest
.pytest_cache/

# Variables d'environnement
.env

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
```

---

# 23. Résumé du déroulement du projet

Le projet a été construit progressivement :

```text
Phase 0
Initialisation Python et connexion à PokéAPI

Phase 1
Récupération d'un Pokémon et nettoyage des données

Phase 2
Modèle Python Pokemon

Phase 3
Gestion robuste des appels HTTP et retries

Phase 4
Comparaison de deux Pokémon

Phase 5
Analyse des Pokémon par type

Phase 6
Simulation d'un combat sur cinq tours

Phase 7
Interface Streamlit

Phase 8
Asyncio, HTTPX et concurrence contrôlée

Phase 9
Cache avec expiration d'une heure

Phase 10
Simulation locale d'une charge importante
```

---

# 24. Démarrage rapide

Pour quelqu'un qui vient simplement de cloner le dépôt :

```bash
python -m venv .venv
```

### Windows

```cmd
.venv\Scripts\activate
```

Puis :

```bash
pip install -r requirements.txt
```

Et :

```bash
python -m streamlit run app.py
```

Pour le test de charge, ouvrir un autre terminal et lancer :

```bash
python -m uvicorn load_testing.mock_api:app --host 127.0.0.1 --port 8000
```

L'application est alors prête pour démontrer les différentes fonctionnalités du mini-projet.