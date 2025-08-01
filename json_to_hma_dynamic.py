import json
import os
import re

# --- HMA Specific Formatting ---
# Dictionary to map full type names to HMA's required abbreviations
TYPE_ABBREVIATIONS = {
    "Electric": "Electr",
    "Psychic": "Psychc",
    "Fighting": "Fight"
}

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
    ability_map = {'-------': 0} # Explicitly map no ability to ID 0
    ability_id = 0
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith(('+', '"')):
                    name = line.replace('+', '').strip().strip('"')
                    if name == "-------": # Skip the header entry if it appears again
                        continue
                    ability_id += 1 # Start counting from 1 for actual abilities
                    ability_map[name] = ability_id
    except FileNotFoundError:
        print(f"  - ERROR: Could not find required abilities file: {filepath}")
    return ability_map

def robust_split(line):
    """
    Splits a comma-separated string while respecting values in quotes and parentheses.
    """
    parts = []
    in_quotes = False
    paren_level = 0
    current_part = ""
    for char in line:
        if char == '"':
            in_quotes = not in_quotes
        elif char == '(' and not in_quotes:
            paren_level += 1
        elif char == ')' and not in_quotes:
            paren_level -= 1
        
        if char == ',' and not in_quotes and paren_level == 0:
            parts.append(current_part.strip())
            current_part = ""
        else:
            current_part += char
    parts.append(current_part.strip())
    return parts

def convert_json_to_hma_script():
    """
    Reads a custom JSON file and merges its changes into a complete, new version
    of the pokemon.stats.txt data, outputting it as a .tfl script.
    """
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
        
        custom_data_map = {p['Name']: p for p in (list(custom_data_obj.values()) if isinstance(custom_data_obj, dict) else custom_data_obj)}
        print(f"\nProcessing {len(custom_data_map)} custom Pokémon edits from '{input_json_filename}'...")

        full_output_lines = []
        with open(stats_filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                original_line = line.strip()
                
                if not original_line or not original_line.startswith('+#'):
                    full_output_lines.append(original_line)
                    continue

                try:
                    name_part = original_line.split('#')[1]
                    species_name = name_part.replace('\\sf', ' F').replace('\\sm', ' M').replace('\\s', ' ')
                    if "Farfetch'd" in species_name: species_name = "Farfetchd"
                except IndexError:
                    full_output_lines.append(original_line)
                    continue

                if species_name in custom_data_map:
                    pokemon = custom_data_map[species_name]
                    print(f"  - Applying changes to {species_name}...")
                    
                    data_part = original_line.split(f"#{name_part}#,")[1]
                    parts = robust_split(data_part)

                    if len(parts) != 25:
                        print(f"  - WARNING: Malformed line #{line_num} for {species_name}. Skipping. Expected 25 columns, found {len(parts)}.")
                        full_output_lines.append(original_line)
                        continue

                    # Update Stats
                    parts[0] = str(pokemon.get('HP', parts[0]))
                    parts[1] = str(pokemon.get('Attack', parts[1]))
                    parts[2] = str(pokemon.get('Defense', parts[2]))
                    parts[3] = str(pokemon.get('Speed', parts[3]))
                    parts[4] = str(pokemon.get('Sp Atk', parts[4]))
                    parts[5] = str(pokemon.get('Sp Def', parts[5]))
                    
                    # Update Types with abbreviations
                    type1_name = pokemon.get('Type 1', parts[6])
                    type2_name = pokemon.get('Type 2', parts[7])
                    parts[6] = TYPE_ABBREVIATIONS.get(type1_name, type1_name)
                    final_type2_name = type2_name if type2_name is not None else type1_name
                    parts[7] = TYPE_ABBREVIATIONS.get(final_type2_name, final_type2_name)

                    # Update Abilities using numeric IDs
                    if "Ability 1" in pokemon and pokemon["Ability 1"] in ability_name_to_id:
                        parts[20] = str(ability_name_to_id[pokemon["Ability 1"]])
                    
                    if "Ability 2" in pokemon:
                        ability2_name = pokemon["Ability 2"] if pokemon["Ability 2"] is not None else '-------'
                        if ability2_name in ability_name_to_id:
                            parts[21] = str(ability_name_to_id[ability2_name])

                    if "Hidden Ability" in pokemon:
                        hidden_ability_name = pokemon["Hidden Ability"] if pokemon["Hidden Ability"] is not None else '-------'
                        if hidden_ability_name in ability_name_to_id:
                            parts[23] = str(ability_name_to_id[hidden_ability_name])
                        else:
                             print(f"    - WARNING: Hidden Ability '{hidden_ability_name}' not found. Using original.")
                    
                    updated_line = f"+#{name_part}#, {', '.join(parts)}"
                    full_output_lines.append(updated_line)
                else:
                    full_output_lines.append(original_line)

        with open(output_tfl_filename, 'w', encoding='utf-8') as f:
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
