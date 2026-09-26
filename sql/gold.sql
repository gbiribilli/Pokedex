CREATE SCHEMA IF NOT EXISTS gold;

CREATE TABLE IF NOT EXISTS gold.ranking_pokemon (
    id_pokemon INTEGER PRIMARY KEY,
    nome_pokemon VARCHAR(100) NOT NULL,
    tipo_primario VARCHAR(50) NOT NULL,
    total_combates INTEGER NOT NULL,
    total_vitorias INTEGER NOT NULL,
    taxa_vitorias NUMERIC(5, 4) NOT NULL
);

CREATE TABLE IF NOT EXISTS gold.taxa_vitorias_por_tipo (
    tipo_primario VARCHAR(50) PRIMARY KEY,
    total_combates INTEGER NOT NULL,
    total_vitorias INTEGER NOT NULL,
    taxa_vitorias NUMERIC(5, 4) NOT NULL
);

CREATE TABLE IF NOT EXISTS gold.taxa_vitorias_por_faixa_velocidade (
    ordem_faixa INTEGER PRIMARY KEY,
    faixa_velocidade VARCHAR(50) NOT NULL,
    total_combates INTEGER NOT NULL,
    total_vitorias INTEGER NOT NULL,
    taxa_vitorias NUMERIC(5, 4) NOT NULL
);


-- 4. Analise 6: Taxa de Vitorias por Multiplicador de Efetividade (taxa_vitorias_por_multiplicador)

CREATE TABLE IF NOT EXISTS gold.taxa_vitorias_por_multiplicador (
    multiplicador_efetividade NUMERIC(4, 2) PRIMARY KEY,
    total_combates INTEGER NOT NULL,
    total_vitorias INTEGER NOT NULL,
    taxa_vitorias NUMERIC(5, 4) NOT NULL
);


-- 5. Analise 7: Matriz de Confronto entre Tipos (matriz_confronto)

CREATE TABLE IF NOT EXISTS gold.matriz_confronto (
    tipo_atacante VARCHAR(50) NOT NULL,
    tipo_defensor VARCHAR(50) NOT NULL,
    multiplicador_efetividade NUMERIC(3, 2) NOT NULL,
    total_confrontos INTEGER NOT NULL,
    vitorias_atacante INTEGER NOT NULL,
    taxa_vitorias_atacante NUMERIC(5, 4) NOT NULL,
    divergencia_efetividade BOOLEAN NOT NULL,
    PRIMARY KEY (tipo_atacante, tipo_defensor)
);

CREATE TABLE IF NOT EXISTS gold.vantagem_primeiro_ataque_por_geracao_raridade (
    nome_geracao VARCHAR(50) NOT NULL,
    categoria_raridade VARCHAR(50) NOT NULL,
    total_combates_primeiro INTEGER NOT NULL,
    vitorias_primeiro INTEGER NOT NULL,
    taxa_vitorias_primeiro NUMERIC(5, 4) NOT NULL,
    total_combates_segundo INTEGER NOT NULL,
    vitorias_segundo INTEGER NOT NULL,
    taxa_vitorias_segundo NUMERIC(5, 4) NOT NULL,
    diferencial_primeiro_ataque NUMERIC(5, 4) NOT NULL,
    PRIMARY KEY (nome_geracao, categoria_raridade)
);


-- 1. Povoar gold.ranking_pokemon
TRUNCATE TABLE gold.ranking_pokemon;
INSERT INTO gold.ranking_pokemon (
    id_pokemon, nome_pokemon, tipo_primario, total_combates, total_vitorias, taxa_vitorias
)
SELECT 
    p.id_pokemon,
    p.nome_pokemon,
    t.nome_tipo AS tipo_primario,
    COUNT(*)::INTEGER AS total_combates,
    SUM(f.venceu)::INTEGER AS total_vitorias,
    ROUND(AVG(f.venceu)::NUMERIC, 4) AS taxa_vitorias
FROM silver.fato_confronto f
JOIN silver.dim_pokemon p ON f.id_pokemon = p.id_pokemon
JOIN silver.dim_tipo t ON p.id_tipo_primario = t.id_tipo
GROUP BY p.id_pokemon, p.nome_pokemon, t.nome_tipo;

-- 2. Povoar gold.taxa_vitorias_por_tipo
TRUNCATE TABLE gold.taxa_vitorias_por_tipo;
INSERT INTO gold.taxa_vitorias_por_tipo (
    tipo_primario, total_combates, total_vitorias, taxa_vitorias
)
SELECT 
    t.nome_tipo AS tipo_primario,
    COUNT(*)::INTEGER AS total_combates,
    SUM(f.venceu)::INTEGER AS total_vitorias,
    ROUND(AVG(f.venceu)::NUMERIC, 4) AS taxa_vitorias
FROM silver.fato_confronto f
JOIN silver.dim_tipo t ON f.id_tipo_primario_pokemon = t.id_tipo
GROUP BY t.nome_tipo;

-- 3. Povoar gold.taxa_vitorias_por_faixa_velocidade
TRUNCATE TABLE gold.taxa_vitorias_por_faixa_velocidade;
INSERT INTO gold.taxa_vitorias_por_faixa_velocidade (
    ordem_faixa, faixa_velocidade, total_combates, total_vitorias, taxa_vitorias
)
SELECT 
    CASE 
        WHEN f.diferenca_velocidade <= -50 THEN 1
        WHEN f.diferenca_velocidade BETWEEN -49 AND -20 THEN 2
        WHEN f.diferenca_velocidade BETWEEN -19 AND -1 THEN 3
        WHEN f.diferenca_velocidade = 0 THEN 4
        WHEN f.diferenca_velocidade BETWEEN 1 AND 19 THEN 5
        WHEN f.diferenca_velocidade BETWEEN 20 AND 49 THEN 6
        ELSE 7
    END AS ordem_faixa,
    CASE 
        WHEN f.diferenca_velocidade <= -50 THEN '<= -50 (Grande Desvantagem)'
        WHEN f.diferenca_velocidade BETWEEN -49 AND -20 THEN '-49 a -20 (Desvantagem Moderada)'
        WHEN f.diferenca_velocidade BETWEEN -19 AND -1 THEN '-19 a -1 (Ligeira Desvantagem)'
        WHEN f.diferenca_velocidade = 0 THEN '0 (Velocidades Iguais)'
        WHEN f.diferenca_velocidade BETWEEN 1 AND 19 THEN '+1 a +19 (Ligeira Vantagem)'
        WHEN f.diferenca_velocidade BETWEEN 20 AND 49 THEN '+20 a +49 (Vantagem Moderada)'
        ELSE '>= +50 (Grande Vantagem)'
    END AS faixa_velocidade,
    COUNT(*)::INTEGER AS total_combates,
    SUM(f.venceu)::INTEGER AS total_vitorias,
    ROUND(AVG(f.venceu)::NUMERIC, 4) AS taxa_vitorias
FROM silver.fato_confronto f
GROUP BY 1, 2;

-- 4. Povoar gold.taxa_vitorias_por_multiplicador
TRUNCATE TABLE gold.taxa_vitorias_por_multiplicador;
INSERT INTO gold.taxa_vitorias_por_multiplicador (
    multiplicador_efetividade, total_combates, total_vitorias, taxa_vitorias
)
SELECT 
    f.multiplicador_efetividade_primario AS multiplicador_efetividade,
    COUNT(*)::INTEGER AS total_combates,
    SUM(f.venceu)::INTEGER AS total_vitorias,
    ROUND(AVG(f.venceu)::NUMERIC, 4) AS taxa_vitorias
FROM silver.fato_confronto f
GROUP BY f.multiplicador_efetividade_primario;

-- 5. Povoar gold.matriz_confronto
TRUNCATE TABLE gold.matriz_confronto;
INSERT INTO gold.matriz_confronto (
    tipo_atacante, tipo_defensor, multiplicador_efetividade,
    total_confrontos, vitorias_atacante, taxa_vitorias_atacante, divergencia_efetividade
)
SELECT 
    t_atk.nome_tipo AS tipo_atacante,
    t_def.nome_tipo AS tipo_defensor,
    e.multiplicador AS multiplicador_efetividade,
    COUNT(*)::INTEGER AS total_confrontos,
    SUM(f.venceu)::INTEGER AS vitorias_atacante,
    ROUND(AVG(f.venceu)::NUMERIC, 4) AS taxa_vitorias_atacante,
    CASE 
        WHEN (e.multiplicador > 1.0 AND AVG(f.venceu) < 0.50) OR
             (e.multiplicador < 1.0 AND AVG(f.venceu) > 0.50) THEN TRUE
        ELSE FALSE
    END AS divergencia_efetividade
FROM silver.fato_confronto f
JOIN silver.dim_tipo t_atk ON f.id_tipo_primario_pokemon = t_atk.id_tipo
JOIN silver.dim_tipo t_def ON f.id_tipo_primario_oponente = t_def.id_tipo
JOIN silver.efetividade_tipo e ON f.id_tipo_primario_pokemon = e.id_tipo_atacante AND f.id_tipo_primario_oponente = e.id_tipo_defensor
GROUP BY t_atk.nome_tipo, t_def.nome_tipo, e.multiplicador;

-- 6. Povoar gold.vantagem_primeiro_ataque_por_geracao_raridade (Analise Proposta)
TRUNCATE TABLE gold.vantagem_primeiro_ataque_por_geracao_raridade;
INSERT INTO gold.vantagem_primeiro_ataque_por_geracao_raridade (
    nome_geracao, categoria_raridade,
    total_combates_primeiro, vitorias_primeiro, taxa_vitorias_primeiro,
    total_combates_segundo, vitorias_segundo, taxa_vitorias_segundo,
    diferencial_primeiro_ataque
)
SELECT 
    g.nome_geracao,
    p.categoria_raridade,
    SUM(CASE WHEN f.primeiro_a_atacar = 1 THEN 1 ELSE 0 END)::INTEGER AS total_combates_primeiro,
    SUM(CASE WHEN f.primeiro_a_atacar = 1 AND f.venceu = 1 THEN 1 ELSE 0 END)::INTEGER AS vitorias_primeiro,
    ROUND(
        COALESCE(
            SUM(CASE WHEN f.primeiro_a_atacar = 1 AND f.venceu = 1 THEN 1 ELSE 0 END)::NUMERIC / 
            NULLIF(SUM(CASE WHEN f.primeiro_a_atacar = 1 THEN 1 ELSE 0 END), 0),
            0
        ), 4
    ) AS taxa_vitorias_primeiro,
    SUM(CASE WHEN f.primeiro_a_atacar = 0 THEN 1 ELSE 0 END)::INTEGER AS total_combates_segundo,
    SUM(CASE WHEN f.primeiro_a_atacar = 0 AND f.venceu = 1 THEN 1 ELSE 0 END)::INTEGER AS vitorias_segundo,
    ROUND(
        COALESCE(
            SUM(CASE WHEN f.primeiro_a_atacar = 0 AND f.venceu = 1 THEN 1 ELSE 0 END)::NUMERIC / 
            NULLIF(SUM(CASE WHEN f.primeiro_a_atacar = 0 THEN 1 ELSE 0 END), 0),
            0
        ), 4
    ) AS taxa_vitorias_segundo,
    ROUND(
        COALESCE(
            SUM(CASE WHEN f.primeiro_a_atacar = 1 AND f.venceu = 1 THEN 1 ELSE 0 END)::NUMERIC / 
            NULLIF(SUM(CASE WHEN f.primeiro_a_atacar = 1 THEN 1 ELSE 0 END), 0),
            0
        ) - 
        COALESCE(
            SUM(CASE WHEN f.primeiro_a_atacar = 0 AND f.venceu = 1 THEN 1 ELSE 0 END)::NUMERIC / 
            NULLIF(SUM(CASE WHEN f.primeiro_a_atacar = 0 THEN 1 ELSE 0 END), 0),
            0
        ), 4
    ) AS diferencial_primeiro_ataque
FROM silver.fato_confronto f
JOIN silver.dim_pokemon p ON f.id_pokemon = p.id_pokemon
JOIN silver.dim_geracao g ON f.id_geracao_pokemon = g.id_geracao
GROUP BY g.nome_geracao, g.numero_geracao, p.categoria_raridade
ORDER BY g.numero_geracao, p.categoria_raridade;
