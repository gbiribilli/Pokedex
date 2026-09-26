import os
import sys
import json
import time
import csv
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from pymongo import MongoClient, UpdateOne
from pymongo.server_api import ServerApi

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


# Configurações de Origem
POKEAPI_BASE = "https://pokeapi.co/api/v2"
CSV_POKEMON_URL = "https://raw.githubusercontent.com/cdiener/pokemon_app/master/pokemon.csv"
CSV_COMBATS_URL = "https://raw.githubusercontent.com/cdiener/pokemon_app/master/combats.csv"

# Diretório de Cache
CACHE_DIR = "dados_brutos"
CACHE_SPECIES_DIR = os.path.join(CACHE_DIR, "especies")
CACHE_POKEMON_DIR = os.path.join(CACHE_DIR, "pokemon")
CACHE_TYPES_DIR = os.path.join(CACHE_DIR, "tipos")

os.makedirs(CACHE_SPECIES_DIR, exist_ok=True)
os.makedirs(CACHE_POKEMON_DIR, exist_ok=True)
os.makedirs(CACHE_TYPES_DIR, exist_ok=True)

# Sessão HTTP reutilizável
session = requests.Session()

def get_mongo_client():
    mongo_uri = os.getenv(
        "MONGO_URI",
        "mongodb+srv://fuzeassistir_db_user:txtaBSpXEFX5DMge@pokedexbronze.6fpjwmr.mongodb.net/?appName=pokedexBronze"
    )
    if "mongodb+srv://" in mongo_uri:
        return MongoClient(mongo_uri, server_api=ServerApi('1'))
    return MongoClient(mongo_uri)

def get_with_cache(url, filepath):
    """
    Retorna o JSON do arquivo local se existir (cache hit);
    caso contrário, realiza a requisição HTTP e salva no disco.
    Retorna uma tupla (dados, fez_requisicao_bool).
    """
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f), False

    resp = session.get(url, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    time.sleep(0.05)  # Respeito ao servidor da PokéAPI
    return data, True

def extrair_csvs():
    """Baixa e lê os arquivos CSV de Pokémon e Batalhas."""
    p_path = os.path.join(CACHE_DIR, "pokemon.csv")
    if not os.path.exists(p_path):
        print("Baixando pokemon.csv...")
        r = session.get(CSV_POKEMON_URL, timeout=30)
        r.raise_for_status()
        with open(p_path, "w", encoding="utf-8") as f:
            f.write(r.text)
    
    c_path = os.path.join(CACHE_DIR, "combats.csv")
    if not os.path.exists(c_path):
        print("Baixando combats.csv...")
        r = session.get(CSV_COMBATS_URL, timeout=30)
        r.raise_for_status()
        with open(c_path, "w", encoding="utf-8") as f:
            f.write(r.text)

    with open(p_path, "r", encoding="utf-8") as f:
        pokemon_csv_rows = list(csv.DictReader(f))
        
    with open(c_path, "r", encoding="utf-8") as f:
        combats_csv_rows = list(csv.DictReader(f))

    return pokemon_csv_rows, combats_csv_rows

def extrair_pokeapi():
    """
    Extrai espécies (1 a 721), todas as formas das variedades e tipos (1 a 21).
    """
    print("Extraindo espécies (1 a 721)...")
    species_docs = []
    requisicoes_feitas = 0

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {}
        for sp_id in range(1, 722):
            fp = os.path.join(CACHE_SPECIES_DIR, f"{sp_id}.json")
            url = f"{POKEAPI_BASE}/pokemon-species/{sp_id}"
            futures[executor.submit(get_with_cache, url, fp)] = (sp_id, url)
        
        for future in as_completed(futures):
            sp_id, url = futures[future]
            try:
                data, fetched = future.result()
                if fetched:
                    requisicoes_feitas += 1
                species_docs.append((sp_id, url, data))
            except Exception as e:
                print(f"Erro na espécie {sp_id}: {e}")

    # Extrair URLs de todas as variedades
    pokemon_targets = {}
    for sp_id, url, sp in species_docs:
        for var in sp.get("varieties", []):
            p_url = var["pokemon"]["url"]
            p_id_str = p_url.rstrip("/").split("/")[-1]
            pokemon_targets[p_id_str] = p_url

    print(f"Extraindo formas físicas de Pokémon ({len(pokemon_targets)} formas mapeadas)...")
    pokemon_docs = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {}
        for p_id_str, p_url in pokemon_targets.items():
            fp = os.path.join(CACHE_POKEMON_DIR, f"{p_id_str}.json")
            futures[executor.submit(get_with_cache, p_url, fp)] = (p_id_str, p_url)

        for future in as_completed(futures):
            p_id_str, p_url = futures[future]
            try:
                data, fetched = future.result()
                if fetched:
                    requisicoes_feitas += 1
                pokemon_docs.append((p_id_str, p_url, data))
            except Exception as e:
                print(f"Erro no pokemon {p_id_str}: {e}")

    print("Extraindo tipos (1 a 21)...")
    type_ids = list(range(1, 20)) + [10001, 10002]  # 1..18, 19 (stellar), 10001 (unknown), 10002 (shadow)
    type_docs = []
    for t_id in type_ids:
        fp = os.path.join(CACHE_TYPES_DIR, f"{t_id}.json")
        url = f"{POKEAPI_BASE}/type/{t_id}"
        try:
            data, fetched = get_with_cache(url, fp)
            if fetched:
                requisicoes_feitas += 1
            type_docs.append((t_id, url, data))
        except Exception as e:
            print(f"Erro no tipo {t_id}: {e}")

    print(f"Total de requisições HTTP realizadas nesta execução: {requisicoes_feitas}")
    return species_docs, pokemon_docs, type_docs

def carregar_bronze_mongo():
    """
    Carrega todos os dados brutos no MongoDB 'pokedex_bronze'.
    Garante linhagem e idempotência via upsert.
    """
    client = get_mongo_client()
    db = client["pokedex_bronze"]

    timestamp_ingestao = datetime.now(timezone.utc).isoformat()

    # 1. PokéAPI Dados
    species_docs, pokemon_docs, type_docs = extrair_pokeapi()

    print("Carregando coleção 'especies' no MongoDB...")
    col_especies = db["especies"]
    ops = []
    for sp_id, url, data in species_docs:
        doc = dict(data)
        doc["_id"] = f"especie/{sp_id}"
        doc["_fonte"] = "pokeapi"
        doc["_url"] = url
        doc["_ingerido_em"] = timestamp_ingestao
        ops.append(UpdateOne({"_id": doc["_id"]}, {"$set": doc}, upsert=True))
    if ops:
        col_especies.bulk_write(ops)
    print(f"Coleção 'especies': {col_especies.count_documents({})} documentos.")

    print("Carregando coleção 'pokemon' no MongoDB...")
    col_pokemon = db["pokemon"]
    ops = []
    for p_id_str, url, data in pokemon_docs:
        doc = dict(data)
        doc["_id"] = f"pokemon/{p_id_str}"
        doc["_fonte"] = "pokeapi"
        doc["_url"] = url
        doc["_ingerido_em"] = timestamp_ingestao
        ops.append(UpdateOne({"_id": doc["_id"]}, {"$set": doc}, upsert=True))
    if ops:
        col_pokemon.bulk_write(ops)
    print(f"Coleção 'pokemon': {col_pokemon.count_documents({})} documentos.")

    print("Carregando coleção 'tipos' no MongoDB...")
    col_tipos = db["tipos"]
    ops = []
    for t_id, url, data in type_docs:
        doc = dict(data)
        doc["_id"] = f"tipo/{t_id}"
        doc["_fonte"] = "pokeapi"
        doc["_url"] = url
        doc["_ingerido_em"] = timestamp_ingestao
        ops.append(UpdateOne({"_id": doc["_id"]}, {"$set": doc}, upsert=True))
    if ops:
        col_tipos.bulk_write(ops)
    print(f"Coleção 'tipos': {col_tipos.count_documents({})} documentos.")

    # 2. CSVs
    pokemon_csv_rows, combats_csv_rows = extrair_csvs()

    print("Carregando coleção 'pokemon_csv' no MongoDB...")
    col_pcsv = db["pokemon_csv"]
    ops = []
    for row in pokemon_csv_rows:
        doc = dict(row)
        doc["_id"] = f"pokemon_csv/{row['#']}"
        doc["_fonte"] = "pokemon.csv"
        doc["_url"] = CSV_POKEMON_URL
        doc["_ingerido_em"] = timestamp_ingestao
        ops.append(UpdateOne({"_id": doc["_id"]}, {"$set": doc}, upsert=True))
    if ops:
        col_pcsv.bulk_write(ops)
    print(f"Coleção 'pokemon_csv': {col_pcsv.count_documents({})} documentos.")

    print("Carregando coleção 'combates' no MongoDB...")
    col_combates = db["combates"]
    ops = []
    # Usar lotes de 5000 para escrita eficiente de 50.000 combates
    batch_size = 5000
    for idx, row in enumerate(combats_csv_rows, start=1):
        doc = dict(row)
        doc["_id"] = f"combate/{idx}"
        doc["_fonte"] = "combats.csv"
        doc["_url"] = CSV_COMBATS_URL
        doc["_ingerido_em"] = timestamp_ingestao
        ops.append(UpdateOne({"_id": doc["_id"]}, {"$set": doc}, upsert=True))
        if len(ops) >= batch_size:
            col_combates.bulk_write(ops)
            ops = []
    if ops:
        col_combates.bulk_write(ops)
    print(f"Coleção 'combates': {col_combates.count_documents({})} documentos.")

    print("\n--- Camada Bronze concluída com sucesso! ---")
    for name in ["pokemon", "especies", "tipos", "pokemon_csv", "combates"]:
        print(f"  - pokedex_bronze.{name}: {db[name].count_documents({})} documentos")

if __name__ == "__main__":
    carregar_bronze_mongo()
