document.addEventListener('DOMContentLoaded', () => {
    // --- Global State ---
    let basePokemonData = [];
    let allAbilities = [];
    let allTypes = [];
    let customPokemon = {}; // Store custom edits by name

    // --- DOM Elements ---
    const selectElement = document.getElementById('pokemon-select');
    const editorGrid = document.getElementById('editor-grid');
    const commitBtn = document.getElementById('commit-btn');
    const editedList = document.getElementById('edited-list');
    const downloadBtn = document.getElementById('download-btn');

    // --- Utility Functions ---
    const getStatTierClass = (stat) => {
        const s = parseInt(stat, 10);
        if (s >= 150) return 'stat-tier-1';
        if (s >= 120) return 'stat-tier-2';
        if (s >= 100) return 'stat-tier-3';
        if (s >= 90) return 'stat-tier-4';
        if (s >= 60) return 'stat-tier-5';
        return 'stat-tier-6';
    };

    // --- NEW: A separate color scale specifically for the BST ---
    const getBstTierClass = (bst) => {
        const s = parseInt(bst, 10);
        if (s >= 700) return 'stat-tier-1'; // Legendary
        if (s >= 600) return 'stat-tier-2'; // Excellent
        if (s >= 500) return 'stat-tier-3'; // Good
        if (s >= 400) return 'stat-tier-4'; // Average
        if (s >= 300) return 'stat-tier-5'; // Below Average
        return 'stat-tier-6'; // Poor
    };

    const getTypeClass = (type) => `type-${type ? type.toLowerCase().replace(' ', '-') : ''}`;
    
    // --- Core Functions ---
    async function initialize() {
        try {
            const response = await fetch('../pokemon_cache.json');
            if (!response.ok) {
                throw new Error("pokemon_cache.json not found. Please make sure it is in the root folder, outside the 'script' folder.");
            }
            basePokemonData = await response.json();

            basePokemonData.forEach(p => {
                p.BST = (p.HP || 0) + (p.Attack || 0) + (p.Defense || 0) + (p['Sp Atk'] || 0) + (p['Sp Def'] || 0) + (p.Speed || 0);
            });
            
            const abilitySet = new Set();
            const typeSet = new Set();
            basePokemonData.forEach(p => {
                if (p['Ability 1']) abilitySet.add(p['Ability 1']);
                if (p['Ability 2']) abilitySet.add(p['Ability 2']);
                if (p['Hidden Ability']) abilitySet.add(p['Hidden Ability']);
                if (p['Type 1']) typeSet.add(p['Type 1']);
                if (p['Type 2']) typeSet.add(p['Type 2']);
            });
            allAbilities = Array.from(abilitySet).sort();
            allTypes = Array.from(typeSet).sort();

            updatePokemonSelector();
            selectElement.dispatchEvent(new Event('change'));
        } catch (error) {
            document.body.innerHTML = `<div class="p-8 text-center text-red-500 font-bold">${error.message}</div>`;
        }
    }

    function updatePokemonSelector() {
        const currentSelection = selectElement.value;
        const allNames = [...new Set([...Object.keys(customPokemon), ...basePokemonData.map(p => p.Name)])].sort();
        
        selectElement.innerHTML = allNames.map(name => `<option value="${name}">${name}</option>`).join('');
        selectElement.value = currentSelection || allNames[0];
    }
    
    function displayPokemon(name) {
        const data = customPokemon[name] || basePokemonData.find(p => p.Name === name);
        if (!data) return;

        let gridHtml = `
            <!-- Header Row -->
            <div class="text-gray-600 font-semibold">Category</div>
            <div class="text-2xl font-semibold text-gray-800 border-b pb-2 mb-2">Original</div>
            <div class="text-2xl font-semibold text-gray-800 border-b pb-2 mb-2">Edited</div>

            <!-- Ability Rows -->
            ${generateRow('Ability 1', data['Ability 1'], 'ability')}
            ${generateRow('Ability 2', data['Ability 2'], 'ability')}
            ${generateRow('Hidden Ability', data['Hidden Ability'], 'ability')}
            
            <!-- Type Rows -->
            ${generateRow('Type 1', data['Type 1'], 'type')}
            ${generateRow('Type 2', data['Type 2'], 'type')}

            <!-- Separator -->
            <div class="col-span-3 h-px bg-gray-200 my-2"></div>

            <!-- Stat Rows -->
            ${generateRow('HP', data.HP, 'stat')}
            ${generateRow('Attack', data.Attack, 'stat')}
            ${generateRow('Defense', data.Defense, 'stat')}
            ${generateRow('Sp Atk', data['Sp Atk'], 'stat')}
            ${generateRow('Sp Def', data['Sp Def'], 'stat')}
            ${generateRow('Speed', data.Speed, 'stat')}
            
            <!-- Separator -->
            <div class="col-span-3 h-px bg-gray-200 my-2"></div>

            <!-- BST Rows -->
            ${generateRow('BST', data.BST, 'bst')}
        `;

        editorGrid.innerHTML = gridHtml;

        const statInputs = editorGrid.querySelectorAll('input[type="number"]');
        statInputs.forEach(input => input.addEventListener('input', () => calculateBst(name)));
        
        const typeSelects = editorGrid.querySelectorAll('select[id^="edit-type"]');
        typeSelects.forEach(select => select.addEventListener('change', () => calculateBst(name)));

        calculateBst(name);
    }

    function generateRow(label, value, type) {
        const id = `edit-${label.toLowerCase().replace(/ /g, '-')}`;
        let originalHtml = '';
        let editedHtml = '';

        switch(type) {
            case 'ability':
                originalHtml = `<div class="text-right">${value || 'N/A'}</div>`;
                editedHtml = `
                    <select id="${id}" class="w-full p-1 border rounded-md">
                        <option value="">-- Keep Original --</option>
                        ${allAbilities.map(o => `<option value="${o}">${o}</option>`).join('')}
                    </select>`;
                break;
            case 'type':
                 originalHtml = `<div class="flex justify-end">${value ? `<span class="px-3 py-1 rounded-full text-sm font-semibold ${getTypeClass(value)}">${value}</span>` : 'N/A'}</div>`;
                 editedHtml = `
                    <select id="${id}" class="w-full p-1 border rounded-md">
                        <option value="">-- Keep Original --</option>
                        ${allTypes.map(o => `<option value="${o}">${o}</option>`).join('')}
                    </select>`;
                break;
            case 'stat':
                originalHtml = `<div class="flex justify-end"><span class="font-bold text-gray-800 px-3 py-1 rounded w-full text-center ${getStatTierClass(value)}">${value}</span></div>`;
                editedHtml = `<input type="number" id="${id}" class="w-full p-1 border rounded-md text-right" placeholder="Original">`;
                break;
            case 'bst':
                originalHtml = `<div class="text-right font-bold">${value || 'N/A'}</div>`;
                editedHtml = `<div class="flex justify-end"><span id="calculated-bst" class="font-bold text-gray-800 px-3 py-1 rounded w-full text-center"></span></div>`;
                break;
        }

        return `<div class="text-gray-600">${label}:</div>${originalHtml}${editedHtml}`;
    }

    function calculateBst(name) {
        let bst = 0;
        const originalData = customPokemon[name] || basePokemonData.find(p => p.Name === name);
        const originalStats = {
            HP: originalData.HP, Attack: originalData.Attack, Defense: originalData.Defense,
            'Sp Atk': originalData['Sp Atk'], 'Sp Def': originalData['Sp Def'], Speed: originalData.Speed
        };

        Object.keys(originalStats).forEach(field => {
            const input = editorGrid.querySelector(`#edit-${field.toLowerCase().replace(/ /g, '-')}`);
            const value = parseInt(input.value, 10);
            bst += !isNaN(value) && value > 0 ? value : parseInt(originalStats[field], 10);
        });
        
        const bstDisplay = editorGrid.querySelector('#calculated-bst');
        if (bstDisplay) {
            bstDisplay.textContent = bst;
            // --- FIX: Use the new BST-specific color function ---
            bstDisplay.className = `font-bold text-gray-800 px-3 py-1 rounded w-full text-center ${getBstTierClass(bst)}`;
        }
    }

    function updateCustomList() {
        if (Object.keys(customPokemon).length === 0) {
            editedList.innerHTML = `<p class="text-gray-500">Your custom Pokémon will appear here.</p>`;
            return;
        }
        editedList.innerHTML = Object.values(customPokemon).map(p => `
            <div class="p-2 rounded bg-gray-200 text-gray-800 cursor-pointer hover:bg-indigo-200" onclick="document.getElementById('pokemon-select').value='${p.Name}'; document.getElementById('pokemon-select').dispatchEvent(new Event('change'))">
                ${p.Name} <span class="text-xs text-gray-600">(BST: ${p.BST})</span>
            </div>
        `).join('');
    }

    function handleCommit() {
        const selectedName = selectElement.value;
        const originalData = customPokemon[selectedName] || basePokemonData.find(p => p.Name === selectedName);
        
        const getFinalValue = (field, originalValue) => {
            const input = document.getElementById(`edit-${field.toLowerCase().replace(/ /g, '-')}`);
            return input && input.value ? input.value : originalValue;
        };

        const finalData = {
            '#': originalData['#'],
            Name: originalData.Name,
            'Ability 1': getFinalValue('Ability 1', originalData['Ability 1']),
            'Ability 2': getFinalValue('Ability 2', originalData['Ability 2']),
            'Hidden Ability': getFinalValue('Hidden Ability', originalData['Hidden Ability']),
            'Type 1': getFinalValue('Type 1', originalData['Type 1']),
            'Type 2': getFinalValue('Type 2', originalData['Type 2']),
            HP: parseInt(getFinalValue('HP', originalData.HP), 10),
            Attack: parseInt(getFinalValue('Attack', originalData.Attack), 10),
            Defense: parseInt(getFinalValue('Defense', originalData.Defense), 10),
            'Sp Atk': parseInt(getFinalValue('Sp Atk', originalData['Sp Atk']), 10),
            'Sp Def': parseInt(getFinalValue('Sp Def', originalData['Sp Def']), 10),
            Speed: parseInt(getFinalValue('Speed', originalData.Speed), 10),
        };

        finalData.BST = finalData.HP + finalData.Attack + finalData.Defense + finalData['Sp Atk'] + finalData['Sp Def'] + finalData.Speed;

        customPokemon[selectedName] = finalData;
        
        updatePokemonSelector();
        displayPokemon(selectedName);
        updateCustomList();
    }

    function handleDownload() {
        if (Object.keys(customPokemon).length === 0) {
            alert("No custom Pokémon to download!");
            return;
        }
        const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(Object.values(customPokemon), null, 2));
        const downloadAnchorNode = document.createElement('a');
        downloadAnchorNode.setAttribute("href", dataStr);
        downloadAnchorNode.setAttribute("download", "custom_pokemon.json");
        document.body.appendChild(downloadAnchorNode);
        downloadAnchorNode.click();
        downloadAnchorNode.remove();
    }

    // --- Event Listeners ---
    selectElement.addEventListener('change', (e) => displayPokemon(e.target.value));
    commitBtn.addEventListener('click', handleCommit);
    downloadBtn.addEventListener('click', handleDownload);

    // --- Initial Load ---
    initialize();
});
