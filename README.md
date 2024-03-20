# Ridership Prediction

By Hantao Xiao, March 2024

## Project Description

The project aims to understand how various events affect the number of people using our services. This interest arose from discussions between ridership and the marketing team. They are particularly curious about the effects of large city events (like Lollapalooza and the Chicago Marathon), sports events at major venues (such as Wrigley Field and Soldier Field). The goal is to create a model that can predict changes in service use based on information about events.

## Project Structure
- `Data/`
  - `Clean/`: Folder for cleaned data.
  - `Raw/`: Folder for raw data.
  - `Event`: Folder for event data.
    - **`event.csv`**: Event data.
  - `instantclient_21_13/`: Folder for Oracle Instant Client. (If your computer successfully connects to the database, you can delete this folder.)

- `Output/`
  - `img/`: Folder for graphs.
  - `Excel/`: Folder for Excel files.

- `Code/`
  - `clean_MLB.py`: Python script to clean MLB data.
  - `pull_data.py`: Python script to pull data from the database.
  - `scrape_MLB.py`: Python script to scrape MLB data.
  - **`final_script.py`**: Python script to run the final analysis.
  - **`event_list.json`**: JSON file for event list.

- `README.md`: Description of the project.


## How to Use

To generate the final analysis, execute final_script.py located in the Code/ directory.

## How to Update Event Data

To add new event data, update the event.csv file in the Data/Event/ directory and the event_list.json file in the Code/ directory.

For instance, to include a new event named 'Test Event' on March 1, 2024, for the 'Midway' station:

- In the event.csv file, add a column titled 'Test Event'.
- In the event_list.json file, insert a new key-value pair: 'Midway': 'Test Event'.