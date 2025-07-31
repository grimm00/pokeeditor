\# Pokémon Rebalancing Tool



An interactive, web-based application for editing and rebalancing Pokémon stats, types, and abilities. This tool is designed for Pokémon enthusiasts, fan game creators, and ROM hackers to experiment with changes, save their work, and export complete datasets for use in their own projects.



!\[Tool Screenshot](https://i.imgur.com/example.png) <!-- It's recommended to replace this with an actual screenshot of your tool -->



---



\## Key Features



\-   \*\*Interactive Editor\*\*: A clean, three-column interface to view original Pokémon data and input your custom changes.

\-   \*\*Complete Pokémon Database\*\*: Includes all official Pokémon, including Mega Evolutions, regional forms, and other variants.

\-   \*\*Real-time Calculations\*\*: The Base Stat Total (BST) for your edited Pokémon is calculated and displayed instantly as you type.

\-   \*\*Conditional Formatting\*\*:

&nbsp;   -   Individual stats and the BST are color-coded to reflect their competitive tier.

&nbsp;   -   Pokémon types are displayed with their official, distinct colors for easy recognition.

\-   \*\*Session Management\*\*:

&nbsp;   -   \*\*Upload Custom Data\*\*: Load a previously saved `custom\_pokemon.json` file to resume a rebalancing session or collaborate with others.

&nbsp;   -   \*\*Multiple Export Options\*\*:

&nbsp;       1.  \*\*Download Custom JSON\*\*: Save only your modified Pokémon as a lightweight "patch" file.

&nbsp;       2.  \*\*Download Merged Data\*\*: Export the complete Pokémon dataset with your custom changes applied.

&nbsp;       3.  \*\*Download Base Data\*\*: Get a clean copy of the original dataset.

\-   \*\*Local \& Private\*\*: The entire application runs in your browser and requires no internet connection after the initial setup. All your data stays on your machine.



---



\## Project Structure



The project is organized into a simple, clean folder structure.




```
/Pokemon\_Rebalancing\_Project/

|

|-- script/

|   |-- pokeeditor.js        # The main application logic

|

|-- styles/

|   |-- pokeeditor.css       # All visual styling for the app

|

|-- index.html               # The main HTML file you open

|-- pokemon\_cache.json       # The database of all Pokémon

|

|-- (Optional Utilities)/

|   |-- generate\_cache.py    # Python script to generate/update the cache

|   |-- export\_to\_excel.py   # Python script to export JSON to a formatted Excel file

```



---



\## Setup \& Installation



Follow these steps to get the tool running on your local machine.



\### 1. Generate the Pokémon Database (One-Time Setup)



The application requires the `pokemon\_cache.json` file to function. If you don't have this file, you must generate it.



\-   \*\*Prerequisites\*\*: Ensure you have Python 3 installed.

\-   \*\*Install Libraries\*\*: Open your terminal or command prompt and run:

&nbsp;   ```bash

&nbsp;   pip install pandas requests openpyxl

&nbsp;   ```

\-   \*\*Run the Script\*\*: Navigate to the `(Optional Utilities)` folder and run the data generation script:

&nbsp;   ```bash

&nbsp;   python generate\_cache.py

&nbsp;   ```

&nbsp;   This will create the `pokemon\_cache.json` file in your main project directory. This process only needs to be done once.



\### 2. Run the Web Application



The application needs to be served by a local web server for the browser to allow it to load the JSON file.



\-   \*\*Start the Server\*\*: Open your terminal in the \*\*root\*\* of the project folder (the one containing `index.html`) and run Python's built-in web server:

&nbsp;   ```bash

&nbsp;   python -m http.server

&nbsp;   ```

\-   \*\*Open the App\*\*: Open your web browser and navigate to the following address:

&nbsp;   \[http://localhost:8000](http://localhost:8000)



The Pokémon Rebalancing Tool should now be fully functional.



---



\## How to Use



\-   \*\*Select a Pokémon\*\*: Use the main dropdown to choose a Pokémon to edit. The list includes all base Pokémon and any custom versions you have loaded or created.

\-   \*\*Edit Data\*\*: Fill in any of the fields in the "Edited" column. Any field left blank will automatically keep its original value when you commit the changes.

\-   \*\*Commit Changes\*\*: Click the "Commit Changes" button to save your modifications. This will add the Pokémon to the "Custom Pokémon List" on the right, or update it if it's already there.

\-   \*\*Manage Data\*\*: Use the buttons on the right to upload a custom JSON file, or download your custom changes, the full merged dataset, or the original base data.



