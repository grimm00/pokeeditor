import json
import os
import re

def parse_hma_stats_file(filepath):
    """
    Parses the pokemon.stats.txt file and returns a dictionary of the raw data lines,
    keyed by the Pokémon's name.
    """
    data_map = {}
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or not line.startswith('+#'):
                    continue
                try:
                    name_part = line.split('#')[1]
                    # Normalize names to match JSON keys
                    species_name = name_part.replace('\\sf', ' F').replace('\\sm', ' M').replace('\\s', ' ')
                    if "Farfetch'd" in species_name: species_name = "Farfetchd"
                    
                    data_map[species_name] = line
                except IndexError:
                    continue # Skip malformed lines
    except FileNotFoundError:
        print(f"  - ERROR: Could not find required file: {filepath}")
    return data_map

def parse_abilities_file(filepath):
    """
    Parses the abilities.names.txt file and returns a name-to-ID mapping.
    """
    ability_map = {}
    ability_id = 0
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith(('+', '"')):
                    # Extract name from lines like +"Ability Name" or "Ability Name"
                    name = line.replace('+', '').strip().strip('"')
                    ability_map[name] = ability_id
                    ability_id += 1
    except FileNotFoundError:
        print(f"  - ERROR: Could not find required abilities file: {filepath}")
    return ability_map

def convert_json_to_hma_script():
    """
    Reads a custom JSON file and merges its changes into a complete, new version
    of the pokemon.stats.txt data, outputting it as a .tfl script.
    """
    # Use default file paths for simplicity
    stats_filepath = "pokemon.stats.txt"
    abilities_filepath = "abilities.names.txt"
    input_json_filename = "custom_pokemon.json"
    output_tfl_filename = "balance_patch.tfl"
    
    print("Using default filenames in the current directory.")

    print("\nReading ability names to create ID map...")
    ability_name_to_id = parse_abilities_file(abilities_filepath)
    if not ability_name_to_id:
        print("Could not load abilities. Aborting.")
        return
    print(f"Successfully mapped {len(ability_name_to_id)} abilities.")

    try:
        with open(input_json_filename, 'r', encoding='utf-8') as f:
            custom_data_obj = json.load(f)
        
        # Convert custom data to a dictionary keyed by name for quick lookups
        custom_data_map = {p['Name']: p for p in (list(custom_data_obj.values()) if isinstance(custom_data_obj, dict) else custom_data_obj)}
        print(f"\nProcessing {len(custom_data_map)} custom Pokémon edits from '{input_json_filename}'...")

        full_output_lines = []
        with open(stats_filepath, 'r', encoding='utf-8') as f:
            for line in f:
                original_line = line.strip()
                
                # If it's not a pokemon data line, add it as-is (preserves header, etc.)
                if not original_line or not original_line.startswith('+#'):
                    full_output_lines.append(original_line)
                    continue

                # It is a pokemon data line, so parse it
                try:
                    name_part = original_line.split('#')[1]
                    species_name = name_part.replace('\\sf', ' F').replace('\\sm', ' M').replace('\\s', ' ')
                    if "Farfetch'd" in species_name: species_name = "Farfetchd"
                except IndexError:
                    full_output_lines.append(original_line) # Keep malformed lines as they are
                    continue

                # Check if this pokemon has been edited
                if species_name in custom_data_map:
                    pokemon = custom_data_map[species_name]
                    print(f"  - Applying changes to {species_name}...")
                    
                    data_part = original_line.split(f"#{name_part}#,")[1]
                    parts = [p.strip() for p in data_part.split(',')]

                    # Update stats, types, and abilities
                    parts[0] = str(pokemon.get('HP', parts[0]))
                    parts[1] = str(pokemon.get('Attack', parts[1]))
                    parts[2] = str(pokemon.get('Defense', parts[2]))
                    parts[3] = str(pokemon.get('Speed', parts[3]))
                    parts[4] = str(pokemon.get('Sp Atk', parts[4]))
                    parts[5] = str(pokemon.get('Sp Def', parts[5]))
                    
                    type1 = pokemon.get('Type 1', parts[6])
                    type2 = pokemon.get('Type 2', parts[7])
                    parts[6] = type1
                    parts[7] = type2 if type2 is not None else type1

                    if "Ability 1" in pokemon:
                        parts[19] = f'"{pokemon["Ability 1"]}"'
                    
                    if "Ability 2" in pokemon:
                        ability2 = pokemon["Ability 2"]
                        parts[20] = f'"{ability2}"' if ability2 is not None else '"-------"'

                    hidden_ability_name = pokemon.get("Hidden Ability")
                    if hidden_ability_name:
                        if hidden_ability_name in ability_name_to_id:
                            parts[23] = str(ability_name_to_id[hidden_ability_name])
                        else:
                            print(f"    - WARNING: Hidden Ability '{hidden_ability_name}' not found. Using original.")
                    
                    updated_line = f"+#{name_part}#, {', '.join(parts)}"
                    full_output_lines.append(updated_line)
                else:
                    # If not edited, add the original line back
                    full_output_lines.append(original_line)

        with open(output_tfl_filename, 'w', encoding='utf-8') as f:
            # The first line (header) is already in full_output_lines
            # We just need to ensure the table name is there if the original file was weird
            if not full_output_lines[0].strip().startswith('@!'):
                 f.write("^data.pokemon.stats\n")
            
            f.write('\n'.join(full_output_lines))

        print(f"\nSuccessfully created full HMA script: '{output_tfl_filename}'")
        print("You can now copy the ENTIRE contents of this file and paste it into HMA's table editor.")

    except FileNotFoundError:
        print(f"\nError: A required file was not found. Please check filenames.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

if __name__ == "__main__":
    convert_json_to_hma_script()
