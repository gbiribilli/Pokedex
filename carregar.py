import os
import sys
import json
from datetime import datetime, timezone
import psycopg
from pymongo import MongoClient
from pymongo.server_api import ServerApi

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def load_dotenv():
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k, v = k.strip(), v.strip().strip("'\"")
                    if k not in os.environ:
                        os.environ[k] = v

load_dotenv()

# Configuração de Banco de Dados
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

PG_HOST = os.getenv("PGHOST", "localhost")
PG_PORT = int(os.getenv("PGPORT", "5432"))
PG_USER = os.getenv("PGUSER", "postgres")
PG_PASSWORD = os.getenv("PGPASSWORD", "postgres")
PG_DBNAME = os.getenv("PGDATABASE", "postgres")


# Mapeamento manual de normalização para casos de exceção da fonte
MANUAL_MAPPING = {
    # Linha 63 - dado ausente (Primeape)
    "": "primeape",
    # Caracteres especiais e pontuação
    "Nidoran♀": "nidoran-f",
    "Nidoran♂": "nidoran-m",
    "Farfetch'd": "farfetchd",
    "Mr. Mime": "mr-mime",
    "Mime Jr.": "mime-jr",
    "Flabébé": "flabebe",
    # Formas com gênero / sufixo no PokéAPI
    "Frillish": "frillish-male",
    "Jellicent": "jellicent-male",
    "Pyroar": "pyroar-male",
    "Meowstic Male": "meowstic-male",
    "Meowstic Female": "meowstic-female",
    "Basculin": "basculin-red-striped",
    # Formas Mega e Primal
    "Mega Venusaur": "venusaur-mega",
    "Mega Charizard X": "charizard-mega-x",
    "Mega Charizard Y": "charizard-mega-y",
    "Mega Blastoise": "blastoise-mega",
    "Mega Alakazam": "alakazam-mega",
    "Mega Gengar": "gengar-mega",
    "Mega Kangaskhan": "kangaskhan-mega",
    "Mega Pinsir": "pinsir-mega",
    "Mega Gyarados": "gyarados-mega",
    "Mega Aerodactyl": "aerodactyl-mega",
    "Mega Mewtwo X": "mewtwo-mega-x",
    "Mega Mewtwo Y": "mewtwo-mega-y",
    "Mega Ampharos": "ampharos-mega",
    "Mega Steelix": "steelix-mega",
    "Mega Scizor": "scizor-mega",
    "Mega Heracross": "heracross-mega",
    "Mega Houndoom": "houndoom-mega",
    "Mega Tyranitar": "tyranitar-mega",
    "Mega Sceptile": "sceptile-mega",
    "Mega Blaziken": "blaziken-mega",
    "Mega Swampert": "swampert-mega",
    "Mega Gardevoir": "gardevoir-mega",
    "Mega Sableye": "sableye-mega",
    "Mega Mawile": "mawile-mega",
    "Mega Aggron": "aggron-mega",
    "Mega Medicham": "medicham-mega",
    "Mega Manectric": "manectric-mega",
    "Mega Sharpedo": "sharpedo-mega",
    "Mega Camerupt": "camerupt-mega",
    "Mega Altaria": "altaria-mega",
    "Mega Banette": "banette-mega",
    "Mega Absol": "absol-mega",
    "Mega Glalie": "glalie-mega",
    "Mega Salamence": "salamence-mega",
    "Mega Metagross": "metagross-mega",
    "Mega Latias": "latias-mega",
    "Mega Latios": "latios-mega",
    "Primal Kyogre": "kyogre-primal",
    "Primal Groudon": "groudon-primal",
    "Mega Rayquaza": "rayquaza-mega",
    "Mega Lopunny": "lopunny-mega",
    "Mega Garchomp": "garchomp-mega",
    "Mega Lucario": "lucario-mega",
    "Mega Abomasnow": "abomasnow-mega",
    "Mega Gallade": "gallade-mega",
    "Mega Audino": "audino-mega",
    "Mega Diancie": "diancie-mega",
    # Rotom Formas
    "Heat Rotom": "rotom-heat",
    "Wash Rotom": "rotom-wash",
    "Frost Rotom": "rotom-frost",
    "Fan Rotom": "rotom-fan",
    "Mow Rotom": "rotom-mow",
    # Deoxys
    "Deoxys Normal Forme": "deoxys-normal",
    "Deoxys Attack Forme": "deoxys-attack",
    "DeoxysAttack Forme": "deoxys-attack",
    "Deoxys Defense Forme": "deoxys-defense",
    "Deoxys Speed Forme": "deoxys-speed",
    # Wormadam
    "Wormadam Plant Cloak": "wormadam-plant",
    "Wormadam Sandy Cloak": "wormadam-sandy",
    "Wormadam Trash Cloak": "wormadam-trash",
    # Giratina, Shaymin, Darmanitan
    "Giratina Altered Forme": "giratina-altered",
    "Giratina Origin Forme": "giratina-origin",
    "Shaymin Land Forme": "shaymin-land",
    "Shaymin Sky Forme": "shaymin-sky",
    "Darmanitan Standard Mode": "darmanitan-standard",
    "Darmanitan Zen Mode": "darmanitan-zen",
    # Therian Formes
    "Tornadus Incarnate Forme": "tornadus-incarnate",
    "Tornadus Therian Forme": "tornadus-therian",
    "Thundurus Incarnate Forme": "thundurus-incarnate",
    "Thundurus Therian Forme": "thundurus-therian",
    "Landorus Incarnate Forme": "landorus-incarnate",
    "Landorus Therian Forme": "landorus-therian",
    # Kyurem
    "Kyurem Black": "kyurem-black",
    "Kyurem White": "kyurem-white",
    "Kyurem Black Kyurem": "kyurem-black",
    "Kyurem White Kyurem": "kyurem-white",
    # Keldeo, Meloetta, Aegislash
    "Keldeo Ordinary Forme": "keldeo-ordinary",
    "Keldeo Resolute Forme": "keldeo-resolute",
    "Meloetta Aria Forme": "meloetta-aria",
    "Meloetta Pirouette Forme": "meloetta-pirouette",
    "Aegislash Shield Forme": "aegislash-shield",
    "Aegislash Blade Forme": "aegislash-blade",
    # Pumpkaboo e Gourgeist
    "Pumpkaboo Average Size": "pumpkaboo-average",
    "Pumpkaboo Small Size": "pumpkaboo-small",
    "Pumpkaboo Large Size": "pumpkaboo-large",
    "Pumpkaboo Super Size": "pumpkaboo-super",
    "Gourgeist Average Size": "gourgeist-average",
    "Gourgeist Small Size": "gourgeist-small",
    "Gourgeist Large Size": "gourgeist-large",
    "Gourgeist Super Size": "gourgeist-super",
    # Zygarde e Hoopa
    "Zygarde Half Forme": "zygarde-50",
    "Hoopa Confined": "hoopa",
    "Hoopa Unbound": "hoopa-unbound",
    "Hoopa": "hoopa",
}

# Tipos oficiais (1 a 18) e mapeamento de nomes em português e inglês
TIPOS_MAP = {
    1: ("Normal", "normal"),
    2: ("Lutador", "fighting"),
    3: ("Voador", "flying"),
    4: ("Venenoso", "poison"),
    5: ("Terrestre", "ground"),
    6: ("Pedra", "rock"),
    7: ("Inseto", "bug"),
    8: ("Fantasma", "ghost"),
    9: ("Aço", "steel"),
    10: ("Fogo", "fire"),
    11: ("Água", "water"),
    12: ("Planta", "grass"),
    13: ("Elétrico", "electric"),
    14: ("Psíquico", "psychic"),
    15: ("Gelo", "ice"),
    16: ("Dragão", "dragon"),
    17: ("Sombrio", "dark"),
    18: ("Fada", "fairy")
}

GERACOES_INFO = [
    (1, 1, "Geração I", "Kanto"),
    (2, 2, "Geração II", "Johto"),
    (3, 3, "Geração III", "Hoenn"),
    (4, 4, "Geração IV", "Sinnoh"),
    (5, 5, "Geração V", "Unova"),
    (6, 6, "Geração VI", "Kalos"),
]

def normalize_name(raw_name, pokeapi_by_name):
    raw_name_clean = raw_name.strip()
    if raw_name_clean in MANUAL_MAPPING:
        return MANUAL_MAPPING[raw_name_clean]
    
    name = raw_name_clean.lower()
    name = name.replace("'", "").replace(".", "").replace(":", "").replace("%", "")
    name = name.replace("♀", "-f").replace("♂", "-m").replace("é", "e")
    name = name.replace(" ", "-")
    
    if name in pokeapi_by_name:
        return name
    
    if name.startswith("mega-"):
        cand = name[5:] + "-mega"
        if cand in pokeapi_by_name:
            return cand
    
    return name

def conectar_mongo():
    if "mongodb+srv://" in MONGO_URI:
        client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
    else:
        client = MongoClient(MONGO_URI)
    return client["pokedex_bronze"]

def conectar_postgres():
    return psycopg.connect(
        host=PG_HOST,
        port=PG_PORT,
        user=PG_USER,
        password=PG_PASSWORD,
        dbname=PG_DBNAME,
        options="-c client_encoding=utf8"
    )

def carregar_silver():
    print("Iniciando carga da Camada 🥈 Silver no PostgreSQL...")
    
    # 1. Executar DDL
    pg_conn = conectar_postgres()
    pg_conn.autocommit = True
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sql_path = os.path.join(script_dir, "sql", "silver.sql")
    with open(sql_path, "r", encoding="utf-8") as f:
        ddl_sql = f.read()
    
    with pg_conn.cursor() as cur:
        cur.execute(ddl_sql)
    print("DDL sql/silver.sql executado com sucesso.")

    # 2. Ler dados brutos exclusivamente do MongoDB
    print("Lendo documentos da camada Bronze (MongoDB)...")
    db_mongo = conectar_mongo()
    
    pokemon_docs = list(db_mongo["pokemon"].find({}))
    species_docs = list(db_mongo["especies"].find({}))
    types_docs = list(db_mongo["tipos"].find({}))
    pcsv_docs = list(db_mongo["pokemon_csv"].find({}))
    combates_docs = list(db_mongo["combates"].find({}))

    print(f"Documentos lidos do Bronze: {len(pokemon_docs)} pokemon, {len(species_docs)} especies, {len(types_docs)} tipos, {len(pcsv_docs)} pokemon_csv, {len(combates_docs)} combates.")

    # Indexar dados do bronze em memória
    pokeapi_by_name = {doc["name"].lower(): doc for doc in pokemon_docs}
    pokeapi_by_id = {doc["id"]: doc for doc in pokemon_docs}
    species_by_id = {doc["id"]: doc for doc in species_docs}
    types_by_id = {doc["id"]: doc for doc in types_docs}
    types_by_name = {doc["name"].lower(): doc for doc in types_docs}

    # Limpar tabelas da silver para repovoamento idempotente (ordem inversa de FKs)
    with pg_conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE silver.fato_confronto, silver.efetividade_tipo, silver.log_conciliacao, silver.dim_pokemon, silver.dim_tipo, silver.dim_geracao CASCADE;")

    # 3. Povoar silver.dim_geracao
    print("Carregando silver.dim_geracao...")
    with pg_conn.cursor() as cur:
        for row in GERACOES_INFO:
            cur.execute("""
                INSERT INTO silver.dim_geracao (id_geracao, numero_geracao, nome_geracao, regiao_principal)
                VALUES (%s, %s, %s, %s);
            """, row)

    # 4. Povoar silver.dim_tipo
    print("Carregando silver.dim_tipo...")
    # Membro especial para tipo inexistente / ausente
    tipo_name_to_sk = {}
    with pg_conn.cursor() as cur:
        # Membro Especial (RS4)
        cur.execute("""
            INSERT INTO silver.dim_tipo (id_tipo, id_tipo_natural, nome_tipo, nome_tipo_en)
            VALUES (-1, -1, 'Nenhum', 'none');
        """)
        tipo_name_to_sk["none"] = -1
        tipo_name_to_sk["nenhum"] = -1
        tipo_name_to_sk[""] = -1

        for sk, (pt_name, en_name) in TIPOS_MAP.items():
            cur.execute("""
                INSERT INTO silver.dim_tipo (id_tipo, id_tipo_natural, nome_tipo, nome_tipo_en)
                VALUES (%s, %s, %s, %s);
            """, (sk, sk, pt_name, en_name))
            tipo_name_to_sk[en_name.lower()] = sk
            tipo_name_to_sk[pt_name.lower()] = sk

    # 5. Povoar silver.efetividade_tipo (324 combinações: 18 x 18)
    print("Carregando silver.efetividade_tipo (matriz 18x18)...")
    efetividade_matriz = {}  # (id_tipo_atacante, id_tipo_defensor) -> multiplicador
    with pg_conn.cursor() as cur:
        for atk_id in range(1, 19):
            atk_doc = types_by_id.get(atk_id, {})
            damage_rel = atk_doc.get("damage_relations", {})
            
            # Conjuntos de modificadores
            double_to = {d["name"].lower() for d in damage_rel.get("double_damage_to", [])}
            half_to = {d["name"].lower() for d in damage_rel.get("half_damage_to", [])}
            no_to = {d["name"].lower() for d in damage_rel.get("no_damage_to", [])}

            for def_id in range(1, 19):
                def_en_name = TIPOS_MAP[def_id][1]
                if def_en_name in no_to:
                    mult = 0.0
                elif def_en_name in half_to:
                    mult = 0.5
                elif def_en_name in double_to:
                    mult = 2.0
                else:
                    mult = 1.0

                efetividade_matriz[(atk_id, def_id)] = mult
                cur.execute("""
                    INSERT INTO silver.efetividade_tipo (id_tipo_atacante, id_tipo_defensor, multiplicador)
                    VALUES (%s, %s, %s);
                """, (atk_id, def_id, mult))

    # 6. Conciliar e Povoar silver.dim_pokemon e silver.log_conciliacao
    print("Conciliando e carregando silver.dim_pokemon...")
    pcsv_docs_sorted = sorted(pcsv_docs, key=lambda x: int(x["#"]))
    
    csv_id_to_pokemon_sk = {}
    csv_id_to_stats = {}
    
    timestamp_proc = datetime.now(timezone.utc)

    with pg_conn.cursor() as cur:
        for pcsv in pcsv_docs_sorted:
            csv_id = int(pcsv["#"])
            raw_name = pcsv.get("Name", "")
            target_name = normalize_name(raw_name, pokeapi_by_name)
            
            matched_pokeapi = pokeapi_by_name.get(target_name)
            
            # Extração de atributos e resolução de espécie base
            if matched_pokeapi:
                pokedex_id = matched_pokeapi["id"]
                pokeapi_name = matched_pokeapi["name"]
                species_url = matched_pokeapi.get("species", {}).get("url", "")
                base_sp_id = int(species_url.rstrip("/").split("/")[-1]) if species_url else pokedex_id
                sp_doc = species_by_id.get(base_sp_id, {})
                
                # Herança de atributos de espécie
                is_legendary = sp_doc.get("is_legendary", False) or (pcsv.get("Legendary", "False").lower() == "true")
                is_mythical = sp_doc.get("is_mythical", False)
                is_baby = sp_doc.get("is_baby", False)
                
                if is_legendary:
                    categoria_raridade = "Lendário"
                elif is_mythical:
                    categoria_raridade = "Mítico"
                elif is_baby:
                    categoria_raridade = "Bebê"
                else:
                    categoria_raridade = "Comum"

                is_forma_alt = not matched_pokeapi.get("is_default", True)
                if "mega" in pokeapi_name:
                    tipo_forma = "Mega"
                elif "primal" in pokeapi_name:
                    tipo_forma = "Primal"
                elif is_forma_alt:
                    tipo_forma = "Forma Alternativa"
                else:
                    tipo_forma = "Padrão"

                altura_m = (matched_pokeapi.get("height", 0) / 10.0) if matched_pokeapi.get("height") is not None else None
                peso_kg = (matched_pokeapi.get("weight", 0) / 10.0) if matched_pokeapi.get("weight") is not None else None
                experiencia_base = matched_pokeapi.get("base_experience")
                taxa_captura = sp_doc.get("capture_rate")
                felicidade_base = sp_doc.get("base_happiness")
                
                # Problema 3: habitat inexistente após Gen 3 é conceito inaplicável
                raw_habitat = sp_doc.get("habitat")
                habitat = raw_habitat["name"] if isinstance(raw_habitat, dict) else ("Inaplicável" if int(pcsv.get("Generation", 1)) > 3 else "Não Informado")
                
                raw_cor = sp_doc.get("color")
                cor = raw_cor["name"] if isinstance(raw_cor, dict) else None
                
                raw_shape = sp_doc.get("shape")
                forma_corporal = raw_shape["name"] if isinstance(raw_shape, dict) else None

                estrategia_log = "Tratamento Específico/Exceção de Domínio" if (raw_name in MANUAL_MAPPING or not raw_name) else "Normalização Padrão de Nomenclatura"
                nome_legivel = "Primeape" if (not raw_name and csv_id == 63) else raw_name
            else:
                # Membro especial / fallback seguro se houvesse não conciliado
                pokedex_id = None
                pokeapi_name = None
                base_sp_id = None
                categoria_raridade = "Comum"
                is_legendary = False
                is_mythical = False
                is_baby = False
                is_forma_alt = False
                tipo_forma = "Desconhecido"
                altura_m = None
                peso_kg = None
                experiencia_base = None
                taxa_captura = None
                felicidade_base = None
                habitat = "Desconhecido"
                cor = None
                forma_corporal = None
                estrategia_log = "Não Conciliado"
                nome_legivel = raw_name if raw_name else "Desconhecido"

            # Sanitização de caracteres para compatibilidade com qualquer encoding do servidor Postgres (ex: WIN1252 / LATIN1)
            nome_legivel_db = nome_legivel.replace("♀", " F").replace("♂", " M").replace("é", "e")
            raw_name_log = raw_name.replace("♀", " F").replace("♂", " M").replace("é", "e") if raw_name else "(Dado Ausente - Linha 63)"


            # Resolução de Tipos
            t1_str = pcsv.get("Type 1", "").strip().lower()
            t2_str = pcsv.get("Type 2", "").strip().lower()
            id_t1 = tipo_name_to_sk.get(t1_str, -1)
            id_t2 = tipo_name_to_sk.get(t2_str, -1)

            # Resolução de Geração
            id_geracao = int(pcsv.get("Generation", 1))

            # Status numéricos
            hp = int(pcsv.get("HP", 0))
            atk = int(pcsv.get("Attack", 0))
            defe = int(pcsv.get("Defense", 0))
            sp_atk = int(pcsv.get("Sp. Atk", 0))
            sp_def = int(pcsv.get("Sp. Def", 0))
            speed = int(pcsv.get("Speed", 0))
            total_status = hp + atk + defe + sp_atk + sp_def + speed

            sk_pokemon = csv_id  # Chave substituta consistente com índice dimensional

            csv_id_to_pokemon_sk[csv_id] = sk_pokemon
            csv_id_to_stats[csv_id] = {
                "id_pokemon": sk_pokemon,
                "id_tipo_primario": id_t1,
                "id_tipo_secundario": id_t2,
                "id_geracao": id_geracao,
                "velocidade": speed,
                "ataque": atk,
                "defesa": defe,
                "total_status": total_status,
                "nome": nome_legivel
            }

            cur.execute("""
                INSERT INTO silver.dim_pokemon (
                    id_pokemon, id_pokemon_csv, id_pokedex, id_especie, nome_pokemon, nome_pokeapi,
                    id_tipo_primario, id_tipo_secundario, id_geracao, categoria_raridade,
                    is_lendario, is_mitico, is_bebe, is_forma_alternativa, tipo_forma,
                    hp, ataque, defesa, ataque_especial, defesa_especial, velocidade, total_status,
                    altura_m, peso_kg, experiencia_base, taxa_captura, felicidade_base,
                    habitat, cor, forma_corporal
                ) VALUES (
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s
                );
            """, (
                sk_pokemon, csv_id, pokedex_id, base_sp_id, nome_legivel_db, pokeapi_name,
                id_t1, id_t2, id_geracao, categoria_raridade,
                is_legendary, is_mythical, is_baby, is_forma_alt, tipo_forma,
                hp, atk, defe, sp_atk, sp_def, speed, total_status,
                altura_m, peso_kg, experiencia_base, taxa_captura, felicidade_base,
                habitat, cor, forma_corporal
            ))

            cur.execute("""
                INSERT INTO silver.log_conciliacao (
                    id_pokemon_csv, nome_csv, id_pokedex, nome_pokeapi, id_especie, status, estrategia, processado_em
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """, (
                csv_id, raw_name_log,
                pokedex_id, pokeapi_name, base_sp_id,
                "CONCILIADO" if matched_pokeapi else "NAO_CONCILIADO",
                estrategia_log, timestamp_proc
            ))


    # 7. Povoar silver.fato_confronto (100.000 linhas = 2 por combate)
    print("Transformando e carregando silver.fato_confronto (100.000 participações)...")
    
    def calcular_efetividade(id_atk_t1, id_def_t1, id_def_t2):
        # Efetividade primária (vs tipo 1 defensor)
        mult_prim = efetividade_matriz.get((id_atk_t1, id_def_t1), 1.0)
        # Efetividade total (multiplica tipo 2 defensor se existir)
        mult_sec = efetividade_matriz.get((id_atk_t1, id_def_t2), 1.0) if id_def_t2 > 0 else 1.0
        return mult_prim, (mult_prim * mult_sec)

    fato_rows = []
    fato_sk_counter = 1

    for c_doc in combates_docs:
        c_id_raw = c_doc.get("_id", "combate/0")
        try:
            id_combate = int(c_id_raw.split("/")[-1])
        except:
            id_combate = fato_sk_counter

        c1_id = int(c_doc["First_pokemon"])
        c2_id = int(c_doc["Second_pokemon"])
        winner_id = int(c_doc["Winner"])

        p1 = csv_id_to_stats[c1_id]
        p2 = csv_id_to_stats[c2_id]

        p1_won = 1 if winner_id == c1_id else 0
        p2_won = 1 if winner_id == c2_id else 0

        p1_mult_prim, p1_mult_tot = calcular_efetividade(p1["id_tipo_primario"], p2["id_tipo_primario"], p2["id_tipo_secundario"])
        p2_mult_prim, p2_mult_tot = calcular_efetividade(p2["id_tipo_primario"], p1["id_tipo_primario"], p1["id_tipo_secundario"])

        # Linha 1: Participação do Pokémon 1 (Primeiro Atacante)
        fato_rows.append((
            fato_sk_counter,
            id_combate,
            p1["id_pokemon"],
            p2["id_pokemon"],
            p1["id_tipo_primario"],
            p2["id_tipo_primario"],
            p1["id_geracao"],
            1,  # primeiro_a_atacar
            p1_won,
            p1["velocidade"] - p2["velocidade"],
            p1["ataque"] - p2["ataque"],
            p1["defesa"] - p2["defesa"],
            p1["total_status"] - p2["total_status"],
            p1_mult_prim,
            p1_mult_tot
        ))
        fato_sk_counter += 1

        # Linha 2: Participação do Pokémon 2 (Segundo Atacante)
        fato_rows.append((
            fato_sk_counter,
            id_combate,
            p2["id_pokemon"],
            p1["id_pokemon"],
            p2["id_tipo_primario"],
            p1["id_tipo_primario"],
            p2["id_geracao"],
            0,  # primeiro_a_atacar
            p2_won,
            p2["velocidade"] - p1["velocidade"],
            p2["ataque"] - p1["ataque"],
            p2["defesa"] - p1["defesa"],
            p2["total_status"] - p1["total_status"],
            p2_mult_prim,
            p2_mult_tot
        ))
        fato_sk_counter += 1

    # Inserção em lotes de 10.000 para alto desempenho
    batch_size = 10000
    with pg_conn.cursor() as cur:
        for i in range(0, len(fato_rows), batch_size):
            batch = fato_rows[i:i + batch_size]
            cur.executemany("""
                INSERT INTO silver.fato_confronto (
                    id_fato, id_combate, id_pokemon, id_oponente,
                    id_tipo_primario_pokemon, id_tipo_primario_oponente, id_geracao_pokemon,
                    primeiro_a_atacar, venceu,
                    diferenca_velocidade, diferenca_ataque, diferenca_defesa, diferenca_total_status,
                    multiplicador_efetividade_primario, multiplicador_efetividade_total
                ) VALUES (
                    %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s,
                    %s, %s, %s, %s,
                    %s, %s
                );
            """, batch)

    print("\n--- Camada Silver carregada com sucesso! ---")
    with pg_conn.cursor() as cur:
        for tbl in ["dim_geracao", "dim_tipo", "efetividade_tipo", "dim_pokemon", "log_conciliacao", "fato_confronto"]:
            cur.execute(f"SELECT COUNT(*) FROM silver.{tbl};")
            count = cur.fetchone()[0]
            print(f"  - silver.{tbl}: {count} linhas")

    pg_conn.close()

if __name__ == "__main__":
    carregar_silver()
