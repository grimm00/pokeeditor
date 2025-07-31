import requests
import json
import os

# --- Configuration ---
SPECIES_COUNT = 1025 
API_SPECIES_URL = "https://pokeapi.co/api/v2/pokemon-species/"
CACHE_FILENAME = "pokemon_cache.json"

def generate_pokemon_cache():
    """
    Fetches data for all Pokémon forms from PokéAPI and saves it to a JSON cache file.
    If the cache file already exists, the script will do nothing.
    """
    # --- Step 1: Check if the cache file already exists ---
    if os.path.exists(CACHE_FILENAME):
        print(f"Cache file '{CACHE_FILENAME}' already exists. No action needed.")
        print("To force a refresh, please delete the existing cache file and run this script again.")
        return

    # --- Step 2: If no cache, fetch fresh data from API ---
    print("No cache file found. Fetching fresh data from PokéAPI.")
    all_pokemon_data = []
    print(f"Fetching all Pokémon forms for {SPECIES_COUNT} species. This will take several minutes...")

    for i in range(1, SPECIES_COUNT + 1):
        try:
            species_res = requests.get(f"{API_SPECIES_URL}{i}")
            species_res.raise_for_status()
            species_data = species_res.json()
            
            species_name = species_data['name'].title()
            print(f"\nFetching Species #{i}: {species_name}")

            for variety in species_data['varieties']:
                pokemon_name = variety['pokemon']['name']
                pokemon_url = variety['pokemon']['url']

                try:
                    print(f"  -> Fetching variant: {pokemon_name}")
                    pokemon_res = requests.get(pokemon_url)
                    pokemon_res.raise_for_status()
                    data = pokemon_res.json()

                    stats = {stat['stat']['name']: stat['base_stat'] for stat in data['stats']}
                    abilities = data['abilities']
                    ability_1 = next((a['ability']['name'] for a in abilities if a['slot'] == 1), None)
                    ability_2 = next((a['ability']['name'] for a in abilities if a['slot'] == 2), None)
                    hidden_ability = next((a['ability']['name'] for a in abilities if a['is_hidden']), None)
                    
                    hp = stats.get('hp', 0)
                    attack = stats.get('attack', 0)
                    defense = stats.get('defense', 0)
                    sp_atk = stats.get('special-attack', 0)
                    sp_def = stats.get('special-defense', 0)
                    speed = stats.get('speed', 0)

                    pokemon_entry = {
                        '#': data['id'],
                        'Name': data['name'].replace('-', ' ').title(),
                        'Type 1': data['types'][0]['type']['name'].title(),
                        'Type 2': data['types'][1]['type']['name'].title() if len(data['types']) > 1 else None,
                        'Ability 1': ability_1.replace('-', ' ').title() if ability_1 else None,
                        'Ability 2': ability_2.replace('-', ' ').title() if ability_2 else None,
                        'Hidden Ability': hidden_ability.replace('-', ' ').title() if hidden_ability else None,
                        'HP': hp,
                        'Attack': attack,
                        'Defense': defense,
                        'Sp Atk': sp_atk,
                        'Sp Def': sp_def,
                        'Speed': speed,
                        'BST': hp + attack + defense + sp_atk + sp_def + speed
                    }
                    all_pokemon_data.append(pokemon_entry)

                except requests.exceptions.RequestException as e:
                    print(f"    -> ERROR fetching variant {pokemon_name}: {e}")

        except requests.exceptions.RequestException as e:
            print(f"ERROR fetching species with ID {i}: {e}")

    # --- Step 3: Sort and save the data to the cache file ---
    all_pokemon_data.sort(key=lambda p: p['#'])
    print(f"\nSaving data to cache file '{CACHE_FILENAME}'...")
    with open(CACHE_FILENAME, 'w', encoding='utf-8') as f:
        json.dump(all_pokemon_data, f, indent=4)
    
    print("Cache file generated successfully!")

# --- Main Execution ---
if __name__ == "__main__":
    generate_pokemon_cache()
