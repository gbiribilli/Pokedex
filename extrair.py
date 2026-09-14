from pymongo import MongoClient
from pymongo.server_api import ServerApi
import csv
import requests

pokemonR = requests.get("https://pokeapi.co/api/v2/pokemon/132")
specieR = requests.get("https://pokeapi.co/api/v2/pokemon-species/132/is_legendary")

pokemon = pokemonR.json()
print(pokemon["name"])


uri = "mongodb+srv://fuzeassistir_db_user:txtaBSpXEFX5DMge@pokedexbronze.6fpjwmr.mongodb.net/?appName=pokedexBronze"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

#db = client['Cluster0']
