CREATE SCHEMA IF NOT EXISTS silver;


-- 1. Dimensao Geracao (dim_geracao)

CREATE TABLE IF NOT EXISTS silver.dim_geracao (
    id_geracao INTEGER PRIMARY KEY,
    numero_geracao INTEGER NOT NULL UNIQUE,
    nome_geracao VARCHAR(50) NOT NULL,
    regiao_principal VARCHAR(50) NOT NULL
);


-- 2. Dimensao Tipo (dim_tipo)

CREATE TABLE IF NOT EXISTS silver.dim_tipo (
    id_tipo INTEGER PRIMARY KEY,
    id_tipo_natural INTEGER,
    nome_tipo VARCHAR(50) NOT NULL UNIQUE,
    nome_tipo_en VARCHAR(50) NOT NULL
);


-- 3. Dimensao Pokemon (dim_pokemon)

CREATE TABLE IF NOT EXISTS silver.dim_pokemon (
    id_pokemon INTEGER PRIMARY KEY,
    id_pokemon_csv INTEGER NOT NULL UNIQUE,
    id_pokedex INTEGER,
    id_especie INTEGER,
    nome_pokemon VARCHAR(100) NOT NULL,
    nome_pokeapi VARCHAR(100),
    id_tipo_primario INTEGER NOT NULL REFERENCES silver.dim_tipo(id_tipo),
    id_tipo_secundario INTEGER NOT NULL REFERENCES silver.dim_tipo(id_tipo),
    id_geracao INTEGER NOT NULL REFERENCES silver.dim_geracao(id_geracao),
    categoria_raridade VARCHAR(50) NOT NULL,
    is_lendario BOOLEAN NOT NULL DEFAULT FALSE,
    is_mitico BOOLEAN NOT NULL DEFAULT FALSE,
    is_bebe BOOLEAN NOT NULL DEFAULT FALSE,
    is_forma_alternativa BOOLEAN NOT NULL DEFAULT FALSE,
    tipo_forma VARCHAR(50),
    hp INTEGER NOT NULL,
    ataque INTEGER NOT NULL,
    defesa INTEGER NOT NULL,
    ataque_especial INTEGER NOT NULL,
    defesa_especial INTEGER NOT NULL,
    velocidade INTEGER NOT NULL,
    total_status INTEGER NOT NULL,
    altura_m NUMERIC(6, 2),
    peso_kg NUMERIC(6, 2),
    experiencia_base INTEGER,
    taxa_captura INTEGER,
    felicidade_base INTEGER,
    habitat VARCHAR(50),
    cor VARCHAR(50),
    forma_corporal VARCHAR(50)
);


-- 4. Matriz de Efetividade de Tipos (efetividade_tipo)

CREATE TABLE IF NOT EXISTS silver.efetividade_tipo (
    id_tipo_atacante INTEGER NOT NULL REFERENCES silver.dim_tipo(id_tipo),
    id_tipo_defensor INTEGER NOT NULL REFERENCES silver.dim_tipo(id_tipo),
    multiplicador NUMERIC(3, 2) NOT NULL,
    PRIMARY KEY (id_tipo_atacante, id_tipo_defensor)
);


-- 5. Tabela Fato Confronto (fato_confronto)

CREATE TABLE IF NOT EXISTS silver.fato_confronto (
    id_fato BIGINT PRIMARY KEY,
    id_combate INTEGER NOT NULL,
    id_pokemon INTEGER NOT NULL REFERENCES silver.dim_pokemon(id_pokemon),
    id_oponente INTEGER NOT NULL REFERENCES silver.dim_pokemon(id_pokemon),
    id_tipo_primario_pokemon INTEGER NOT NULL REFERENCES silver.dim_tipo(id_tipo),
    id_tipo_primario_oponente INTEGER NOT NULL REFERENCES silver.dim_tipo(id_tipo),
    id_geracao_pokemon INTEGER NOT NULL REFERENCES silver.dim_geracao(id_geracao),
    primeiro_a_atacar SMALLINT NOT NULL,
    venceu SMALLINT NOT NULL,
    diferenca_velocidade INTEGER NOT NULL,
    diferenca_ataque INTEGER NOT NULL,
    diferenca_defesa INTEGER NOT NULL,
    diferenca_total_status INTEGER NOT NULL,
    multiplicador_efetividade_primario NUMERIC(3, 2) NOT NULL,
    multiplicador_efetividade_total NUMERIC(4, 2) NOT NULL
);

-- Indices para otimizacao analitica
CREATE INDEX IF NOT EXISTS idx_fato_pokemon ON silver.fato_confronto(id_pokemon);
CREATE INDEX IF NOT EXISTS idx_fato_tipo ON silver.fato_confronto(id_tipo_primario_pokemon);
CREATE INDEX IF NOT EXISTS idx_fato_geracao ON silver.fato_confronto(id_geracao_pokemon);
CREATE INDEX IF NOT EXISTS idx_fato_dif_vel ON silver.fato_confronto(diferenca_velocidade);
CREATE INDEX IF NOT EXISTS idx_fato_mult_efet ON silver.fato_confronto(multiplicador_efetividade_primario);


-- 6. Log de Auditoria da Conciliacao (log_conciliacao)

CREATE TABLE IF NOT EXISTS silver.log_conciliacao (
    id_pokemon_csv INTEGER PRIMARY KEY,
    nome_csv VARCHAR(100),
    id_pokedex INTEGER,
    nome_pokeapi VARCHAR(100),
    id_especie INTEGER,
    status VARCHAR(50),
    estrategia VARCHAR(100),
    processado_em TIMESTAMP WITH TIME ZONE
);
