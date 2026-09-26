
import os
import sys
from datetime import datetime, timezone
import psycopg

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

PG_HOST = os.getenv("PGHOST", "localhost")
PG_PORT = int(os.getenv("PGPORT", "5433"))
PG_USER = os.getenv("PGUSER", "postgres")
PG_PASSWORD = os.getenv("PGPASSWORD", "postgres")
PG_DBNAME = os.getenv("PGDATABASE", "postgres")

def conectar_postgres():
    return psycopg.connect(
        host=PG_HOST,
        port=PG_PORT,
        user=PG_USER,
        password=PG_PASSWORD,
        dbname=PG_DBNAME,
        options="-c client_encoding=utf8"
    )

def publicar_gold():
    print("Iniciando publicação da Camada 🥇 Gold no PostgreSQL...")
    
    pg_conn = conectar_postgres()
    pg_conn.autocommit = True
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sql_path = os.path.join(script_dir, "sql", "gold.sql")
    
    with open(sql_path, "r", encoding="utf-8") as f:
        gold_sql = f.read()
        
    print("Executando DDL e agregações SQL no banco (sql/gold.sql)...")
    with pg_conn.cursor() as cur:
        cur.execute(gold_sql)

    print("\n--- Camada Gold publicada com sucesso! ---")
    timestamp_pub = datetime.now(timezone.utc).isoformat()
    print(f"Momento da publicação: {timestamp_pub}")
    
    tabelas_gold = [
        "ranking_pokemon",
        "taxa_vitorias_por_tipo",
        "taxa_vitorias_por_faixa_velocidade",
        "taxa_vitorias_por_multiplicador",
        "matriz_confronto",
        "vantagem_primeiro_ataque_por_geracao_raridade"
    ]
    
    with pg_conn.cursor() as cur:
        for tbl in tabelas_gold:
            cur.execute(f"SELECT COUNT(*) FROM gold.{tbl};")
            count = cur.fetchone()[0]
            print(f"  - gold.{tbl}: {count} linhas")

    pg_conn.close()

if __name__ == "__main__":
    publicar_gold()
