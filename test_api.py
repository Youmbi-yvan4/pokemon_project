from services.pokemon_service import get_pokemon


pokemon = get_pokemon("pikachu")

if pokemon:
    print("ID :", pokemon["id"])
    print("Nom :", pokemon["name"])
    print("Types :", pokemon["types"])
    print("HP :", pokemon["hp"])
    print("Attaque :", pokemon["attack"])
    print("Défense :", pokemon["defense"])
    print("Attaque spéciale :", pokemon["special_attack"])
    print("Défense spéciale :", pokemon["special_defense"])
    print("Vitesse :", pokemon["speed"])
else:
    print("Pokémon introuvable")